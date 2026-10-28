import contextlib
import io
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mozhi import core
from mozhi._version import __version__


class StandaloneTests(unittest.TestCase):
    def cli(self, *args, stdin=None, cwd=None, timeout=5):
        return subprocess.run([sys.executable, str(ROOT / "src/mozhi.py"), *map(str, args)],
                              cwd=cwd, input=stdin, capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout)

    def test_version_help_and_usage_error(self):
        self.assertEqual(self.cli("--version").stdout.strip(), f"Mozhi {__version__}")
        self.assertIn("repl", self.cli("--help").stdout)
        self.assertEqual(self.cli("run").returncode, 2)

    def test_check_does_not_execute(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "sample.mozhi"
            file.write_text('ezhuthu("marker.txt", "bad")\n1 / 0 sollu\n')
            result = self.cli("check", file, cwd=folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(folder) / "marker.txt").exists())

    def test_utf8_bom_and_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "தமிழ் source.mozhi"
            file.write_text('"வணக்கம்" sollu\n', encoding="utf-8-sig")
            for args in [("run", file), (file,)]:
                result = self.cli(*args, cwd=folder)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "வணக்கம்\n")

    def test_errors_have_filename_line_and_stderr(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "bad.mozhi"
            for source in ['1 / 0 sollu\n', 'a = vechukko\n', '"missing\n']:
                file.write_text(source)
                result = self.cli("run", file)
                self.assertEqual(result.returncode, 1)
                self.assertIn(str(file), result.stderr)
                self.assertIn("Line 1", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.stdout, "")
        self.assertEqual(self.cli("run", "missing.mozhi").returncode, 1)

    def test_repl_persistence_blocks_and_recovery(self):
        source = 'n = 7 vechukko\nseiy double(x):\n    x * 2 thirumbu\nmudivu\ndouble(n)\n1 / 0 sollu\nn\na = vechukko\nn + 1\nquit\n'
        result = self.cli("repl", stdin=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("14", result.stdout)
        self.assertIn("8", result.stdout)
        self.assertIn("<repl>", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_repl_nested_blocks_and_eof(self):
        result = self.cli("repl", stdin='n = 0 vechukko\nn < 2 varaikum:\n    true na:\n        n = n + 1 vechukko\n    mudivu\nmudivu\nn\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2", result.stdout)
        self.assertEqual(self.cli("repl", stdin='seiy f():\n').returncode, 1)

    def test_file_io_and_strings(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.cli("run", ROOT / "examples/file_io.mozhi", cwd=folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((Path(folder) / "mozhi-example.txt").read_text(encoding="utf-8"), "வணக்கம்\nMozhi\n")
        result = self.cli("run", ROOT / "examples/standard_library.mozhi")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "vanakkam nanba\nMozhi romba nalla irukku\n9\n7\n")

    def test_new_examples(self):
        expected = {"hello_world": "Vanakkam, world!\n", "fibonacci": "55\n",
                    "arrays_loops": "20\n", "recursion": "720\n"}
        for name, output in expected.items():
            result = self.cli("run", ROOT / f"examples/{name}.mozhi")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, output)
        result = self.cli("run", ROOT / "examples/benchmark.mozhi")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("49995000\nSeconds: "))

    def test_no_browser_timeout_on_cli(self):
        start = time.monotonic()
        result = self.cli("run", ROOT / "examples/long_running.mozhi", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Mudinthathu\n")
        self.assertGreaterEqual(time.monotonic() - start, 10.5)

    @unittest.skipIf(sys.platform == "win32", "POSIX signal delivery; Windows console Ctrl+C is manual")
    def test_ctrl_c_exit_code(self):
        process = subprocess.Popen([sys.executable, str(ROOT / "src/mozhi.py"), "run", str(ROOT / "examples/long_running.mozhi")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            time.sleep(0.4)
            process.send_signal(signal.SIGINT)
            _, error = process.communicate(timeout=4)
            self.assertEqual(process.returncode, 130)
            self.assertIn(b"Stopped by user", error)
        finally:
            if process.poll() is None:
                process.kill()

    def test_builtin_errors_have_source_line(self):
        for source in ['padi("does-not-exist.mozhi")\n', 'seeratra(1)\n', 'pirithu(3, ",")\n']:
            with self.subTest(source=source):
                with self.assertRaises(core.MozhiError) as error:
                    core.run(source)
                self.assertEqual(error.exception.line, 1)


if __name__ == "__main__":
    unittest.main()
