# Distribution and release engineering

Mozhi remains an interpreted language. PyInstaller bundles its Python interpreter,
stdlib and Mozhi package into an executable; it does **not** compile `.mozhi`
programs. Every channel uses `src/mozhi/core.py`. The only version source is
`src/mozhi/_version.py`; Python metadata, CLI output, filenames, manifests and
package versions derive from it.

## Availability versus preparation

This repository prepares distributions; preparation is not registry acceptance.
No actual release, PyPI upload, tap publication, or community submission is
authorized merely by running the build. A version tag triggers testing and
preparation only. Publication is a separately approved manual workflow.

| Channel | Prepared implementation | External prerequisite |
| --- | --- | --- |
| Direct download | Native archives, Python runtime, licenses, SHA-256 receipts | Approved GitHub Release |
| PyPI | Wheel, sdist, console script; no runtime pip dependencies | Name ownership, account/trusted publisher, approved upload |
| Homebrew | Generated multi-platform formula and native install/test/reinstall/uninstall checks | Publish `sm1else-bot/homebrew-mozhi` after release URLs work |
| WinGet | Validated `jessenth.Mozhi` version/installer/locale manifests, portable x64 ZIP | Submit to `microsoft/winget-pkgs` and pass review |
| Chocolatey | Embedded official archive, checksum validation, shim install/uninstall, versioned fallback URL, nupkg | Account, package-ID ownership, community moderation |
| AUR | Generated `mozhi-bin` PKGBUILD with exact archive digest | AUR account/SSH key, name check and maintenance |
| Debian/Ubuntu | Control metadata, `.deb` builder and native smoke/install/remove checks | Distro policy/review or approved direct-download packaging |
| Fedora | RPM spec and optional rpmbuild foundation | Fedora review, source packaging policy, maintained submission |

`jessenth.Mozhi` is the namespace explicitly selected by the maintainer, not a
claim of an already registered WinGet package. The PyPI JSON lookup for `mozhi`
returned 404 on 2026-10-28; that neither reserves the name nor guarantees future
availability. Check again immediately before publishing. Chocolatey, AUR and
distribution package IDs likewise require ownership/availability checks.

## Native targets

| Target | Native CI runner | Notes |
| --- | --- | --- |
| Windows x64 | `windows-2022`, x64 Python 3.12 | ZIP containing `mozhi.exe`; local Windows 11 builds also tested |
| macOS ARM64 | `macos-15`, ARM64 Python 3.12 | Native ARM64 binary; macOS 15 is the tested baseline |
| macOS x64 | `macos-15-intel`, x64 Python 3.12 | Native Intel binary; not a Universal 2 claim |
| Linux x64 | `ubuntu-22.04`, x64 Python 3.12 | glibc 2.35+ baseline; not a fully static or musl/Alpine binary |

There is no Windows ARM64, Linux ARM64 or universal macOS artifact yet. Do not
relabel an x64 binary as ARM64 or cross-build with PyInstaller. Native tests are
authoritative; old OS versions not exercised by those runners are not promised.
The Python wheel supports Python 3.10+, with compatibility CI on 3.10–3.14.

## Build locally

Use a clean Python 3.12 virtual environment on the target operating system. A
build on Windows produces Windows artifacts; macOS and Linux require native
runners. Installing from the checkout with Python remains an independent option.

```sh
python -m venv .venv
# Activate the venv using your shell's standard command.
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -q
python -m build
python -m twine check dist/*.whl dist/*.tar.gz
python tools/build_standalone.py
python tools/smoke_archive.py dist/releases
python tools/prepare_release.py --allow-partial
```

On Windows, the venv interpreter can be called directly as
`.venv\Scripts\python.exe`; on Unix use `.venv/bin/python`.

`--allow-partial` prepares metadata for the locally available platform and marks
the result incomplete. It is for development/native CI, not publication. The
final aggregation must call `prepare_release.py` **without** that option and
provide all four tested native archives plus Python distributions.

Artifacts use:

```text
mozhi-<version>-windows-x64.zip
mozhi-<version>-macos-arm64.tar.gz
mozhi-<version>-macos-x64.tar.gz
mozhi-<version>-linux-x64.tar.gz
mozhi-<version>-py3-none-any.whl
mozhi-<version>.tar.gz
SHA256SUMS
```

