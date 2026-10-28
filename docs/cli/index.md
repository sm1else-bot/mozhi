# Command-line reference

[Install Mozhi](../install.md), then open a terminal. The same commands are
available through PyPI, Homebrew, native archives and the `.deb`.

| Command | Behavior |
| --- | --- |
| `mozhi --version` | Print `Mozhi 0.1.0` for this release |
| `mozhi --help` | Show command help |
| `mozhi run file.mozhi` | Execute a UTF-8 source file |
| `mozhi file.mozhi` | Shorthand for `run` |
| `mozhi check file.mozhi` | Tokenize and parse without execution |
| `mozhi repl` | Open a persistent interactive session |
| `mozhi --example` | Run the embedded legacy demonstration |

`mozhi` without arguments prints help. `mozhi run --help` and
`mozhi check --help` show command-specific help. Use `--example` by itself.

## Files and arguments

Relative paths resolve from your terminal's working directory; absolute paths
also work. Quote paths containing spaces:

```sh
mozhi run "my programs/hello.mozhi"
mozhi check "my programs/hello.mozhi"
```

Use `mozhi run -- ./-example.mozhi` for a filename that could be interpreted as
an option. The CLI accepts one file and does not pass additional arguments to
Mozhi programs. It has no `-c` option, module/import command, or stdin-source
mode. `mozhi run -` is not an instruction to read program text from stdin.

Python installations also support `python -m mozhi` with the same arguments.
Bundled native installations do not need Python. The repository's
`python src/mozhi.py file.mozhi` launcher remains compatible; unlike the
installed command, it runs the original demonstration without arguments.

## Syntax checking

```sh
mozhi check hello.mozhi
```

A valid file prints `hello.mozhi: syntax OK` and exits with 0. Checking does not
print program output, prompt for input or write program files. It is not a type
checker and cannot prove that runtime names, indices or arithmetic are valid.
For example, `1 / 0 sollu` parses successfully and fails only when run.

## Output and exit status

Program output and input prompts use stdout. Handled errors go to stderr with
the filename and available source statement line. Source files and streams use
UTF-8; a UTF-8 BOM at the beginning of a file is accepted.

| Status | Meaning |
| --- | --- |
| `0` | Successful execution/check; normal REPL exit |
| `1` | Syntax, runtime, source-file or encoding error; incomplete REPL input at EOF |
| `2` | Invalid CLI arguments |
| `130` | Ctrl+C interrupts a file run |

A REPL error normally keeps the session running, and Ctrl+C cancels the current
entry/run rather than exiting. See [REPL behavior](repl.md). `podhum` ends the
current program successfully; it is not a custom process-exit-code mechanism.

There is no built-in CLI execution timeout. The browser's configurable budget
is a separate usability control. See [errors](../errors.md),
[running files and pipes](programs.md), and [troubleshooting](../troubleshooting.md).
