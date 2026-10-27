# Mozhi

A Tanglish programming language with Tamil-inspired, verb-final syntax.

```mozhi
"Vanakkam, world!" sollu
a = 10 vechukko
"Value: " kooda a sollu
```

Mozhi explores grammar as well as vocabulary. `sollu` (say) follows the expression, `vechukko` (keep/store) closes an assignment, and conditions precede `na` or `varaikum`. Assignment still uses infix `=`, so this is a hybrid syntax rather than a fully postfix stack language. Tamil has many dialects and constructions; Mozhi is an experiment, not a complete model of Tamil grammar.

**Historical note:** Mozhi was conceived on May 31, 2026, and developed further in June 2026. This repository was prepared in October 2026 for its first public publication, which is pending approval. Its early Git commits are retrospectively dated archival reconstructions from recovered source files and development records, not original commits made at that time. See [PROVENANCE.md](PROVENANCE.md) for methodology and evidence.

## Status

This is an experimental archival release. Two preserved interpreter stages are available: an earlier Python CLI and a later browser runtime. Their behavior differs. Neither is production-ready, Python-compatible, or a sandbox for untrusted code. Language repairs and packaging will follow separately.

## Run the CLI

Use Python 3; repository checks currently run on Python 3.13. The current CLI uses only the standard library and needs no pip install.

```sh
python src/mozhi.py examples/hello.mozhi
python -m unittest discover -s tests -v
```

Expected hello output:

```text
Vanakkam, world!
Value: 10
```

There is no installed `mozhi` command or packaged REPL yet. Always pass an explicit file: invoking the CLI without a filename runs its historical built-in demo, whose loop can fail to terminate. The four preserved June examples target the later browser runtime.

## Use the playground

From the repository root:

```sh
python -m http.server 8000
```

Open [the playground locally](http://localhost:8000/playground/). Wait for **Run Mozhi**, paste code, and run it. For the historical programs, copy the contents of `examples/demo.mozhi`, `library.mozhi`, `gossip.mozhi`, or `calculator.mozhi` into the editor. Calculator inputs 1, 10, 5, 6 add ten, show it, and exit the menu.

CodeMirror 5.65.13 and Pyodide 0.23.4 load from external CDNs. First loading needs network access. The playground uses plain-text editing, not dedicated Mozhi syntax highlighting. Stop the local server with Ctrl+C. The runtime has no execution budget or Stop button; a nonterminating program can freeze its browser tab.

## Implemented features and differences

| Feature | CLI snapshot | Browser snapshot |
| --- | --- | --- |
| Numbers, strings, booleans, arithmetic, conditions | Present | Present |
| Functions and return | Present | Present |
| Arrays, indexing, push/pop | Present | Present |
| Loops and outer-variable updates | Known scoping bug | Parent-scope fix present |
| Classes and methods | Incomplete; closure handling is broken | Property assignment and methods supported |
| Input | Synchronous `kelu(...)` | Asynchronous `ketukko(...)` |
| Length and conversion | `neelam`, `enn`, `padam`, `vaari` | Same names |
| `podhum` | Exits the CLI process | Prints a message; does not halt execution |

See [LANGUAGE.md](LANGUAGE.md) for the supported syntax and [the documentation source](docs/index.md) for examples. The browser embeds a separate Python interpreter; it does not import `src/mozhi.py`. This preparation keeps both actual stages instead of claiming they are identical.

## Known limitations

- The CLI's child-scope assignment bug can make loops infinite. Its OOP implementation lacks the later property and closure fixes. Use the playground for the four historical examples.
- `**` is recognized after `*` by the tokenizer and fails to parse as exponentiation. Boolean operators evaluate both operands. Indentation/error handling and function argument validation need work.
- Constructors are called manually after `ClassName porul`. Missing properties and invalid numeric input produce runtime errors; the calculator does not guard against division by zero.
- Browser execution blocks the main thread for programs without asynchronous input. Concurrent Run clicks and engine-load failures are not managed robustly.
- No imports/package ecosystem, standard library collection, compatibility guarantee, packaged installer, dedicated highlighter, or official GitHub Linguist recognition is included.

## Documentation

```sh
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
python -m mkdocs build --strict
```

The generated `site/` is ignored. The current docs correct a historical array-pop syntax error and identify runtime-specific behavior; exact original docs remain in the archival commits.

## Roadmap and contributions

First: a shared language specification, bounded execution, runtime regression coverage, and deliberate convergence of CLI/browser behavior. Next: a CLI/REPL package, syntax highlighting and editor integration, then modules and packaging. Official Linguist recognition is a future milestone; `.mozhi` files are not relabeled as Python.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes. The language concept and syntax were directed by the project author; implementation was AI-assisted with Claude, then Gemini and Google Antigravity. These tools assisted development rather than independently originating the author's language idea.

Licensed under [MIT](LICENSE). [HISTORY.md](HISTORY.md) describes the chronology; [PROVENANCE.md](PROVENANCE.md) explains the retrospective commits.