Native archives include `mozhi`/`mozhi.exe`, the project's MIT license, bundled
Python/PyInstaller notices, and `build-info.json`. The latter records the native
target, Python/bundler versions, CLI/core source digests and smoke-test evidence.
Checksums and source digests are validated again when aggregating. A changed
interpreter requires rebuilding the native binaries; stale archives are rejected.

PyInstaller and the build front end are pinned in `requirements-build.txt`.
Archive member timestamps/order/ownership are normalized. OS images, transitive
tool dependencies, native libraries and signing can still change bytes: this is
not a promise of bit-for-bit reproducibility across machines. Retain workflow
logs and the exact tool versions with each release, and use clean runners.

## Verification gates

The distribution workflow builds on all four native runners. Before uploading
an artifact it tests its binary outside the checkout, with an empty PATH and
Python-related environment settings removed, then extracts and tests the actual
archive. It exercises `--version`, help, UTF-8 paths/output, `run`, shorthand,
non-executing `check`, runtime/syntax failures, persistent multiline REPL state,
and error recovery. The Python wheel is installed and uninstalled in a fresh
external venv. Reinstall/upgrade mechanics are checked using the same version;
cross-version upgrade compatibility must be tested when a second version exists.

macOS checks Homebrew installation, its test block, reinstall and uninstall using
a local-archive copy of the generated formula. Windows checks Chocolatey pack,
local-feed install, forced upgrade/reinstall and uninstall on the disposable
runner. Never run those system-install tests on a personal machine without
understanding their effects; the helper requires `--disposable-runner`.

WinGet metadata is validated against vendored official 1.10.0 schemas, and can be
checked with `winget validate --manifest <generated-version-directory>`. Full
WinGet install/upgrade/uninstall against its official URL must be repeated after
the approved release exists; before publication that URL deliberately has no
download to install. The contained ZIP is already exercised independently.

Linux builds `.deb` when `dpkg-deb` exists, tests extracted execution, and CI
installs/reinstalls/removes it. If `rpmbuild` is available the helper builds an RPM;
otherwise it explicitly reports an unbuilt foundation. AUR scripts receive shell
syntax checks. None of this constitutes Debian, Fedora or AUR acceptance.

## Package-manager publication

The complete build emits `prepared-release` in GitHub Actions. It contains
`releases/` and `package-managers/`, including the final formula, WinGet manifests,
Chocolatey package sources, Linux recipes, checksums and release notes. These
files use real computed hashes, not placeholders. URLs target the matching
versioned GitHub Release; test every URL after publishing it.

**Homebrew:** use the generated `homebrew-mozhi/Formula/mozhi.rb` to populate the
official `sm1else-bot/homebrew-mozhi` tap once that release exists. Then the user
workflow is `brew tap sm1else-bot/mozhi` followed by `brew install mozhi`.
`brew upgrade mozhi` and `brew uninstall mozhi` follow normal Homebrew behavior.
Homebrew/core acceptance is separate and normally calls for a reviewed
source-build formula; do not advertise an untapped `brew install mozhi` today.

**WinGet:** submit the generated `winget/manifests/j/jessenth/Mozhi/<version>/`
directory to `microsoft/winget-pkgs`. Run manifest validation, then after the URL
is public test a local manifest install, upgrade and uninstall. Wait for the
community PR and source ingestion before advertising
`winget install --id jessenth.Mozhi --exact`.

**Chocolatey:** `choco pack <generated>/chocolatey/mozhi.nuspec` builds a package
with the official ZIP embedded, so install tests need no unpublished download.
The installer validates SHA-256, extracts its executable and creates a shim;
uninstall removes that shim and Chocolatey removes package-owned files. The same
install script handles upgrades. The fallback downloader also enforces SHA-256
against a versioned official URL. Submit with the maintainer's community API key
only after package-ID ownership is established. Pass package validation,
verification/VirusTotal and moderation. Unsigned PyInstaller files can attract
false positives; investigate rather than disabling endpoint protection.

