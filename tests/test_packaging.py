import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
AVAILABLE = importlib.util.find_spec("jsonschema") and importlib.util.find_spec("yaml")
if AVAILABLE:
    import prepare_release as release


@unittest.skipUnless(AVAILABLE, "Install requirements-build.txt for distribution tests")
class PackagingTests(unittest.TestCase):
    def fixture(self, folder, target):
        # Unit-test archive mattum; idhai release seiya koodathu.
        metadata = {"version": release.VERSION, "platform": target, "smokeTested": True}
        for module in ("core", "cli"):
            metadata[module + "Sha256"] = hashlib.sha256((ROOT / f"src/mozhi/{module}.py").read_bytes()).hexdigest()
        files = {"build-info.json": json.dumps(metadata).encode(), "LICENSE": b"test-fixture", "LICENSES/Python.txt": b"test-fixture", "LICENSES/PyInstaller.txt": b"test-fixture"}
        files["mozhi.exe" if target.startswith("windows") else "mozhi"] = b"UNIT TEST FIXTURE - NOT AN EXECUTABLE"
        file = folder / release.expected_filename(target)
        if target.startswith("windows"):
            with zipfile.ZipFile(file, "w") as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
        else:
            with tarfile.open(file, "w:gz") as archive:
                for name, data in files.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        file.with_name(file.name + ".sha256").write_text(f"{digest}  {file.name}\n")
        return file

    def test_complete_set_generates_valid_manager_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for target in release.TARGETS:
                self.fixture(folder, target)
            package_files = {f"mozhi/{name}.py": (ROOT / f"src/mozhi/{name}.py").read_bytes() for name in ("core", "cli", "_version", "__init__", "__main__")}
            metadata = f"Metadata-Version: 2.4\nName: mozhi\nVersion: {release.VERSION}\n".encode()
            with zipfile.ZipFile(folder / f"mozhi-{release.VERSION}-py3-none-any.whl", "w") as archive:
                for name, contents in package_files.items():
                    archive.writestr(name, contents)
                archive.writestr(f"mozhi-{release.VERSION}.dist-info/METADATA", metadata)
            with tarfile.open(folder / f"mozhi-{release.VERSION}.tar.gz", "w:gz") as archive:
                sources = {f"mozhi-{release.VERSION}/src/{name}": data for name, data in package_files.items()}
                sources[f"mozhi-{release.VERSION}/PKG-INFO"] = metadata
                for name, contents in sources.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(contents)
                    archive.addfile(member, io.BytesIO(contents))
            output = folder / "prepared"
            release.prepare(folder, output)
            manifest = json.loads((output / "release-manifest.json").read_text())
            self.assertTrue(manifest["completePlatformSet"])
            self.assertEqual(manifest["publicationStatus"], "prepared-only-not-published")
            self.assertEqual(manifest["wingetIdentifier"], "jessenth.Mozhi")
            formula = output / "homebrew-mozhi/Formula/mozhi.rb"
            if shutil.which("ruby"):
                subprocess.run(["ruby", "-c", str(formula)], check=True, capture_output=True)
            self.assertEqual(len((output / "SHA256SUMS").read_text().splitlines()), 6)
            self.assertTrue((output / "chocolatey/mozhi.nuspec").is_file())
            self.assertTrue((output / "linux/PKGBUILD").is_file())

    def test_missing_platform_is_not_publishable(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.fixture(folder, "windows-x64")
            with self.assertRaises(ValueError):
                release.prepare(folder, folder / "out")
            release.prepare(folder, folder / "partial", partial=True)
            self.assertFalse(json.loads((folder / "partial/release-manifest.json").read_text())["completePlatformSet"])

    def test_tampered_archive_and_stale_source_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            file = self.fixture(folder, "windows-x64")
            file.with_name(file.name + ".sha256").write_text("0" * 64 + "  " + file.name)
            with self.assertRaisesRegex(ValueError, "Checksum"):
                release.checked_archives(folder, partial=True)
            self.fixture(folder, "windows-x64")
            with zipfile.ZipFile(file) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}
            metadata = json.loads(files["build-info.json"])
            metadata["coreSha256"] = "0" * 64
            files["build-info.json"] = json.dumps(metadata).encode()
            with zipfile.ZipFile(file, "w") as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(ValueError, "different core source"):
                release.checked_archives(folder, partial=True)

    def test_publishing_requires_explicit_approval(self):
        from publish_release import publish
        with self.assertRaisesRegex(SystemExit, "approval"):
            publish(Path("does-not-exist"), "v" + release.VERSION, "0")


class HistoricalPreservationTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / ".git").exists() and shutil.which("git"), "Archival verification requires the Git checkout")
    def test_archival_snapshot_hashes_and_trees(self):
        data = json.loads((ROOT / "evidence/snapshots.json").read_text())
        for commit in data["archivalCommits"]:
            tree = subprocess.check_output(["git", "rev-parse", commit["commit"] + "^{tree}"], cwd=ROOT, text=True).strip()
            self.assertEqual(tree, commit["tree"])
            for file in commit["files"]:
                contents = subprocess.check_output(["git", "show", commit["commit"] + ":" + file["path"]], cwd=ROOT)
                self.assertEqual(hashlib.sha256(contents).hexdigest(), file["sha256"])
