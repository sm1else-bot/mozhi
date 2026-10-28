# Running Mozhi

## Command line

Use [Installation](install.md) to choose the public `.deb`, Homebrew, PyPI or
native archive. PyPI needs Python 3.10+; the other options bundle Python.

```sh
mozhi --version
mozhi run hello.mozhi
mozhi check hello.mozhi
mozhi repl
```

Create `hello.mozhi` with [the first-program guide](cli/programs.md).
[Command reference](cli/index.md) covers arguments and streams;
[REPL](cli/repl.md) covers multiline input and recovery;
[troubleshooting](troubleshooting.md) covers PATH and installation problems.
The Python installation also supports `python -m mozhi`. The legacy
`python src/mozhi.py` adapter still runs its built-in example without arguments
or with `--example`.

Exit codes are 0 for success, 1 for language/file errors, 2 for usage errors, and 130 for Ctrl+C. Output goes to stdout; errors include the filename and available statement line on stderr. Local programs are not subject to the browser timeout.

In the REPL, assignments and functions persist. Multiline blocks use the same grammar and `mudivu` terminator as files. Expressions echo their value; `quit`, `exit`, or EOF exits. Ctrl+C cancels the current input/run and keeps the session. Invalid input reports an error without discarding the environment. Already-executed changes are not rolled back.

Native distributions bundle Python. See [Distribution](distribution.md) for availability, native builds and package-manager preparation. [Standard library](standard-library.md) documents local file I/O and shared built-ins.

## Browser playground

Start a server from the repository root:

```sh
python -m pip install -r requirements-docs.txt
python tools/build_site.py
python -m http.server 8000 --directory site
```

Open `http://localhost:8000/playground/`. Wait for the engine to become ready, paste a program, and click **Run Mozhi**. Runtime files are fetched over HTTP, so opening the HTML directly as a `file:` URL is not supported. The browser downloads Pyodide 0.23.4 and CodeMirror 5.65.13 from external CDNs. A plain textarea is used if the editor library fails to load.

- **Stop** terminates the running worker, including tight infinite loops or a program waiting for input. It then starts a fresh engine.
- **Execution limit** defaults to 10 seconds and accepts 0.1–3600 seconds. It measures elapsed execution time outside input waits, not CPU instructions.
- **Input waits** pause the remaining budget. Submitting with Enter or the input button resumes that remaining budget rather than starting a new full interval.
- **Retry engine** is shown after a load failure. Check network access, then retry.
- **Output** is streamed with buffering and capped at 65,536 JavaScript characters. The cap prevents runaway printing from growing the page indefinitely.
- **One run at a time:** Run is disabled during execution, input, and loading. Old input requests are discarded after Stop or timeout.

`podhum` ends the entire current program without destroying the reusable engine. Runtime errors leave the controls ready for a new run. The worker and timeout are usability controls, not a security or memory sandbox. Do not run untrusted code on the assumption that they provide isolation from every resource hazard.

### Learning and editing

**Studio** contains the interactive lesson workspace. **Learn** opens this full MkDocs documentation, styled to match the studio. **Examples** opens the program gallery. Build with `tools/build_site.py` to preview all three together; serving only the source playground does not generate the Learn pages.

The studio has eight lessons covering output, variables, decisions, loops, arrays, functions, input, and objects. Each lesson includes an explanation, a runnable starter, a practice task, a hint, and expected output. Completion requires a successful run that passes the lesson's check. Progress is saved locally. Checks are lightweight learning aids, not exhaustive correctness proofs.

Use **Examples** for eight programs, including the original demo, calculator, library, and gossip sources. The **Reference** tab searches language keywords and provides copyable snippets. Hover over a keyword in the editor for its meaning. Errors highlight the reported source line and offer a button to navigate there.

Editor settings control font size and line wrapping. Import `.mozhi` or `.txt` files up to 256 KB and download the current program as UTF-8. Edited code is protected by a replacement confirmation. **Restore previous draft** in editor settings recovers the last replaced program.

| Shortcut | Action |
| --- | --- |
| Ctrl+Enter | Run |
| Ctrl+Shift+Enter | Stop |
| Ctrl+K | Search lessons, examples, and commands |
| Ctrl+S | Download the current program |
| ? outside text fields | Keyboard help |

### Local records and sharing

The current draft, editor preferences, completed lessons, and last eight runs are saved in browser local storage for this origin. Run records include source, output, outcome, and duration; use **Clear history** to remove them. Storage can be unavailable or cleared by the browser, so download programs you need to keep. Execution still works when storage is blocked.

**Share code** creates a link containing the source, filename, and lesson in its URL fragment. No application storage service receives the program. Anyone with the link can read its code; avoid including secrets. Sharing does not include run history or input answers. Links need a reachable deployment of this website; localhost links only work on the sender's computer. Programs exceeding the link size limit must be downloaded instead. The interface uses optional Google Fonts with system font fallbacks.

## Maintaining the two adapters

The synchronous core is `src/mozhi/core.py`; `src/mozhi.py` is a compatibility launcher. `tools/sync_playground.py` generates an asynchronous browser engine in `playground/runtime.py`, retaining the same parser and language behavior with a different input/output adapter. After core changes:

```sh
python tools/sync_playground.py
python -m unittest discover -s tests -v
```

The regression suite checks generation freshness and exercises both adapters in bounded subprocesses. After building the site, `python tools/check_docs.py` checks source links, rendered anchors and runnable snippets. Optional real-browser tests require Node.js 20 or later:

```sh
npm ci
npx playwright install chromium
npm run test:browser
npm run test:studio
```

Set `MOZHI_TEST_BROWSER` to an existing Chrome/Chromium executable to avoid downloading the test browser. Tests use a fresh temporary profile, not your personal browser session.