**PyPI:** run `python -m build`, `python -m twine check dist/*.whl dist/*.tar.gz`,
then install the wheel from outside the checkout. Configure PyPI Trusted
Publishing for this repository's approved publishing workflow, or use Twine with
a scoped credential stored outside the repository. Verify name ownership before
the first upload. Only then advertise `pip install mozhi`. Pip users need Python;
native executable users do not.

**Linux:** review generated `linux/PKGBUILD`, `linux/debian/` and `linux/mozhi.spec`.
The binary PKGBUILD is for `mozhi-bin` and conflicts with/provides `mozhi`.
Debian and Fedora official packaging policies usually prefer source packages and
distribution-managed Python dependencies, not vendoring a Python runtime. Use
these binary recipes as tested foundations/direct artifacts, not assertions that
official maintainers will accept them. A package manager can install Python as a
dependency automatically in a future source package. No custom apt/dnf repository
is added by this project.

## Signing and notarization

Code signing and notarization are not inferred from a successful test. Without
provided credentials these builds are unsigned on Windows and normally ad-hoc
signed on macOS by PyInstaller, not Developer ID notarized distributions.

- macOS public distribution normally needs an Apple Developer Program account,
  Developer ID Application certificate/private key, appropriate hardened-runtime
  configuration, and `notarytool` credentials. PyInstaller accepts
  `MOZHI_CODESIGN_IDENTITY` when an identity is already installed in the runner
  keychain. Configure secrets and notarization separately, validate with
  `codesign --verify` and Gatekeeper assessment, and rebuild the archive/checksums
  **after** any signing changes. Do not assume a raw CLI binary can be stapled in
  the same manner as an app or signed installer; select an appropriate notarizable
  container when enabling that release path.
- Windows Authenticode needs a code-signing certificate or authorized signing
  service (often a hardware-backed key) and a trusted timestamp service. Use
  `signtool sign`/`verify` in an approved signing environment, then rebuild archive
  digests and package metadata. A signed binary alone does not guarantee immediate
  SmartScreen reputation.
- Keep certificate passwords, signing keys, registry tokens and account secrets
  in approved secret stores. None are fabricated or committed here. Unsigned
  releases require an explicit maintainer decision and clear release notes.

## Release-maintainer checklist

1. Update only `src/mozhi/_version.py`; review compatibility and release notes.
2. Confirm package names/ownership, copyright notices and dependency licenses.
3. Run language, CLI, browser, packaging and archival-evidence checks.
4. Push the version tag only after reviewing the source. Its distribution workflow
   prepares artifacts but does not create even a draft GitHub Release.
5. Require all four native jobs and final aggregation to pass. Inspect build
   metadata, SHA256SUMS, generated package-manager files and install/uninstall logs.
6. Decide signing/notarization, provide approved credentials if required, and rerun
   all validation after signing. Record supported OS baselines and limitations.
7. Obtain explicit approval for the concrete version/artifacts. Configure the
   GitHub `release` environment with required reviewers. The manual **Publish
   approved release** workflow defaults publication approval to false; it verifies
   the tag, exact successful native build commit, complete artifact set and hashes.
8. After publication, verify every download and package-manager URL. Submit/publish
   the tap and community manifests/packages with their respective credentials.
9. Publish PyPI only through its separately approved credential/trusted-publisher
   path. Verify wheel installation, and record the actual registry project URL.
10. Test real upgrades from the previous release and removal through each accepted
    manager. Record moderation/acceptance links before updating availability claims.
11. Never overwrite a released asset with new bytes. Issue a new version for fixes.
    Retain known-good artifacts and notes for rollback; do not rewrite archival Git
    history or evidence hashes.

The project has no authority to guarantee registry approval timelines. External
acceptance, publisher ownership, signing accounts and release approval are real
remaining steps, not implied by successful CI.

References: [PyInstaller](https://pyinstaller.org/en/stable/operating-mode.html),
[Homebrew formula guidance](https://docs.brew.sh/Formula-Cookbook),
[WinGet manifests](https://learn.microsoft.com/windows/package-manager/package/manifest),
[Chocolatey ZIP packages](https://docs.chocolatey.org/en-us/guides/create/create-zip-package/).
