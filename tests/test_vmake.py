"""Regression checks for paths, multi-file synthesis, cache invalidation and download gating."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('vmake', Path(__file__).resolve().parents[1] / 'vmake.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.configure_environment()

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vmake test space ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        _, self.config = v.load_config('blink')
        self.config.update(name='test', top='wrapper', sources=['wrapper.v', 'invert.v'])
        (self.root / 'config.json').write_text(json.dumps(self.config))
        (self.root / 'wrapper.v').write_text('module wrapper(input wire a, output wire y); invert u(.a(a),.y(y)); endmodule\n')
        (self.root / 'invert.v').write_text('module invert(input wire a, output wire y); assign y = ~a; endmodule\n')

    def test_real_multisource_synthesis_and_content_cache(self):
        p = v.Project(self.root, self.config)
        p.synth()
        output = p.artifact('.json')
        self.assertIn('wrapper', json.loads(output.read_text())['modules'])
        with patch.object(v, 'run', side_effect=AssertionError('unchanged synthesis should be cached')):
            v.Project(self.root, self.config).synth()
        source = self.root / 'invert.v'
        old = source.stat()
        source.write_text('module invert(input wire a, output wire y); assign y = a; endmodule\n')
        os.utime(source, ns=(old.st_atime_ns, old.st_mtime_ns))
        before = v.file_hash(output)
        with patch.object(v, 'run', wraps=v.run) as command:
            v.Project(self.root, self.config).synth()
            self.assertTrue(command.called)
        self.assertNotEqual(before, v.file_hash(output))
        changed = dict(self.config, part='xc7a35tcsg324-2')
        with patch.object(v, 'run', wraps=v.run) as command:
            v.Project(self.root, changed).synth()
            self.assertTrue(command.called, 'effective configuration override must invalidate cache')
        source.write_text('not valid verilog !')
        p.artifact('.bit').write_bytes(b'old downloadable result')
        with self.assertRaises(v.BuildError):
            v.Project(self.root, self.config).synth()
        self.assertFalse(output.exists())
        self.assertFalse(p.artifact('.bit').exists())

    def test_program_stops_before_hardware_on_simulation_failure(self):
        p = v.Project(self.root, self.config)
        with patch.object(p, 'require_hardware'), patch.object(p, 'sim', side_effect=v.BuildError('simulation failed')), patch.object(v, 'run') as command:
            with self.assertRaises(v.BuildError):
                p.program()
            command.assert_not_called()

    def test_program_requires_constraints(self):
        p = v.Project(self.root, dict(self.config, constraints=None))
        with patch.object(v, 'run') as command:
            with self.assertRaises(v.BuildError):
                p.program()
            command.assert_not_called()

    def test_wave_fails_if_testbench_does_not_create_vcd(self):
        (self.root / 'testbench.v').write_text('module testbench; initial begin #1; $finish; end endmodule\n')
        cfg = dict(self.config, testbench='testbench.v', sim_top='testbench', wave_file='build/test.vcd')
        p = v.Project(self.root, cfg)
        (p.build / 'test.vcd').write_text('old VCD that must not be opened')
        with self.assertRaisesRegex(v.BuildError, '未生成'):
            p.wave()
        self.assertFalse((p.build / 'test.vcd').exists())

    def test_clean_rejects_escaping_symlink(self):
        outside = self.root / 'outside'
        outside.mkdir()
        project = self.root / 'project'
        project.mkdir()
        (project / 'build').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(v.BuildError):
            v.Project(project, self.config)

if __name__ == '__main__':
    unittest.main()
