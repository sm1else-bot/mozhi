# Contributing to Mozhi

Mozhi is an experimental language with deliberately preserved historical implementations. Report which runtime you used: Python CLI or browser playground. Include a minimal `.mozhi` program, expected/actual output, and Python/browser version.

Start with `python -m unittest discover -s tests -v`. Documentation uses `python -m mkdocs build --strict` after installing `requirements-docs.txt`.

Propose syntax changes with their Tamil grammatical rationale and a migration example. Keep interpreter repairs distinct from grammar changes. New behavior needs meaningful regression coverage, especially for scope, OOP, asynchronous input, and termination. Run untrusted or potentially nonterminating programs only with appropriate isolation and bounds.

Do not rewrite archival commits, change recovered source hashes, backdate new work, or add private conversation exports. New work uses its actual commit time. Read PROVENANCE.md before changing historical documentation. Do not change Linguist attributes to disguise `.mozhi` as another language.

No package publication or release automation is configured. Contributions are reviewed before publication. Project code is MIT licensed; externally loaded browser dependencies retain their own licenses.
