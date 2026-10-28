# Mozhi documentation

> These examples run in the current CLI and browser adapters. Both input spellings, `kelu` and `ketukko`, are supported. See the repository README and LANGUAGE.md for execution controls and current limitations.

## Start here

| Task | Guide |
| --- | --- |
| Install with `.deb`, Homebrew, PyPI or native archive | [Installation](install.md) |
| Create and run a UTF-8 program | [First program](cli/programs.md) |
| Look up commands, streams and exit statuses | [CLI reference](cli/index.md) |
| Experiment interactively | [REPL](cli/repl.md) |
| Find runnable local programs | [CLI examples](examples/cli-programs.md) |
| Resolve an install or execution problem | [Troubleshooting](troubleshooting.md) |

See [Running Mozhi](runtime.md) for browser controls, [Operators](basics/operators.md)
for precedence and short-circuit rules, and [Errors](errors.md) for diagnostics.

Mozhi is an experimental programming language with Tamil-inspired, verb-final syntax. These pages explain the language, show working programs, and document its current limits. Studio contains the interactive lessons; Learn is the full language guide.

**Historical note:** The early repository commits are retrospective archival reconstructions from recovered development records. They are not original commits made on those dates. The repository's PROVENANCE.md explains the evidence and method.

---

## Language Philosophy

Most programming languages use English structures. Mozhi breaks this convention by incorporating:

* **Natural Declarations**: Stating variables using `vechukko` ("keep this").
* **Colloquial Control Flow**: Evaluating decisions using `na` ("if") and loops using `varaikum` ("until").
* **Object-Oriented Idioms**: Designing models with `vagai` ("class") and creating instances with `porul` ("object").

---

## Quick Tour

To get started, check out the core sections of the documentation:

### [1. Basics](basics/variables.md)
Learn how to define variables with `vechukko`, output strings with `sollu`, and accept inputs dynamically with `ketukko`.

### [2. Control Flow](control-flow/conditionals.md)
Discover loops (`varaikum`) and conditionals (`na` / `illana`) to make programs make decisions.

### [3. Advanced OOP & Arrays](advanced/oop.md)
Learn classes (`vagai`), instantiation (`porul`), instance attributes (`naan.property`), and array literals such as `[1, 2, 3]`.

### [4. Functions](advanced/functions.md)
Define reusable functions with `seiy`, return with `thirumbu`, and use recursion.
The [standard library](standard-library.md) covers conversion, strings, timing,
randomness and local file operations.

---

## Example Snippet

Here is a quick overview of what Mozhi looks like:

```text
# Oru siriya varaverpu.
name = ketukko("Enna per? ") vechukko
greeting = "Vanakkam, " kooda name vechukko
greeting sollu
```
