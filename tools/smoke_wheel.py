"""Install, reinstall/upgrade, test and uninstall a wheel in a fresh external venv."""
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile
import venv

from smoke_distribution import smoke


def test_wheel(wheel, version):
    with tempfile.TemporaryDirectory(prefix="mozhi-wheel-") as folder:
        environment = Path(folder) / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        binary_dir = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = binary_dir / ("python.exe" if sys.platform == "win32" else "python")
        executable = binary_dir / ("mozhi.exe" if sys.platform == "win32" else "mozhi")
        for options in ([], ["--upgrade", "--force-reinstall"]):
            subprocess.run([str(python), "-m", "pip", "install", "--no-deps", *options, str(wheel.resolve())], cwd=folder, check=True)
            smoke(executable, version, python_free=False)
        subprocess.run([str(python), "-m", "pip", "uninstall", "-y", "mozhi"], cwd=folder, check=True)
        assert not executable.exists(), "Console entry point survived uninstall"
    print("PASS wheel install, upgrade/reinstall, external execution and uninstall")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    test_wheel(args.wheel, args.version)
