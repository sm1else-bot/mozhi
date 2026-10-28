# Errors and validation

Syntax and runtime failures include the failing statement's source line. For example:

```text
count = 1 vechukko
count / 0 sollu
```

The division reports `[Mozhi] Line 2: division by zero`. A file run prefixes the
source filename, exits with status 1 and prints the diagnostic on stderr without
a Python traceback for handled user errors. The browser displays it in Output
and allows another run. Ctrl+C ends a file run with status 130; in the
[REPL](cli/repl.md), it returns to the prompt instead.

`mozhi check file.mozhi` parses without execution, so this example passes syntax
checking and fails only when run. See [command reference](cli/index.md) for
status 2 (invalid arguments), streams and incomplete REPL input at EOF.

## Indentation and blocks

- An indented block must follow a colon.
- A dedent must match an existing outer indentation level.
- Tabs expand to four columns; mixing tabs and spaces within a single indentation prefix is rejected.
- Blocks still require `mudivu`; indentation alone does not end the construct.
- Strings require a closing quote. Escaped quotes, backslashes, `\n`, and `\t` are supported.

## Calls and objects

Function/method parameter names must be unique. Calls must supply the declared number of arguments. Methods need a first parameter to receive the instance, conventionally `naan`. Builtin input accepts zero or one prompt argument; `neelam`, `enn`, `padam`, and `vaari` each require one argument.

Property reads, property assignments, and method calls require a `porul` object. Missing fields and methods report errors. Initializers are called manually; accessing a field before setting it is an error.

## Arrays and control flow

Indexing and push/pop require a list. Indices must be integers, not booleans, and must be within the list's range. Negative indices follow Python list indexing. Popping an empty list reports an error.

`nillu` and `thodaru` require a loop inside the current function; they cannot escape a called function into its caller's loop. `thirumbu` requires a function or method. `podhum` terminates the whole program, even inside nested calls.

## Input and recovery

Both input aliases return strings. Use `enn` or `padam` for numeric conversion. Invalid conversions, missing CLI input, and division by zero stop the run with a diagnostic; they are not silently converted to zero. Mozhi does not yet offer exception-handling syntax for recovery inside the program.

In the playground, the execution timer pauses while input is pending. Stop cancels that input request. A timeout or Stop restarts the worker; engine-load failures show Retry. See [Running Mozhi](runtime.md) for the remaining execution and sandbox limitations.

## Files and installation

Missing source files, invalid UTF-8, missing file-built-in parent directories and
permission failures produce handled CLI errors. File operations use the current
working directory, not the source file's directory. The browser rejects file
built-ins explicitly. See [standard library](standard-library.md) and
[troubleshooting](troubleshooting.md) for PATH, architecture and package issues.
