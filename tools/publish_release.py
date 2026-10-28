"""Explicitly approved publishing only; preparation workflows do not invoke this."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def validated_files(folder, tag, run_id):
    version = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag) or tag != "v" + version:
        raise SystemExit("Tag does not match the canonical release version")
    info = json.loads((folder / "package-managers/release-manifest.json").read_text())
    if not info.get("completePlatformSet") or info["version"] != version:
        raise SystemExit("Refusing incomplete release set")
    if not str(run_id).isdigit():
        raise SystemExit("Build run ID must be numeric")
    run = json.loads(subprocess.check_output(["gh", "api", f"repos/sm1else-bot/mozhi/actions/runs/{run_id}"], text=True))
    revision = subprocess.check_output(["git", "rev-parse", "refs/tags/" + tag + "^{commit}"], text=True).strip()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != revision:
        raise SystemExit("Checkout does not match the release tag")
    if subprocess.run(["git", "merge-base", "--is-ancestor", revision, "origin/main"], capture_output=True).returncode:
        raise SystemExit("Release commit must be merged into main")
    if (run.get("conclusion") != "success" or run.get("head_sha") != revision
            or run.get("path") != ".github/workflows/distributions.yml"
            or run.get("repository", {}).get("full_name") != "sm1else-bot/mozhi"
            or run.get("event") not in {"push", "workflow_dispatch"}):
        raise SystemExit("Build run is not a successful matching native distribution workflow")
    files = []
    receipts = (folder / "package-managers/SHA256SUMS").read_text().splitlines()
    for line in receipts:
        digest, name = line.split()
        if Path(name).name != name:
            raise SystemExit("Invalid artifact filename")
        file = folder / "releases" / name
        if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Checksum mismatch: {name}")
        files.append(file)
    for artifact in info["artifacts"].values():
        file = folder / "releases" / artifact["filename"]
        if file not in files or hashlib.sha256(file.read_bytes()).hexdigest() != artifact["sha256"]:
            raise SystemExit("Native artifact missing from checksums or manifest digest differs")
    for name in (f"mozhi-{version}.tar.gz", f"mozhi-{version}-py3-none-any.whl"):
        if folder / "releases" / name not in files:
            raise SystemExit("Python distribution missing from checksums")
    files.append(folder / "package-managers/SHA256SUMS")
    return files


def publish(folder, tag, run_id, approved=False):
    if not approved:
        raise SystemExit("Explicit release approval is required")
    files = validated_files(folder, tag, run_id)
    version = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]
    subprocess.run(["gh", "release", "create", tag, "--verify-tag", "--title", "Mozhi " + version,
                    "--notes-file", str(folder / "package-managers/RELEASE_NOTES.md"), *map(str, files)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        validated_files(args.directory.resolve(), args.tag, args.run_id)
    else:
        publish(args.directory.resolve(), args.tag, args.run_id, args.approved)
