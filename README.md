# Mozhi

A Tanglish programming language with Tamil-inspired, verb-final syntax.

```mozhi
"Vanakkam, world!" sollu
a = 10 vechukko
"Value: " kooda a sollu
```

Mozhi explores grammar as well as vocabulary. `sollu` (say) follows the expression, `vechukko` (keep/store) closes an assignment, and conditions precede `na` or `varaikum`. Assignment still uses infix `=`, so this is a hybrid syntax rather than a fully postfix stack language. Tamil has many dialects and constructions; Mozhi is an experiment, not a complete model of Tamil grammar.

**Historical note:** Mozhi was conceived on May 31, 2026, and developed further in June 2026. This GitHub repository was first published on October 27, 2026. Its early Git commits are retrospectively dated archival reconstructions from recovered source files and development records, not original commits made at that time. See [PROVENANCE.md](PROVENANCE.md) for methodology and evidence.

## Status

This is an experimental language with an explicitly preserved archival history. The current CLI and browser adapters share parser/runtime fixes through generated browser code. Neither is production-ready, Python-compatible, or a sandbox for untrusted code. Original interpreter stages remain unchanged in the archival commits.

## Run the CLI

Use Python 3.10 or later. The CLI uses only the standard library and needs no pip install.

```sh
python src/mozhi.py examples/hello.mozhi
python -m unittest discover -s tests -v
```

Expected hello output:

```text
Vanakkam, world!
Value: 10
```

There is no installed `mozhi` command or packaged REPL yet. Invoking the CLI without a filename (or with `--example`) runs the built-in demo. All five programs in `examples/` now work with the CLI and browser; the calculator requests interactive input.

## Use the playground

From the repository root:

```sh
python -m http.server 8000
```

Open [the playground locally](http://localhost:8000/playground/). Wait for **Run Mozhi**, paste code, and run it. For the historical programs, copy the contents of `examples/demo.mozhi`, `library.mozhi`, `gossip.mozhi`, or `calculator.mozhi` into the editor. Calculator inputs 1, 10, 5, 6 add ten, show it, and exit the menu.

CodeMirror 5.65.13 and Pyodide 0.23.4 load from external CDNs. First loading needs network access. The playground uses plain-text editing, not dedicated Mozhi syntax highlighting. A plain textarea remains usable if CodeMirror fails to load. Stop the local server with Ctrl+C.

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

See [LANGUAGE.md](LANGUAGE.md) for the supported syntax and [the documentation source](docs/index.md) for examples. The browser runs a generated asynchronous adapter, `playground/runtime.py`, in Pyodide. `tools/sync_playground.py` generates its parser/runtime from `src/mozhi.py`; input/output adapters differ, but language fixes are kept together. After changing the core, run `python tools/sync_playground.py`. A regression check detects a stale generated artifact.

## Known limitations

- This is still an experimental language, not full Python compatibility. Constructors are called manually after `ClassName porul`; indexed assignment and module imports are not implemented.
- Errors now report source statement lines and validate indentation, argument counts, array indices, properties, input conversion and control-flow placement. There is no exception-handling syntax for recovering within a Mozhi program yet.
- The browser limit measures elapsed execution time outside input waits, not CPU instructions. A stopped worker must reload Pyodide. Extremely memory-hungry programs are not safely sandboxed. CLI execution remains unbounded; use Ctrl+C or an external process timeout for intentional endless programs.
- No module/package ecosystem, standard library collection, compatibility guarantee, packaged installer, dedicated highlighter, or official GitHub Linguist recognition is included.

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
```

`MOZHI_TEST_BROWSER` may name an existing Chrome/Chromium executable instead of the Playwright download. The checks use a fresh temporary profile, exercise worker Stop/timeout/recovery and input pauses, and do not operate your personal browser session.

## Documentation

```sh
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
python -m mkdocs build --strict
```

The generated `site/` is ignored. The docs cover [runtime controls](docs/runtime.md), [operators](docs/basics/operators.md), and [error handling](docs/errors.md). Exact original documentation remains in the archival commits.

## Roadmap and contributions

Next: a fuller language specification, deeper runtime coverage, a CLI/REPL package, syntax highlighting and editor integration, then modules and packaging. Official Linguist recognition is a future milestone; `.mozhi` files are not relabeled as Python.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes. The language concept and syntax were directed by the project author; implementation was AI-assisted with Claude, then Gemini and Google Antigravity. These tools assisted development rather than independently originating the author's language idea.

Licensed under [MIT](LICENSE). [HISTORY.md](HISTORY.md) describes the chronology; [PROVENANCE.md](PROVENANCE.md) explains the retrospective commits.
