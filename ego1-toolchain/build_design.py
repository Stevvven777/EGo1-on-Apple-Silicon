#!/usr/bin/env python3
"""Build a Verilog design for EGO1 with the locally validated toolchain."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PART = "xc7a35tcsg324-1"
p = argparse.ArgumentParser(description="EGO1: Verilog → JSON → FASM → frames → .bit")
p.add_argument("--top", default="top", help="RTL top module (default: top)")
p.add_argument("--xdc", required=True, type=Path, help="EGO1 pin constraints")
p.add_argument("--out", default=Path("build"), type=Path, help="Output directory")
p.add_argument("--freq", default=100.0, type=float, help="Timing target in MHz")
p.add_argument("rtl", nargs="+", type=Path, help="Synthesizable Verilog/SystemVerilog only")
a = p.parse_args()
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", a.top):
    p.error("Use a plain Verilog module identifier for --top")
if a.freq <= 0:
    p.error("--freq must be positive")
for f in [a.xdc, *a.rtl]:
    if not f.is_file():
        p.error(f"File does not exist: {f}")
a.out = a.out.resolve()
a.out.mkdir(parents=True, exist_ok=True)
# Never leave an old successful bitstream looking like the result of a failed run.
(a.out / "top.bit").unlink(missing_ok=True)
env = os.environ.copy()
env["PATH"] = str(ROOT / "bin") + ":/opt/homebrew/bin:" + env.get("PATH", "")

def run(label, args):
    print(f"[{label}]", flush=True)
    log = a.out / (label + ".log")
    with log.open("w") as stream:
        r = subprocess.run([str(x) for x in args], cwd=a.out, env=env,
                           stdout=stream, stderr=subprocess.STDOUT)
    if r.returncode:
        print(log.read_text(errors="replace")[-7000:], file=sys.stderr)
        raise SystemExit(f"FAILED: {label}. Full log: {log}")

def quote(path):
    return '"' + str(path.resolve()).replace('\\', '\\\\').replace('"', '\\"') + '"'

run("lint", ["verilator", "--lint-only", "-Wall", "--top-module", a.top,
             *[f.resolve() for f in a.rtl]])
# A short temporary synthesis directory also avoids spaces in ABC's internal paths.
with tempfile.TemporaryDirectory(prefix="ego1-synth-") as tmp:
    ys = Path(tmp) / "synth.ys"
    ys.write_text("read_verilog -sv " + " ".join(quote(f) for f in a.rtl) +
                  f"\nsynth_xilinx -family xc7 -top {a.top}\ncheck -assert\n" +
                  "write_json top.json\n")
    run("synthesis", ["yosys", "-Q", "-T", "-s", ys])
run("nextpnr", [ROOT / "bin/nextpnr-himbaechel", "--device", PART,
                 "--freq", str(a.freq), "--json", "top.json",
                 "-o", "xdc=" + str(a.xdc.resolve()), "-o", "fasm=top.fasm"])
db = ROOT / "src/prjxray-db/artix7"
run("fasm2frames", [ROOT / "bin/fasm2frames", "--db-root", db, "--part", PART,
                    "top.fasm", "top.frames"])
run("bitstream", [ROOT / "bin/xc7frames2bit", "--part_file", db / PART / "part.yaml",
                  "--part_name", PART, "--frm_file", "top.frames", "--output_file", "top.bit"])
bit = a.out / "top.bit"
if bit.stat().st_size < 1024 or bytes.fromhex("aa995566") not in bit.read_bytes():
    bit.unlink(missing_ok=True)
    raise SystemExit("Invalid bitstream: missing configuration sync word or unexpected size")
print(f"SUCCESS: {bit} ({bit.stat().st_size:,} bytes)")
