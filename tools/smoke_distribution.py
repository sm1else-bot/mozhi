"""Test a CLI outside the checkout with Python-related environment paths removed."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def smoke(executable, version, python_free=True):
    executable = str(Path(executable).resolve())
    environment = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX"):
        environment.pop(key, None)
    if python_free:
        environment["PATH"] = str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32") if os.name == "nt" else "/usr/bin:/bin"
    with tempfile.TemporaryDirectory(prefix="mozhi-distribution-") as directory:
        cwd = Path(directory)
        if python_free:
            empty_path = cwd / "empty-path"
            empty_path.mkdir()
            environment["PATH"] = str(empty_path)

        def invoke(arguments, expected=0, stdin=None):
            result = subprocess.run([executable, *arguments], cwd=cwd, env=environment,
                                    input=stdin, text=True, encoding="utf-8", capture_output=True, timeout=40)
            if result.returncode != expected:
                raise AssertionError((arguments, result.returncode, result.stdout, result.stderr))
            return result

        assert invoke(["--version"]).stdout.strip() == f"Mozhi {version}"
        invoke(["--help"])
        source = cwd / "Tamil source.mozhi"
        source.write_text('"வணக்கம்!" sollu\n', encoding="utf-8")
        assert invoke(["run", str(source)]).stdout == "வணக்கம்!\n"
        assert invoke([source.name]).stdout == "வணக்கம்!\n"
        assert "syntax OK" in invoke(["check", str(source)]).stdout
        source.write_text('ezhuthu("should-not-exist.txt", "no")\n1 / 0 sollu\n', encoding="utf-8")
        invoke(["check", str(source)])
        assert not (cwd / "should-not-exist.txt").exists(), "check executed the program"
        source.write_text('a = vechukko\n', encoding="utf-8")
        assert "Line" in invoke(["check", str(source)], expected=1).stderr
        source.write_text('1 / 0 sollu\n', encoding="utf-8")
        assert source.name in invoke(["run", str(source)], expected=1).stderr
        invoke(["run", "missing.mozhi"], expected=1)
        result = invoke(["repl"], stdin='n = 7 vechukko\nseiy double(x):\n    x * 2 thirumbu\nmudivu\ndouble(n)\n1 / 0 sollu\nn\nquit\n')
        assert "14" in result.stdout and "7" in result.stdout
        assert "Line" in result.stderr and "Traceback" not in result.stderr
        nested = invoke(["repl"], stdin='n = 0 vechukko\nn < 2 varaikum:\n    true na:\n        n = n + 1 vechukko\n    mudivu\nmudivu\nn\nquit\n')
        assert "2" in nested.stdout and not nested.stderr
    print(f"PASS external-directory CLI smoke: {executable}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    smoke(args.executable, args.version)
