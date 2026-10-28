import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import publish_release
import verify_pypi


class PublicationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        (self.folder / "releases").mkdir()
        (self.folder / "package-managers").mkdir()
        self.version = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]
        self.tag = "v" + self.version
        self.revision = "a" * 40
        self.names = [f"mozhi-{self.version}-windows-x64.zip", f"mozhi-{self.version}-py3-none-any.whl", f"mozhi-{self.version}.tar.gz"]
        receipts = []
        for name in self.names:
            (self.folder / "releases" / name).write_bytes(b"unit test fixture only")
            receipts.append(hashlib.sha256(b"unit test fixture only").hexdigest() + "  " + name)
        self.receipt = self.folder / "package-managers/SHA256SUMS"
        self.receipt.write_text("\n".join(receipts))
        self.manifest = {"version": self.version, "completePlatformSet": True,
                         "artifacts": {"windows-x64": {"filename": self.names[0], "sha256": receipts[0].split()[0]}}}
        (self.folder / "package-managers/release-manifest.json").write_text(json.dumps(self.manifest))
        self.run = {"conclusion": "success", "head_sha": self.revision,
                    "path": ".github/workflows/distributions.yml", "event": "push",
                    "repository": {"full_name": "sm1else-bot/mozhi"}}
        self.head = self.revision

    def command(self, arguments, **kwargs):
        if arguments[0] == "gh":
            return json.dumps(self.run)
        if arguments == ["git", "rev-parse", "HEAD"]:
            return self.head
        self.assertEqual(arguments, ["git", "rev-parse", "refs/tags/" + self.tag + "^{commit}"])
        return self.revision

    def validate(self, ancestor=True):
        with patch.object(publish_release.subprocess, "check_output", side_effect=self.command), \
             patch.object(publish_release.subprocess, "run", return_value=SimpleNamespace(returncode=0 if ancestor else 1)):
            return publish_release.validated_files(self.folder, self.tag, "123")

    def test_accepts_only_matching_successful_release_commit(self):
        self.assertEqual(len(self.validate()), 4)
        for key, value in [("head_sha", "b" * 40), ("conclusion", "failure"),
                           ("path", ".github/workflows/other.yml"), ("event", "pull_request"),
                           ("repository", {"full_name": "other/mozhi"})]:
            with self.subTest(key=key):
                previous = self.run[key]
                self.run[key] = value
                with self.assertRaisesRegex(SystemExit, "matching native"):
                    self.validate()
                self.run[key] = previous

    def test_rejects_unmerged_or_mismatched_checkout(self):
        with self.assertRaisesRegex(SystemExit, "merged into main"):
            self.validate(ancestor=False)
        self.head = "b" * 40
        with self.assertRaisesRegex(SystemExit, "Checkout"):
            self.validate()

    def test_rejects_missing_python_receipts_and_modified_upload(self):
        self.receipt.write_text(self.receipt.read_text().splitlines()[0])
        with self.assertRaisesRegex(SystemExit, "Python distribution missing"):
            self.validate()
        (self.folder / "releases" / self.names[0]).write_bytes(b"changed")
        with self.assertRaisesRegex(SystemExit, "Checksum mismatch"):
            self.validate()

    def test_rejects_public_registry_bytes_that_differ_from_approved_files(self):
        from io import BytesIO
        info = {"info": {"name": "mozhi", "version": self.version}, "urls": []}
        with patch.object(verify_pypi.urllib.request, "urlopen", return_value=BytesIO(json.dumps(info).encode())):
            with self.assertRaisesRegex(AssertionError, "approved distribution bytes"):
                verify_pypi.verify(self.version, self.folder / "releases")
