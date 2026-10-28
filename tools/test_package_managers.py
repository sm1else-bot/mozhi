"""Native CI installation tests; run only on disposable GitHub-hosted runners."""
import argparse
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def test_chocolatey(metadata):
    folder = metadata / "chocolatey"
    run(["choco", "pack", str(folder / "mozhi.nuspec"), "--output-directory", str(folder)])
    installed = False
    try:
        for verb, extra in [("install", []), ("upgrade", ["--force"])]:
            run(["choco", verb, "mozhi", "--version", VERSION, "--source", str(folder), "--yes", "--no-progress", *extra])
            installed = True
            executable = shutil.which("mozhi")
            assert executable, "Chocolatey shim was not installed"
            result = subprocess.check_output([executable, "--version"], text=True)
            assert result.strip() == f"Mozhi {VERSION}"
    finally:
        if installed:
            run(["choco", "uninstall", "mozhi", "--yes", "--no-progress"])
    assert shutil.which("mozhi") is None, "Chocolatey shim survived uninstall"


def test_brew(metadata, archives):
    formula = metadata / "homebrew-mozhi" / "Formula" / "mozhi.rb"
    original = "https://github.com/sm1else-bot/mozhi/releases/download/v" + VERSION
    with tempfile.TemporaryDirectory(prefix="mozhi-tap-") as folder:
        local = Path(folder) / "mozhi.rb"
        local.write_text(formula.read_text().replace(original, archives.resolve().as_uri()))
        installed = False
        try:
            run(["brew", "install", "--formula", str(local)])
            installed = True
            run(["brew", "test", "mozhi"])
            run(["brew", "reinstall", "--formula", str(local)])
            run(["brew", "test", "mozhi"])
        finally:
            if installed:
                run(["brew", "uninstall", "mozhi"])
        assert shutil.which("mozhi") is None, "Homebrew binary survived uninstall"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=ROOT / "dist/package-managers")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "dist/releases")
    parser.add_argument("--disposable-runner", action="store_true", required=True)
    args = parser.parse_args()
    if platform.system() == "Windows":
        test_chocolatey(args.metadata.resolve())
    elif platform.system() == "Darwin":
        test_brew(args.metadata.resolve(), args.artifacts.resolve())
    else:
        raise SystemExit("Use build_linux_packages.py for Linux packaging checks")
