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
    run = json.loads(subprocess.check_output(["gh", "run", "view", str(run_id), "--json", "conclusion,headSha,workflowName"], text=True))
    revision = subprocess.check_output(["git", "rev-parse", tag + "^{commit}"], text=True).strip()
    if run["conclusion"] != "success" or run["headSha"] != revision or run["workflowName"] != "Build and validate Mozhi distributions":
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
        if folder / "releases" / artifact["filename"] not in files:
            raise SystemExit("Native artifact missing from checksums")
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
