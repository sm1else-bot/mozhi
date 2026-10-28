"""Verify archive integrity and the extracted executable, not only the build tree."""
import argparse
from pathlib import Path
import tarfile
import tempfile
import zipfile

from prepare_release import checked_archives, VERSION
from smoke_distribution import smoke


def verify(folder):
    for target, artifact in checked_archives(folder, partial=True).items():
        with tempfile.TemporaryDirectory(prefix="mozhi-extracted-") as directory:
            if target.startswith("windows"):
                with zipfile.ZipFile(artifact["path"]) as archive:
                    if set(archive.namelist()) != {"mozhi.exe", "LICENSE", "build-info.json", "LICENSES/Python.txt", "LICENSES/PyInstaller.txt"}:
                        raise ValueError("Unexpected archive members")
                    archive.extractall(directory)
                executable = Path(directory) / "mozhi.exe"
            else:
                with tarfile.open(artifact["path"]) as archive:
                    if set(archive.getnames()) != {"mozhi", "LICENSE", "build-info.json", "LICENSES/Python.txt", "LICENSES/PyInstaller.txt"}:
                        raise ValueError("Unexpected archive members")
                    archive.extractall(directory, filter="data")
                executable = Path(directory) / "mozhi"
            smoke(executable, VERSION)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    verify(parser.parse_args().folder.resolve())
