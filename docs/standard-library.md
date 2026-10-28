# Standard library foundations

The CLI and Pyodide adapter use the same parser, AST, environments, functions,
arrays and runtime implementation. These built-ins extend existing arithmetic,
string concatenation and array push/pop/indexing without changing syntax.

| Built-in | Arguments and result |
| --- | --- |
| `kelu(prompt)` / `ketukko(prompt)` | Optional prompt, returns an input string; both spellings remain aliases |
| `neelam(value)` | Length of a string or array |
| `enn(value)` | Integer conversion |
| `padam(value)` | Floating-point conversion |
| `vaari(value)` | String conversion, preserving existing behavior |
| `ver(number)` | Square root; negative real inputs report an error |
| `pirithu(text, separator)` | Split a string into an array of strings |
| `inaithu(array, separator)` | Join an array of strings |
| `maatru(text, old, new)` | Replace all matching substrings |
| `neram()` | Monotonic elapsed-time clock in seconds; subtract two readings for benchmarks |
| `seeratra()` | Pseudorandom float in `[0, 1)` |
| `seeratra(low, high)` | Pseudorandom integer, inclusive bounds; one argument is invalid |
| `padi(path)` | Read an entire UTF-8 file |
| `ezhuthu(path, text)` | Write UTF-8 text, replacing an existing file |
| `serthu_ezhuthu(path, text)` | Append UTF-8 text |

Arguments are ordinary function-call arguments. Built-ins retain their existing
priority over user-defined functions with the same name. Invalid arity/types and
file errors are reported with the calling statement line. Random values are not
cryptographic. `neram()` has an unspecified origin, not a calendar timestamp.

```mozhi
# Sarangalai pirithu marubadiyum inaikkalam.
words = pirithu("vanakkam,nanba", ",") vechukko
inaithu(words, " ") sollu
```

File paths resolve against the process working directory, not automatically
against the source file's directory. Parent directories must already exist.
Writing returns no value. These functions can access files permitted to the
local user and are not sandboxed.

```mozhi
# Ithu ulloor CLI-il odum.
ezhuthu("notes.txt", "வணக்கம்\n")
serthu_ezhuthu("notes.txt", "Mozhi\n")
padi("notes.txt") sollu
```

The browser explicitly rejects `padi`, `ezhuthu` and `serthu_ezhuthu`: it does not
expose the host filesystem. The existing input adapter remains asynchronous and
the worker's execution budget still applies. Other deterministic built-ins are
checked against both adapters, including actual Pyodide browser execution.

The [CLI example guide](examples/cli-programs.md) links the runnable sources,
expected outputs and download instructions. Examples include `hello_world.mozhi`, `fibonacci.mozhi`,
`arrays_loops.mozhi`, `recursion.mozhi`, `file_io.mozhi`, `benchmark.mozhi`,
`long_running.mozhi`, and `standard_library.mozhi`. Existing examples remain.
The long-running example intentionally exceeds the browser's default 10-second
limit; run it locally or raise that browser limit. Neural-network, attention,
and MozhiBERT examples were not present in this checkout and are not fabricated.

Use [Installation](install.md) to obtain the local interpreter and
[CLI file execution](cli/programs.md#working-directory-and-file-io) for path
and filesystem behavior. `mozhi check` does not execute built-ins.
