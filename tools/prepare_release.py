"""Prepare checksums and package-manager files from real, tested release archives.

This tool never uploads, creates a GitHub Release, or submits registry packages.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import tarfile
import zipfile
from email.parser import BytesParser
from xml.sax.saxutils import escape

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = runpy.run_path(str(ROOT / "src/mozhi/_version.py"))["__version__"]
OWNER = "sm1else-bot"
REPO = f"https://github.com/{OWNER}/mozhi"
IDENTIFIER = "jessenth.Mozhi"
TARGETS = ("windows-x64", "macos-arm64", "macos-x64", "linux-x64")


def expected_filename(target):
    return f"mozhi-{VERSION}-{target}." + ("zip" if target.startswith("windows") else "tar.gz")

def checked_python(folder, required=False):
    wheel = folder / f"mozhi-{VERSION}-py3-none-any.whl"
    source = folder / f"mozhi-{VERSION}.tar.gz"
    for file in (wheel, source):
        if not file.is_file():
            if required:
                raise ValueError(f"Missing Python distribution: {file.name}")
            return []
    with zipfile.ZipFile(wheel) as archive:
        metadata = BytesParser().parsebytes(archive.read(f"mozhi-{VERSION}.dist-info/METADATA"))
        if metadata["Name"] != "mozhi" or metadata["Version"] != VERSION:
            raise ValueError("Wheel metadata version/name mismatch")
        for module in ("core", "cli", "_version", "__init__", "__main__"):
            if archive.read(f"mozhi/{module}.py") != (ROOT / f"src/mozhi/{module}.py").read_bytes():
                raise ValueError("Wheel contains stale interpreter/package source")
    with tarfile.open(source) as archive:
        metadata = BytesParser().parsebytes(archive.extractfile(f"mozhi-{VERSION}/PKG-INFO").read())
        if metadata["Name"] != "mozhi" or metadata["Version"] != VERSION:
            raise ValueError("Source distribution version/name mismatch")
        for module in ("core", "cli", "_version", "__init__", "__main__"):
            if archive.extractfile(f"mozhi-{VERSION}/src/mozhi/{module}.py").read() != (ROOT / f"src/mozhi/{module}.py").read_bytes():
                raise ValueError("Source distribution contains stale interpreter/package source")
    return [wheel.name, source.name]


def checked_archives(folder, partial=False):
    archives = {}
    for target in TARGETS:
        file = folder / expected_filename(target)
        if not file.is_file():
            if partial:
                continue
            raise ValueError(f"Missing native artifact: {file.name}")
        if file.suffix == ".zip":
            with zipfile.ZipFile(file) as archive:
                metadata = json.loads(archive.read("build-info.json"))
                assert "mozhi.exe" in archive.namelist()
        else:
            with tarfile.open(file) as archive:
                metadata = json.load(archive.extractfile("build-info.json"))
                assert "mozhi" in archive.getnames()
        if metadata.get("version") != VERSION or metadata.get("platform") != target or metadata.get("smokeTested") is not True:
            raise ValueError(f"Artifact lacks matching native smoke-test evidence: {file.name}")
        for module in ("core", "cli"):
            source_digest = hashlib.sha256((ROOT / f"src/mozhi/{module}.py").read_bytes()).hexdigest()
            if metadata.get(module + "Sha256") != source_digest:
                raise ValueError(f"Artifact was built from different {module} source: {file.name}")
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        receipt = file.with_name(file.name + ".sha256")
        if not receipt.is_file() or receipt.read_text().split() != [digest, file.name]:
            raise ValueError(f"Checksum receipt does not match {file.name}")
        archives[target] = {"path": file, "sha256": digest, "metadata": metadata}
    if not archives:
        raise ValueError("No tested archives found")
    return archives


def homebrew(archives, base):
    lines = ["class Mozhi < Formula", '  desc "Tamil-inspired, verb-final interpreted programming language"',
             f'  homepage "{REPO}"', f'  version "{VERSION}"', '  license "MIT"']
    for os_, entries in [("macos", [("arm64", "arm"), ("x64", "intel")]), ("linux", [("x64", "intel")])]:
        available = [(cpu, ruby_cpu) for cpu, ruby_cpu in entries if f"{os_}-{cpu}" in archives]
        if available:
            lines.append(f"  on_{os_} do")
            for cpu, ruby_cpu in available:
                artifact = archives[f"{os_}-{cpu}"]
                lines += [f"    on_{ruby_cpu} do", f'      url "{base}/{artifact["path"].name}"',
                          f'      sha256 "{artifact["sha256"]}"', "    end"]
            lines.append("  end")
    lines += ['  def install', '    bin.install "mozhi"', '    pkgshare.install "LICENSE", "LICENSES", "build-info.json"', '  end', '  test do',
              '    assert_match "Mozhi #{version}", shell_output("#{bin}/mozhi --version")',
              '    (testpath/"hello.mozhi").write("\\\"Vanakkam!\\\" sollu\\n")',
              '    assert_equal "Vanakkam!\\n", shell_output("#{bin}/mozhi run #{testpath}/hello.mozhi")',
              '    assert_match "syntax OK", shell_output("#{bin}/mozhi check #{testpath}/hello.mozhi")',
              '    assert_match "6", pipe_output("#{bin}/mozhi repl", "n = 6 vechukko\\nn\\nquit\\n", 0)',
              '  end', 'end', '']
    return "\n".join(lines)


def winget(artifact, base, output):
    common = {"PackageIdentifier": IDENTIFIER, "PackageVersion": VERSION}
    documents = {
        "version": {**common, "DefaultLocale": "en-US", "ManifestType": "version", "ManifestVersion": "1.10.0"},
        "defaultLocale": {**common, "PackageLocale": "en-US", "Publisher": "Jessenth Ebenezer",
                          "PublisherUrl": "https://jessenth.com", "PackageName": "Mozhi", "License": "MIT",
                          "LicenseUrl": f"{REPO}/blob/v{VERSION}/LICENSE", "PackageUrl": REPO,
                          "ShortDescription": "Tamil-inspired, verb-final interpreted programming language",
                          "Description": "Mozhi CLI with a bundled Python runtime. Run, check, and interactively evaluate .mozhi programs.",
                          "Tags": ["language", "interpreter", "tamil", "tanglish"],
                          "ManifestType": "defaultLocale", "ManifestVersion": "1.10.0"},
        "installer": {**common, "InstallerType": "zip", "NestedInstallerType": "portable",
                      "NestedInstallerFiles": [{"RelativeFilePath": "mozhi.exe", "PortableCommandAlias": "mozhi"}],
                      "UpgradeBehavior": "install", "Commands": ["mozhi"],
                      "Installers": [{"Architecture": "x64", "InstallerUrl": f"{base}/{artifact['path'].name}",
                                      "InstallerSha256": artifact["sha256"].upper()}],
                      "ManifestType": "installer", "ManifestVersion": "1.10.0"},
    }
    folder = output / "winget" / "manifests" / "j" / "jessenth" / "Mozhi" / VERSION
    folder.mkdir(parents=True, exist_ok=True)
    names = {"version": f"{IDENTIFIER}.yaml", "installer": f"{IDENTIFIER}.installer.yaml", "defaultLocale": f"{IDENTIFIER}.locale.en-US.yaml"}
    for kind, document in documents.items():
        schema = json.loads((ROOT / f"packaging/schemas/{kind}.schema.json").read_text(encoding="utf-8-sig"))
        jsonschema.validate(document, schema)
        header = f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.{kind}.1.10.0.schema.json\n"
        (folder / names[kind]).write_text(header + yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")


def chocolatey(artifact, base, output):
    folder = output / "chocolatey"
    tools = folder / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    # Official archive is embedded so moderation/install tests do not need an unpublished URL.
    import shutil
    shutil.copyfile(artifact["path"], tools / artifact["path"].name)
    shutil.copyfile(ROOT / "LICENSE", tools / "LICENSE.txt")
    (folder / "mozhi.nuspec").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd"><metadata>
<id>mozhi</id><version>{VERSION}</version><title>Mozhi</title><authors>Jessenth Ebenezer</authors><owners>sm1else-bot</owners>
<projectUrl>{REPO}</projectUrl><projectSourceUrl>{REPO}</projectSourceUrl><licenseUrl>{REPO}/blob/v{VERSION}/LICENSE</licenseUrl>
<requireLicenseAcceptance>false</requireLicenseAcceptance><summary>Tamil-inspired interpreted programming language</summary>
<description>Mozhi CLI, REPL and syntax checker with a bundled Python runtime. No separate Python installation required.</description>
<tags>mozhi language interpreter tamil tanglish cli</tags><releaseNotes>{REPO}/releases/tag/v{VERSION}</releaseNotes>
<docsUrl>https://projects.jessenth.com/mozhi/learn/</docsUrl><bugTrackerUrl>{REPO}/issues</bugTrackerUrl>
</metadata><files><file src="tools/**" target="tools" /></files></package>\n''', encoding="utf-8")
    install = f'''$ErrorActionPreference = 'Stop'
if (-not [Environment]::Is64BitOperatingSystem) {{ throw 'Mozhi requires Windows x64.' }}
$tools = Split-Path -Parent $MyInvocation.MyCommand.Definition
$archive = Join-Path $tools '{artifact['path'].name}'
$checksum = '{artifact['sha256']}'
$url = '{base}/{artifact['path'].name}'
if (Test-Path -LiteralPath $archive) {{
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $checksum) {{ throw 'Mozhi archive checksum mismatch.' }}
    Get-ChocolateyUnzip -FileFullPath $archive -Destination $tools -PackageName 'mozhi'
}} else {{
    Install-ChocolateyZipPackage -PackageName 'mozhi' -Url64bit $url -Checksum64 $checksum -ChecksumType64 'sha256' -UnzipLocation $tools
}}
$exe = Join-Path $tools 'mozhi.exe'
Set-Content -LiteralPath ($exe + '.ignore') -Value ''
Install-BinFile -Name 'mozhi' -Path $exe
'''
    (tools / "chocolateyinstall.ps1").write_text(install, encoding="utf-8")
    (tools / "chocolateyuninstall.ps1").write_text("$ErrorActionPreference = 'Stop'\n$tools = Split-Path -Parent $MyInvocation.MyCommand.Definition\nUninstall-BinFile -Name 'mozhi' -Path (Join-Path $tools 'mozhi.exe')\n", encoding="utf-8")
    (tools / "VERIFICATION.txt").write_text(f"Official source: {base}/{artifact['path'].name}\nSHA-256: {artifact['sha256']}\nArchive contains a native smoke-tested PyInstaller executable and Python runtime.\n", encoding="utf-8")


def linux(artifact, base, output):
    directory = output / "linux"
    directory.mkdir(parents=True, exist_ok=True)
    name = artifact["path"].name
    (directory / "PKGBUILD").write_text(f'''pkgname=mozhi-bin
pkgver={VERSION}
pkgrel=1
pkgdesc='Tamil-inspired interpreted programming language'
arch=('x86_64')
url='{REPO}'
license=('MIT')
depends=('glibc' 'zlib')
provides=('mozhi')
conflicts=('mozhi')
source=("{base}/{name}")
sha256sums=('{artifact['sha256']}')
package() {{
  install -Dm755 mozhi "$pkgdir/usr/bin/mozhi"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  cp -r LICENSES "$pkgdir/usr/share/licenses/$pkgname/"
}}
''', encoding="utf-8")
    (directory / "mozhi.spec").write_text(f'''Name: mozhi
Version: {VERSION}
Release: 1%{{?dist}}
Summary: Tamil-inspired interpreted programming language
License: MIT
URL: {REPO}
Source0: {base}/{name}
ExclusiveArch: x86_64
Requires: glibc >= 2.35, zlib
AutoReqProv: no
%global debug_package %{{nil}}
%description
Mozhi CLI, REPL and syntax checker with a bundled Python runtime.
%prep
%setup -q -c
%build
%install
install -Dm755 mozhi %{{buildroot}}%{{_bindir}}/mozhi
%check
test "$(./mozhi --version)" = "Mozhi {VERSION}"
%files
%{{_bindir}}/mozhi
%license LICENSE LICENSES
''', encoding="utf-8")
    debian = directory / "debian" / "DEBIAN"
    debian.mkdir(parents=True, exist_ok=True)
    (debian / "control").write_text(f"Package: mozhi\nVersion: {VERSION}\nSection: devel\nPriority: optional\nArchitecture: amd64\nMaintainer: Jessenth Ebenezer <jessenth12@gmail.com>\nDepends: libc6 (>= 2.35), zlib1g\nHomepage: {REPO}\nDescription: Tamil-inspired interpreted programming language\n Bundled interpreter, REPL and syntax checker; no separate Python installation.\n", encoding="utf-8")


def prepare(folder, output, partial=False):
    artifacts = checked_archives(folder, partial)
    python_distributions = checked_python(folder, required=not partial)
    base = f"{REPO}/releases/download/v{VERSION}"
    output.mkdir(parents=True, exist_ok=True)
    checksums = []
    for file in sorted(folder.iterdir()):
        if file.is_file() and (file.suffix in {".whl", ".deb", ".rpm", ".nupkg"} or file.name.endswith((".tar.gz", ".zip"))):
            checksums.append(f"{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}")
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    if any(not target.startswith("windows") for target in artifacts):
        tap = output / "homebrew-mozhi" / "Formula"
        tap.mkdir(parents=True, exist_ok=True)
        (tap / "mozhi.rb").write_text(homebrew(artifacts, base), encoding="utf-8")
    if "windows-x64" in artifacts:
        winget(artifacts["windows-x64"], base, output)
        chocolatey(artifacts["windows-x64"], base, output)
    if "linux-x64" in artifacts:
        linux(artifacts["linux-x64"], base, output)
    manifest = {"version": VERSION, "repository": REPO, "wingetIdentifier": IDENTIFIER,
                "publicationStatus": "prepared-only-not-published", "completePlatformSet": len(artifacts) == len(TARGETS),
                "pythonDistributions": python_distributions,
                "artifacts": {target: {"filename": item["path"].name, "sha256": item["sha256"], "evidence": item["metadata"]} for target, item in artifacts.items()}}
    (output / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    notes = f"""Mozhi {VERSION}

Standalone interpreted Mozhi CLI: run, shorthand file execution, REPL, syntax checking.
Includes the Python runtime in native archives. PyPI wheel/sdist require Python 3.10+.

Archives: Windows x64, macOS ARM64/x64 (tested on macOS 15), Linux x64 (glibc 2.35+).
Each native artifact passed run/check/repl/version smoke tests outside the checkout with an empty PATH.
SHA256SUMS records download integrity. Signing/notarization is not asserted by this build.
Unsigned downloads may receive operating-system trust warnings; see docs/distribution.md.

The early Git commits are retrospective archival reconstructions, not original dated commits.
See PROVENANCE.md. Bundling the Python interpreter does not compile Mozhi programs.

Package-manager files are prepared for submission; this does not mean registry acceptance.
"""
    (output / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    print(f"Prepared {len(artifacts)} tested platform(s): {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, default=ROOT / "dist/releases")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/package-managers")
    parser.add_argument("--allow-partial", action="store_true", help="local/native CI validation only; not publishable")
    args = parser.parse_args()
    prepare(args.artifacts.resolve(), args.output.resolve(), args.allow_partial)
