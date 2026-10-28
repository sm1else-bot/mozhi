"""Install, reinstall, execute and uninstall a wheel or sdist in an external venv."""
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
            index = ["--no-index"] if wheel.name.endswith(".whl") else ["--index-url", "https://pypi.org/simple"]
            subprocess.run([str(python), "-m", "pip", "--isolated", "install", "--no-deps", *index, *options, str(wheel.resolve())], cwd=folder, check=True)
            smoke(executable, version, python_free=False)
        subprocess.run([str(python), "-m", "pip", "uninstall", "-y", "mozhi"], cwd=folder, check=True)
        assert not executable.exists(), "Console entry point survived uninstall"
        result = subprocess.run([str(python), "-I", "-c", "import mozhi"], cwd=folder, capture_output=True)
        assert result.returncode != 0, "Mozhi package survived uninstall"
    print(f"PASS {wheel.name}: install, reinstall, external execution and uninstall")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    test_wheel(args.wheel, args.version)
