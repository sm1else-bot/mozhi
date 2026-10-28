"""After approved publication, verify PyPI hashes and a real registry installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import venv

from smoke_distribution import smoke


def verify(version, artifacts, attempts=1):
    names = (f"mozhi-{version}-py3-none-any.whl", f"mozhi-{version}.tar.gz")
    expected = {name: hashlib.sha256((artifacts / name).read_bytes()).hexdigest() for name in names}
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(f"https://pypi.org/pypi/mozhi/{version}/json", timeout=30) as response:
                info = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code != 404 or attempt + 1 == attempts:
                raise
            time.sleep(10)
    assert info["info"]["name"] == "mozhi" and info["info"]["version"] == version
    actual = {file["filename"]: file["digests"]["sha256"] for file in info["urls"]}
    assert actual == expected, "Public PyPI files differ from the approved distribution bytes"
    with tempfile.TemporaryDirectory(prefix="mozhi-public-pypi-") as directory:
        folder = Path(directory)
        environment = folder / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        binaries = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        executable = binaries / ("mozhi.exe" if os.name == "nt" else "mozhi")
        subprocess.run([str(python), "-m", "pip", "--isolated", "install", "--index-url",
                        "https://pypi.org/simple", "--no-cache-dir", "--no-deps", f"mozhi=={version}"],
                       cwd=folder, check=True)
        smoke(executable, version, python_free=False)
        subprocess.run([str(python), "-m", "pip", "uninstall", "-y", "mozhi"], cwd=folder, check=True)
        assert not executable.exists(), "Public installation's console script survived uninstall"
    print(f"PASS public PyPI mozhi=={version}: approved hashes, install, run, REPL, check and uninstall")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=1)
    args = parser.parse_args()
    if args.attempts < 1 or args.attempts > 12:
        parser.error("attempts must be between 1 and 12")
    verify(args.version, args.artifacts.resolve(), args.attempts)
