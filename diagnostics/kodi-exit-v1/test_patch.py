import contextlib
import io
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT.parents[1] / 'validation-deps'))
import javalang

class PatchTests(unittest.TestCase):
    def fixture(self, folder):
        p = Path(folder)
        main = p / 'tools/android/packaging/xbmc/src/Main.java.in'
        main.parent.mkdir(parents=True)
        main.write_text((ROOT / 'upstream-Main.java.in').read_text())
        (p / 'version.txt').write_text((ROOT / 'upstream-version.txt').read_text())
        return p, main

    def run_patch(self, p, revision='e513e0ff4331fc25fd2454659a9dd3e6b7670146'):
        with patch('sys.argv', ['apply.py', str(p)]), patch('subprocess.check_output', return_value=revision), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(ROOT / 'apply.py'), run_name='__main__')

    def test_actual_pinned_template_produces_parseable_separate_app(self):
        with tempfile.TemporaryDirectory() as folder:
            p, main = self.fixture(folder)
            self.run_patch(p)
            source = main.read_text().replace('@APP_PACKAGE@', 'com.stormtracker.kodidiagnostic').replace('@APP_NAME@', 'KodiZidooDiagnostic').replace('@APP_NAME_LC@', 'kodizidoodiagnostic')
            tree = javalang.parse.parse(source)
            methods = {m.name for m in tree.types[0].methods}
            self.assertIn('readOwnProcessExitHistory', methods)
            self.assertIn('onStop', methods)
            self.assertIn('APP_PACKAGE com.stormtracker.kodidiagnostic', (p/'version.txt').read_text())
            with self.assertRaises(SystemExit):
                self.run_patch(p)  # Never silently apply twice.

    def test_wrong_revision_refused_without_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            p, main = self.fixture(folder)
            before = main.read_bytes()
            with self.assertRaises(SystemExit):
                self.run_patch(p, 'wrong')
            self.assertEqual(main.read_bytes(), before)

    def test_modified_source_refused_without_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            p, main = self.fixture(folder)
            main.write_text(main.read_text() + '\n// modified\n')
            before = main.read_bytes()
            with self.assertRaises(SystemExit):
                self.run_patch(p)
            self.assertEqual(main.read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
