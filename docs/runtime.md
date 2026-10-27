# Running Mozhi

## Command line

From the repository root, use Python 3.10 or later:

```sh
python src/mozhi.py examples/hello.mozhi
python src/mozhi.py examples/demo.mozhi
python src/mozhi.py examples/library.mozhi
python src/mozhi.py examples/gossip.mozhi
python src/mozhi.py examples/calculator.mozhi
```

The CLI uses the Python standard library. Without a filename, or with `--example`, it runs the built-in demonstration. Source files and redirected input/output use UTF-8. Both `kelu` and `ketukko` read a string. CLI programs have no automatic time limit; Ctrl+C stops a running program.

## Browser playground

Start a server from the repository root:

```sh
python -m http.server 8000
```

Open `http://localhost:8000/playground/`. Wait for the engine to become ready, paste a program, and click **Run Mozhi**. Runtime files are fetched over HTTP, so opening the HTML directly as a `file:` URL is not supported. The browser downloads Pyodide 0.23.4 and CodeMirror 5.65.13 from external CDNs. A plain textarea is used if the editor library fails to load.

- **Stop** terminates the running worker, including tight infinite loops or a program waiting for input. It then starts a fresh engine.
- **Execution limit** defaults to 10 seconds and accepts 0.1–3600 seconds. It measures elapsed execution time outside input waits, not CPU instructions.
- **Input waits** pause the remaining budget. Submitting with Enter or the input button resumes that remaining budget rather than starting a new full interval.
- **Retry engine** is shown after a load failure. Check network access, then retry.
- **Output** is streamed with buffering and capped at 65,536 JavaScript characters. The cap prevents runaway printing from growing the page indefinitely.
- **One run at a time:** Run is disabled during execution, input, and loading. Old input requests are discarded after Stop or timeout.

`podhum` ends the entire current program without destroying the reusable engine. Runtime errors leave the controls ready for a new run. The worker and timeout are usability controls, not a security or memory sandbox. Do not run untrusted code on the assumption that they provide isolation from every resource hazard.

## Maintaining the two adapters

The synchronous core is `src/mozhi.py`. `tools/sync_playground.py` generates an asynchronous browser engine in `playground/runtime.py`, retaining the same parser and language behavior with a different input/output adapter. After core changes:

```sh
python tools/sync_playground.py
python -m unittest discover -s tests -v
```

The regression suite checks generation freshness and exercises both adapters in bounded subprocesses. Optional real-browser tests require Node.js 20 or later:

```sh
npm ci
npx playwright install chromium
npm run test:browser
```

Set `MOZHI_TEST_BROWSER` to an existing Chrome/Chromium executable to avoid downloading the test browser. Tests use a fresh temporary profile, not your personal browser session.
