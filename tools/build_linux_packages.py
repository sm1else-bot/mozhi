"""Build and test a local Debian package; optionally build the prepared RPM spec."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

from prepare_release import checked_archives, VERSION
from smoke_distribution import smoke


def build(archives, metadata, output):
    artifact = checked_archives(archives, partial=True)["linux-x64"]["path"]
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mozhi-linux-package-") as folder:
        root = Path(folder)
        source = root / "source"
        source.mkdir()
        with tarfile.open(artifact) as archive:
            archive.extractall(source, filter="data")
        smoke(source / "mozhi", VERSION)
        stage = root / "debian"
        shutil.copytree(metadata / "linux/debian", stage)
        binary = stage / "usr/bin"
        binary.mkdir(parents=True)
        shutil.copy2(source / "mozhi", binary / "mozhi")
        license_ = stage / "usr/share/doc/mozhi"
        license_.mkdir(parents=True)
        shutil.copyfile(source / "LICENSE", license_ / "copyright")
        shutil.copytree(source / "LICENSES", license_ / "LICENSES")
        package = output / f"mozhi_{VERSION}_amd64.deb"
        subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(package)], check=True)
        extracted = root / "installed-deb"
        subprocess.run(["dpkg-deb", "-x", str(package), str(extracted)], check=True)
        smoke(extracted / "usr/bin/mozhi", VERSION)
        if shutil.which("rpmbuild"):
            rpm = root / "rpm"
            for name in ("BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"):
                (rpm / name).mkdir(parents=True)
            shutil.copyfile(artifact, rpm / "SOURCES" / artifact.name)
            subprocess.run(["rpmbuild", "-bb", "--define", f"_topdir {rpm}", str(metadata / "linux/mozhi.spec")], check=True)
            for result in (rpm / "RPMS").rglob("*.rpm"):
                shutil.copyfile(result, output / result.name)
        else:
            print("RPM spec prepared; rpmbuild is unavailable on this runner")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, default=Path("dist/releases"))
    parser.add_argument("--metadata", type=Path, default=Path("dist/package-managers"))
    parser.add_argument("--output", type=Path, default=Path("dist/linux-packages"))
    args = parser.parse_args()
    build(args.artifacts.resolve(), args.metadata.resolve(), args.output.resolve())
