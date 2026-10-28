# Mozhi

A Tanglish programming language with Tamil-inspired, verb-final syntax.

```mozhi
"Vanakkam, world!" sollu
a = 10 vechukko
"Value: " kooda a sollu
```

Mozhi explores grammar as well as vocabulary. `sollu` (say) follows the expression, `vechukko` (keep/store) closes an assignment, and conditions precede `na` or `varaikum`. Assignment still uses infix `=`, so this is a hybrid syntax rather than a fully postfix stack language. Tamil has many dialects and constructions; Mozhi is an experiment, not a complete model of Tamil grammar.

**Historical note:** Mozhi was conceived on May 31, 2026, and developed further in June 2026. This GitHub repository was first published on October 27, 2026. Its early Git commits are retrospectively dated archival reconstructions from recovered source files and development records, not original commits made at that time. See [PROVENANCE.md](https://github.com/sm1else-bot/mozhi/blob/main/PROVENANCE.md) for methodology and evidence.

## Status

This is an experimental language with an explicitly preserved archival history. The current CLI and browser adapters share parser/runtime fixes through generated browser code. Neither is production-ready, Python-compatible, or a sandbox for untrusted code. Original interpreter stages remain unchanged in the archival commits.

## Install and run the CLI

### Debian / Ubuntu x64

```sh
curl -fLO https://github.com/sm1else-bot/mozhi/releases/download/v0.1.0/mozhi_0.1.0_amd64.deb
curl -fLO https://github.com/sm1else-bot/mozhi/releases/download/v0.1.0/mozhi_0.1.0_amd64.deb.sha256
sha256sum -c mozhi_0.1.0_amd64.deb.sha256
sudo apt install ./mozhi_0.1.0_amd64.deb
```

Python is bundled. The package requires x86-64, glibc 2.35+ and `zlib1g`.
It does not configure an APT repository or make `apt install mozhi` available
from Debian/Ubuntu's official archives. Upgrade by downloading and installing
the next verified `.deb`; remove with `sudo apt remove mozhi`.

### PyPI and Homebrew

[Mozhi 0.1.0 is available on PyPI](https://pypi.org/project/mozhi/0.1.0/). Install with Python 3.10 or later:

```sh
python -m pip install mozhi
mozhi --version
mozhi repl
```

See the [PyPI project](https://pypi.org/project/mozhi/) for published versions.
Create a UTF-8 `.mozhi` file, then use `mozhi run file.mozhi` to execute it or
`mozhi check file.mozhi` to validate its syntax without running it.

On macOS (Apple Silicon or Intel) and Linux x64, install the bundled interpreter through the [official Homebrew tap](https://github.com/sm1else-bot/homebrew-mozhi). This option does not need a separate Python installation:

```sh
brew install sm1else-bot/mozhi/mozhi
mozhi --version
```

The tested baselines are macOS 15 and Linux with glibc 2.35+. This is a maintainer tap, separate from Homebrew/core.

Install from this checkout with Python 3.10 or later (no runtime dependencies):

```sh
python -m pip install -e .
mozhi --version
mozhi run examples/hello_world.mozhi
mozhi examples/fibonacci.mozhi
mozhi check examples/file_io.mozhi
mozhi repl
```

`mozhi` works outside the repository after installation. `python -m mozhi` is also supported. Local programs have no execution timeout. Ctrl+C returns exit code 130; source/runtime/I/O errors go to stderr and return 1, and usage errors return 2. Source and terminal pipes use UTF-8. `check` parses without running statements.

The REPL retains variables and functions, continues multiline blocks until `mudivu`, echoes expression values, and recovers from errors. `quit`, `exit`, or EOF ends the session. A failed block may have already changed state; the REPL does not roll back executed statements.

Build Python distributions with `python -m pip install -r requirements-build.txt` and `python -m build`. Standalone Windows, macOS and Linux archives bundle Python with PyInstaller, so end users do not need to install Python. See [distribution and installation](https://github.com/sm1else-bot/mozhi/blob/main/docs/distribution.md) for native build commands, package-manager preparation, and publication status.

**Distribution channels:** PyPI is the first public distribution channel. Version 0.1.0 was published on October 28, 2026 through GitHub Actions Trusted Publishing and verified with a clean public-registry installation. Homebrew is available through the maintainer tap, using the verified native archives from the [v0.1.0 GitHub Release](https://github.com/sm1else-bot/mozhi/releases/tag/v0.1.0). WinGet, Chocolatey, AUR, Debian and Fedora registry entries remain unpublished. No release is published automatically by a version tag.

The downloadable `.deb` is public; official Debian/Ubuntu archive listings remain
unpublished. [Installation](https://projects.jessenth.com/mozhi/learn/install/)
covers native downloads, PATH, upgrades, removal and platform requirements.

### CLI guides

- [Command reference](https://projects.jessenth.com/mozhi/learn/cli/)
- [First program, file paths and pipes](https://projects.jessenth.com/mozhi/learn/cli/programs/)
- [Interactive REPL](https://projects.jessenth.com/mozhi/learn/cli/repl/)
- [CLI example programs](https://projects.jessenth.com/mozhi/learn/examples/cli-programs/)
- [Troubleshooting](https://projects.jessenth.com/mozhi/learn/troubleshooting/)

Examples under `examples/` require a checkout or individual source downloads.
Installing a wheel/native package does not create that folder in your current
directory. `check` validates syntax only, not runtime names, types or arithmetic.
Ctrl+C stops a file run with status 130; in the REPL it returns to the prompt.

The opening program in this README prints:

```text
Vanakkam, world!
Value: 10
```

The legacy `python src/mozhi.py file.mozhi` entry point remains supported; without arguments it still runs the original built-in demo. The installed `mozhi` command shows help without arguments. Existing examples are preserved. New examples cover Fibonacci, recursion, arrays, UTF-8 file I/O, timing, and an 11-second local computation. File I/O is explicitly local-only; the browser retains its own execution limit.

## Use the playground

Open [Mozhi Studio](https://sm1else-bot.github.io/mozhi/) or read [Learn](https://sm1else-bot.github.io/mozhi/learn/). GitHub Pages builds and publishes the combined site after checks pass on each push to `main`.

From the repository root:

```sh
python -m pip install -r requirements-docs.txt
python tools/build_site.py
python -m http.server 8000 --directory site
```

Open [the playground locally](http://localhost:8000/playground/). The light studio includes eight guided lessons, practice tasks, hints, and progress earned by running working programs. Browse eight examples, including the original demo, library, gossip, and calculator programs. Calculator inputs 1, 10, 5, 6 add ten, show it, and exit the menu.

**Studio** contains the interactive lessons, **Learn** opens the full MkDocs documentation, and **Examples** opens the program gallery. The combined build places these at `playground/`, `learn/`, and `examples/` within the ignored `site/` directory. Its relative links also work when hosted under a repository path. Rebuild after editing sources; generated files are not committed.

The editor includes Mozhi syntax highlighting, keyword tooltips, a searchable reference, error line navigation, font and wrapping controls, file import/export, and a command palette. Use Ctrl+Enter to run, Ctrl+Shift+Enter to stop, Ctrl+K to search, or Ctrl+S to download. The interface adapts to phones and supports keyboard navigation.

Drafts, preferences, lesson progress, and the last eight runs are saved in browser storage on this origin. Replacing edited code asks for confirmation and keeps the previous draft recoverable from editor settings. Clearing browser data removes these records. Download important programs for a durable copy. **Share code** encodes the current program in a URL fragment without uploading it to a storage service. Anyone with the link can read the code; recipients need access to the same hosted website. A localhost link only works on your computer.

CodeMirror 5.65.13 and Pyodide 0.23.4 load from external CDNs, and optional web fonts load from Google Fonts. First loading needs network access. A plain textarea remains usable if CodeMirror fails to load. Stop the local server with Ctrl+C.

Programs execute in a worker. **Stop** terminates even a tight infinite loop, and a configurable execution limit defaults to **10 seconds** (0.1–3600 seconds). Waiting for user input pauses the timer; submitting input resumes the remaining budget. Stopping or timing out cancels pending input and creates a fresh engine. Engine-load failures expose **Retry engine**. Output is capped at 65,536 JavaScript characters to keep runaway printing responsive. This is a usability limit, not a security sandbox.

## Implemented features and differences

| Feature | CLI adapter | Browser adapter |
| --- | --- | --- |
| Numbers, strings, booleans, arithmetic, conditions | Present | Present |
| Functions and return | Present | Present |
| Arrays, indexing, push/pop | Present | Present |
| Loops and outer-variable updates | Fixed; updates find the defining scope | Same semantics |
| Classes and methods | Properties, bound instances, method closures | Same semantics |
| Input | Synchronous `kelu(...)` or `ketukko(...)` | Both aliases, asynchronously awaited |
| Length and conversion | `neelam`, `enn`, `padam`, `vaari` | Same names |
| `podhum` | Terminates the current program, including nested calls | Same semantics; engine remains reusable |

See [LANGUAGE.md](https://github.com/sm1else-bot/mozhi/blob/main/LANGUAGE.md) for the supported syntax and [the documentation source](https://github.com/sm1else-bot/mozhi/blob/main/docs/index.md) for examples. The browser runs a generated asynchronous adapter, `playground/runtime.py`, in Pyodide. `tools/sync_playground.py` generates its parser/runtime from `src/mozhi/core.py`; input/output adapters differ, but language fixes are kept together. After changing the core, run `python tools/sync_playground.py`. A regression check detects a stale generated artifact.

## Known limitations

- This is still an experimental language, not full Python compatibility. Constructors are called manually after `ClassName porul`; indexed assignment and module imports are not implemented.
- Errors now report source statement lines and validate indentation, argument counts, array indices, properties, input conversion and control-flow placement. There is no exception-handling syntax for recovering within a Mozhi program yet.
- The browser limit measures elapsed execution time outside input waits, not CPU instructions. A stopped worker must reload Pyodide. Extremely memory-hungry programs are not safely sandboxed. CLI execution remains unbounded; use Ctrl+C or an external process timeout for intentional endless programs.
- There is no module system, compatibility guarantee, or official GitHub Linguist recognition. Native archives, the `.deb`, PyPI and the maintainer Homebrew tap are public; other prepared package-manager metadata is not an accepted registry listing. The playground highlighter is a lightweight token highlighter, not a language server or autocomplete engine.

## Runtime checks

The Python suite runs language regressions against both the synchronous CLI and generated asynchronous browser adapter in bounded subprocesses:

```sh
python tools/sync_playground.py
python -m unittest discover -s tests -v
```

Optional actual-browser checks require Node.js 20 or later, network access, and Playwright's isolated Chromium:

```sh
npm ci
npx playwright install chromium
npm run test:browser
npm run test:studio
```

`MOZHI_TEST_BROWSER` may name an existing Chrome/Chromium executable instead of the Playwright download. The checks use a fresh temporary profile, exercise worker Stop/timeout/recovery and input pauses, and do not operate your personal browser session.

## Documentation

```sh
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
python -m mkdocs build --strict
```

The generated `site/` is ignored. After building, run `python tools/check_docs.py`
to validate documentation links, rendered anchors and runnable Mozhi snippets.
The docs cover installation, CLI/REPL use, functions, language features, the
standard library, browser controls and release maintenance. Exact original
documentation remains in the archival commits.

## Roadmap and contributions

Next: a fuller language specification, deeper runtime coverage, richer editor integration, a larger standard library, and modules. Official Linguist recognition is a future milestone; `.mozhi` files are not relabeled as Python.

Read [CONTRIBUTING.md](https://github.com/sm1else-bot/mozhi/blob/main/CONTRIBUTING.md) before proposing changes. The language concept and syntax were directed by the project author; implementation was AI-assisted with Claude, then Gemini and Google Antigravity. These tools assisted development rather than independently originating the author's language idea.

Licensed under [MIT](https://github.com/sm1else-bot/mozhi/blob/main/LICENSE). [HISTORY.md](https://github.com/sm1else-bot/mozhi/blob/main/HISTORY.md) describes the chronology; [PROVENANCE.md](https://github.com/sm1else-bot/mozhi/blob/main/PROVENANCE.md) explains the retrospective commits.
