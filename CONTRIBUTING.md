# Contributing to Mozhi

Mozhi is an experimental language with deliberately preserved historical implementations. Report which runtime you used: Python CLI or browser playground. Include a minimal `.mozhi` program, expected/actual output, and Python/browser version.

After core changes run `python tools/sync_playground.py`, then `python -m unittest discover -s tests -v`. The browser engine is generated; edit the core and generator adapter instead of editing that artifact by hand. Optional worker/UI integration checks use `npm ci`, `npx playwright install chromium`, then `npm run test:browser` and `npm run test:studio`. The studio suite exercises lessons, persistence, file and link sharing, diagnostics, and mobile controls. Playground lesson and reference content lives in `playground/content.js`; interface behavior and styles live in `playground/app.js` and `playground/studio.css`. Documentation uses `python -m mkdocs build --strict` after installing `requirements-docs.txt`.

Build the combined website with `python tools/build_site.py`, then run `npm run test:site` to check Studio/Learn/Examples navigation, nested documentation links, mobile search, and hosting under a repository URL prefix. The MkDocs theme overrides are in `docs/overrides/` and `docs/stylesheets/studio.css`. Preview with `python -m http.server 8000 --directory site`; rebuild after source changes.

Run `python tools/check_docs.py` after building to validate Markdown paths,
generated navigation/fragment targets and explicitly runnable `mozhi` fences.
Use `text` fences for syntax templates with placeholders. Installation lives in
`docs/install.md`, terminal behavior in `docs/cli/`, and browser controls in
`docs/runtime.md`. Keep examples, command names, exits and package availability
consistent with the shipped version. Runnable example comments use Tanglish.

The public `.deb` is a GitHub Release download, not an official APT archive
entry. Its separate `.sha256` receipt was appended without replacing the initial
`SHA256SUMS`. The manual `verify-deb.yml` workflow tests public downloads in
clean Ubuntu/Debian containers. Never test system installation/removal on a
personal host when a disposable runner is available.

Propose syntax changes with their Tamil grammatical rationale and a migration example. Keep interpreter repairs distinct from grammar changes. New behavior needs meaningful regression coverage, especially for scope, OOP, asynchronous input, and termination. Run untrusted or potentially nonterminating programs only with appropriate isolation and bounds.

Do not rewrite archival commits, change recovered source hashes, backdate new work, or add private conversation exports. New work uses its actual commit time. Read PROVENANCE.md before changing historical documentation. Do not change Linguist attributes to disguise `.mozhi` as another language.

Native builds and release preparation are automated; publication requires explicit maintainer approval. See docs/distribution.md for the checklist and external registry steps. Edit src/mozhi/core.py for language behavior, src/mozhi/cli.py for terminal adapters, and src/mozhi/_version.py for the single version. Run tests with requirements-build.txt installed to include package-manager validation. Project code is MIT licensed; externally loaded browser dependencies retain their own licenses.
