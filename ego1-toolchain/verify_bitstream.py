#!/usr/bin/env python3
"""Verify the generated .bit decodes to the input frames, excluding frame ECC."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('build_dir', type=Path)
build = parser.parse_args().build_dir.resolve()
with (build / 'bitread.log').open('w') as log:
    subprocess.run([str(root / 'bin/bitread'), '--part_file',
                    str(root / 'src/prjxray-db/artix7/xc7a35tcsg324-1/part.yaml'),
                    '-o', str(build / 'decoded.frames'), str(build / 'top.bit')],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
expected = {int(addr, 16): [int(w, 16) for w in data.split(',')]
            for addr, data in (line.split() for line in (build / 'top.frames').read_text().splitlines() if line.strip())}
actual = {}
for chunk in (build / 'decoded.frames').read_text().split('.frame ')[1:]:
    addr, *words = chunk.split()
    actual[int(addr, 16)] = [int(w, 16) for w in words]
if expected.keys() - actual.keys():
    raise SystemExit('FAIL: missing frames')
for addr, words in expected.items():
    words[50] &= 0xffffe000  # bitread masks these frame ECC bits by default.
    if actual[addr] != words:
        raise SystemExit(f'FAIL: mismatched frame {addr:#x}')
extra = actual.keys() - expected.keys()
if any(any(actual[addr]) for addr in extra):
    raise SystemExit('FAIL: nonzero unexpected padding frames')
result = {
    'status': 'PASS', 'part': 'xc7a35tcsg324-1',
    'input_frames': len(expected), 'decoded_frames': len(actual), 'zero_padding_frames': len(extra),
    'comparison': 'All input frames match, excluding 13 ECC bits in word 50; all added frames are zero.',
    'bitstream_bytes': (build / 'top.bit').stat().st_size,
    'bitstream_sha256': hashlib.sha256((build / 'top.bit').read_bytes()).hexdigest(),
    'scope': 'Software bitstream verification only; does not verify physical hardware behavior.'
}
(build / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
