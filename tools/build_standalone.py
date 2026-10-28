"""Build and smoke-test one native executable, then produce a versioned archive."""
import argparse
import gzip
import hashlib
import json
import importlib.metadata
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import tarfile
import zipfile
import urllib.request

from smoke_distribution import smoke

ROOT = Path(__file__).resolve().parents[1]
VERSION = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]


def platform_id():
    system, machine = platform.system(), platform.machine().lower()
    values = {("Windows", "amd64"): "windows-x64", ("Windows", "x86_64"): "windows-x64",
              ("Darwin", "arm64"): "macos-arm64", ("Darwin", "x86_64"): "macos-x64",
              ("Linux", "x86_64"): "linux-x64"}
    if (system, machine) not in values:
        raise SystemExit(f"Unsupported native build target: {system} {machine}")
    return values[system, machine]


def build(output):
    target = platform_id()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    work = ROOT / "build"
    work.mkdir(exist_ok=True)
    if os.name == "nt":
        numbers = ", ".join(VERSION.split(".") + ["0"])
        text = f'''VSVersionInfo(ffi=FixedFileInfo(filevers=({numbers}), prodvers=({numbers}), mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0', [StringStruct('CompanyName','Jessenth Ebenezer'), StringStruct('FileDescription','Mozhi interpreted programming language'), StringStruct('FileVersion','{VERSION}'), StringStruct('ProductName','Mozhi'), StringStruct('ProductVersion','{VERSION}'), StringStruct('OriginalFilename','mozhi.exe')])]), VarFileInfo([VarStruct('Translation',[1033,1200])])])'''
        (work / "windows-version.txt").write_text(text, encoding="utf-8")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm",
                    "--distpath", str(work / "standalone"), "--workpath", str(work / "pyinstaller"),
                    str(ROOT / "packaging/mozhi.spec")], cwd=ROOT, check=True)
    executable = work / "standalone" / ("mozhi.exe" if os.name == "nt" else "mozhi")
    smoke(executable, VERSION)
    stage = work / f"stage-{target}"
    stage.mkdir(exist_ok=True)
    shutil.copyfile(executable, stage / executable.name)
    (stage / executable.name).chmod(0o755)
    shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE")
    licenses = stage / "LICENSES"
    licenses.mkdir(exist_ok=True)
    installed_license = next((path for path in [Path(sys.base_prefix) / "LICENSE.txt", Path(sys.base_prefix) / "LICENSE"] if path.is_file()), None)
    python_license = installed_license.read_bytes() if installed_license else urllib.request.urlopen(
        f"https://raw.githubusercontent.com/python/cpython/v{platform.python_version()}/LICENSE", timeout=30).read()
    (licenses / "Python.txt").write_bytes(python_license)
    distribution = importlib.metadata.distribution("pyinstaller")
    copying = next(path for path in distribution.files if str(path).endswith("COPYING.txt"))
    (licenses / "PyInstaller.txt").write_bytes(distribution.locate_file(copying).read_bytes())
    metadata = {"version": VERSION, "platform": target, "python": platform.python_version(),
                "bundler": __import__("PyInstaller").__version__, "smokeTested": True,
                "signing": "not-certified-by-this-build-script",
                "coreSha256": hashlib.sha256((ROOT / "src/mozhi/core.py").read_bytes()).hexdigest(),
                "cliSha256": hashlib.sha256((ROOT / "src/mozhi/cli.py").read_bytes()).hexdigest()}
    (stage / "build-info.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    name = f"mozhi-{VERSION}-{target}"
    if os.name == "nt":
        artifact = output / f"{name}.zip"
        with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(path for path in stage.rglob("*") if path.is_file()):
                entry = zipfile.ZipInfo(item.relative_to(stage).as_posix(), (2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, item.read_bytes())
    else:
        artifact = output / f"{name}.tar.gz"
        with artifact.open("wb") as stream, gzip.GzipFile(fileobj=stream, mode="wb", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as archive:
                for item in sorted(path for path in stage.rglob("*") if path.is_file()):
                    info = archive.gettarinfo(str(item), item.relative_to(stage).as_posix())
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ""
                    with item.open("rb") as data:
                        archive.addfile(info, data)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (output / (artifact.name + ".sha256")).write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")
    print(artifact)
    return artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist/releases")
    build(parser.parse_args().output_dir)
