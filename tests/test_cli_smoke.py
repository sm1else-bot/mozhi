"""Behavior checks for the current CLI snapshot; never checks out archival commits."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CliSmokeTests(unittest.TestCase):
    def run_source(self, source):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "sample.mozhi"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "src" / "mozhi.py"), str(path)],
                capture_output=True, text=True, timeout=3,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout

    def test_documented_hello(self):
        self.assertEqual(
            self.run_source((ROOT / "examples" / "hello.mozhi").read_text()),
            "Vanakkam, world!\nValue: 10\n",
        )

    def test_array_push_pop_and_index(self):
        self.assertEqual(self.run_source(
            "values = [10, 20] vechukko\n30 ullapodu values\n"
            "values veliyapodu\nvalues sollu\nvalues[1] sollu\n"
        ), "[10, 20]\n20\n")

    def test_function_and_conditional(self):
        self.assertEqual(self.run_source(
            "seiy double(x):\n    x * 2 thirumbu\nmudivu\n"
            "double(4) == 8 na:\n    \"correct\" sollu\n"
            "illana:\n    \"wrong\" sollu\nmudivu\n"
        ), "correct\n")


if __name__ == "__main__":
    unittest.main()
