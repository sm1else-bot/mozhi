# Install Mozhi

Mozhi 0.1.0 is available through PyPI, the maintainer Homebrew tap, native
GitHub Release archives and a downloadable Debian package. All channels run the
same interpreted language. Native archives and the `.deb` bundle Python; PyPI
installation needs Python 3.10 or later.

## Choose an installation

| System | Recommended route | Separate Python needed? |
| --- | --- | --- |
| Ubuntu / Debian x64 | Download the `.deb` below | No |
| macOS Apple Silicon or Intel | Homebrew | No |
| Other Linux x64 with glibc 2.35+ | Homebrew or native archive | No |
| Windows x64 | Native ZIP, or PyPI with Python | ZIP: no; PyPI: yes |
| Systems with Python 3.10+ | PyPI in a virtual environment | Yes |

Native targets are Windows x64, macOS ARM64/Intel and Linux x64. Linux ARM64,
Alpine/musl and a universal macOS binary are not supplied. The native build
baselines are macOS 15 and Ubuntu 22.04 (glibc 2.35). See
[distribution engineering](distribution.md) for tested targets and limitations.

## Debian and Ubuntu

Download version 0.1.0 from the official release, verify it, then install:

```sh
curl -fLO https://github.com/sm1else-bot/mozhi/releases/download/v0.1.0/mozhi_0.1.0_amd64.deb
curl -fLO https://github.com/sm1else-bot/mozhi/releases/download/v0.1.0/mozhi_0.1.0_amd64.deb.sha256
sha256sum -c mozhi_0.1.0_amd64.deb.sha256
sudo apt install ./mozhi_0.1.0_amd64.deb
mozhi --version
```

The package installs `/usr/bin/mozhi`, requires `libc6 >= 2.35` and `zlib1g`, and
includes the Python runtime and license notices. It targets `amd64` (x86-64), not
ARM64. Check `dpkg --print-architecture` if unsure.

Public install, CLI/REPL/check, reinstall and removal passed on clean Ubuntu
22.04, Ubuntu 24.04 and Debian 12 containers. The
[verification run](https://github.com/sm1else-bot/mozhi/actions/runs/40776472622)
uses the actual release URL and checksum.

This is a local `.deb` installation. Mozhi is not in Debian/Ubuntu's official
repositories, and this package does not add an APT source. A bare
`sudo apt install mozhi` will not discover it on a fresh machine. For later
versions, download and verify the new `.deb`, then install that file with APT.

```sh
sudo apt install --reinstall ./mozhi_0.1.0_amd64.deb
sudo apt remove mozhi
```

The `.deb` was added after the initial native release. Its dedicated `.sha256`
file covers it; the original `SHA256SUMS` remains unchanged and covers the six
original archives/Python files. SHA-256 verifies download bytes, not a separate
package-signing identity.

## Homebrew

```sh
brew install sm1else-bot/mozhi/mozhi
mozhi --version
```

This uses [the maintainer tap](https://github.com/sm1else-bot/homebrew-mozhi),
separate from Homebrew/core. The qualified command selects the correct tap and
trusts only this formula on Homebrew 6. It supports macOS ARM64/Intel and Linux
x64, with Python bundled.

```sh
brew update
brew upgrade mozhi
brew uninstall mozhi
```

## PyPI

For a direct install into an existing Python environment:

```sh
python -m pip install mozhi
mozhi --version
```

For an isolated project environment on Linux/macOS:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install mozhi
```

On Windows PowerShell, activation is optional; call the environment directly:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install mozhi
.\.venv\Scripts\mozhi.exe --version
```

Use the interpreter that owns the environment for updates and removal:

```sh
python -m pip install --upgrade mozhi
python -m pip uninstall mozhi
```

If your operating system reports an externally managed Python environment, use a
virtual environment or choose Homebrew/the `.deb` rather than overriding that
protection. `python -m mozhi` provides the same CLI when its console-script
folder is not on PATH.

## Native archives

Download the matching file and `SHA256SUMS` from
[GitHub Releases](https://github.com/sm1else-bot/mozhi/releases/tag/v0.1.0).

| Platform | Archive |
| --- | --- |
| Windows x64 | `mozhi-0.1.0-windows-x64.zip` |
| macOS Apple Silicon | `mozhi-0.1.0-macos-arm64.tar.gz` |
| macOS Intel | `mozhi-0.1.0-macos-x64.tar.gz` |
| Linux x64 | `mozhi-0.1.0-linux-x64.tar.gz` |

Extract to a dedicated directory and retain `LICENSE`, `LICENSES/` and
`build-info.json` alongside the executable. Run `./mozhi --version` on Unix or
`.\mozhi.exe --version` in PowerShell. Put that directory on PATH to use `mozhi`
from any working directory. Windows users can compare `Get-FileHash -Algorithm
SHA256 <archive>` with the matching line in `SHA256SUMS` before extraction.

For manual upgrades, verify and extract the new archive into a new directory,
then update PATH. Remove the old directory when no longer needed. Uninstall by
removing that directory and its PATH entry. These archives do not install an
updater. Windows binaries are unsigned; macOS binaries are ad-hoc signed and
not Developer ID notarized.

## Development checkout

```sh
git clone https://github.com/sm1else-bot/mozhi.git
cd mozhi
python -m pip install -e .
mozhi run examples/hello_world.mozhi
```

Run this inside an activated Python 3.10+ environment. Examples referenced by
repository paths require a checkout; a wheel install does not copy an
`examples/` directory into your current folder. You can also download individual
programs from the [CLI example guide](examples/cli-programs.md).

Next: [your first program](cli/programs.md), [command reference](cli/index.md),
[REPL](cli/repl.md), or [installation troubleshooting](troubleshooting.md).
