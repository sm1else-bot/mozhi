# Troubleshooting

## `mozhi` is not found

Check that installation finished and open a new terminal after changing PATH.
For PyPI, run `python -m pip show mozhi` with the interpreter used to install it,
then try `python -m mozhi --version`. An activated virtual environment exposes
its own console scripts; a different Python environment may not contain Mozhi.

Homebrew users can run `brew list --versions mozhi` and inspect
`brew --prefix`. A `.deb` install places the command at `/usr/bin/mozhi`.
For an extracted archive, try `./mozhi --version` or `.\mozhi.exe --version`
before adding its directory to PATH.

If multiple installations exist, use `command -v mozhi` on Unix or
`Get-Command mozhi -All` in PowerShell to see which command runs. Upgrade or
remove it using the same installer that created it.

## Python installation is externally managed

Use [a virtual environment](install.md#pypi), Homebrew or the bundled `.deb`.
A virtual environment on some Debian/Ubuntu systems needs their `python3-venv`
package. Do not assume that a pip installed into one Python environment changes
another environment or a standalone native executable.

## The Debian package will not install

Use `sudo apt install ./mozhi_0.1.0_amd64.deb` from its download directory so APT
can resolve `libc6` and `zlib1g`. Verify the `.sha256` receipt first. Check
`dpkg --print-architecture`: this release requires `amd64` and glibc 2.35+.
It does not support Debian 11, Ubuntu 20.04, ARM64 or Alpine/musl.

`apt install mozhi` cannot find an uninstalled package in the official archives;
download the local `.deb`. This project does not configure an APT repository.
If dependencies cannot be resolved, use a supported OS or the Python source
package with Python 3.10+, rather than forcing an incompatible binary install.

## The native executable is rejected

Check OS/CPU against the [installation matrix](install.md), verify the download
hash, and extract all archive contents to a dedicated folder. An x64 executable
is not an ARM64 build. Windows executables are unsigned and macOS binaries are
ad-hoc signed without Developer ID notarization; see
[signing status](distribution.md#signing-and-notarization).

## Files cannot be found

Source paths and file-built-in paths start from the terminal's current working
directory. Quote spaces and use an absolute path if needed. Example programs
are downloaded separately or run from the checkout. A wheel install does not
put the repository examples in your working directory.

The CLI reads UTF-8, including an optional BOM. Save files as UTF-8 if a decoding
error occurs. A terminal lacking Tamil glyphs can show missing characters even
when the file and output encoding are correct.

## `check` passes but execution fails

`check` parses without executing. Undefined names, invalid input, missing files,
array bounds and division by zero can still fail at runtime. Consult
[errors](errors.md). It is not a type checker or a program-verification tool.

## A program keeps running

CLI programs have no automatic time limit. Ctrl+C stops a file run or returns a
REPL entry to its prompt. In Studio, use **Stop**, or adjust the browser's
execution budget. [Runtime controls](runtime.md) describe input waits and recovery.

## The browser cannot read a local file

The file built-ins are explicitly local-only. Use the editor's import/download
controls to move source text, or execute the program with the CLI. A shared
Studio link carries source text, not filesystem access or input answers.

## Report a problem

Include `mozhi --version`, installation method, operating system/architecture,
the smallest failing program, the exact command and diagnostic, and expected
output in [a GitHub issue](https://github.com/sm1else-bot/mozhi/issues). Do not
include credentials or private files. See [contributing](https://github.com/sm1else-bot/mozhi/blob/main/CONTRIBUTING.md).
