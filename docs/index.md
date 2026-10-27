# A little Tamil. A lot to build.

> These examples run in the current CLI and browser adapters. Both input spellings, `kelu` and `ketukko`, are supported. See the repository README and LANGUAGE.md for execution controls and current limitations.

Start with [Running Mozhi](runtime.md) for CLI commands and playground controls. See [Operators](basics/operators.md) for exponentiation and short-circuit rules, and [Errors and validation](errors.md) for diagnostics and recovery.

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
Learn classes (`vagai`), instantiation (`porul`), instance attributes (`naan.property`), and lists (`varisai`).

---

## Example Snippet

Here is a quick overview of what Mozhi looks like:

```text
# Simple greeter in Mozhi
name = ketukko("Enna per? ") vechukko
greeting = "Vanakkam, " kooda name vechukko
greeting sollu
```
