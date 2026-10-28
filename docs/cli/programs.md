# Run your first program

First [install Mozhi](../install.md). Save the following UTF-8 text as
`hello.mozhi` in a folder of your choice:

```mozhi
"Vanakkam, world!" sollu
name = "Mozhi" vechukko
"Ithu " kooda name sollu
```

From that folder:

```sh
mozhi check hello.mozhi
mozhi run hello.mozhi
```

The run prints:

```text
Vanakkam, world!
Ithu Mozhi
```

`mozhi hello.mozhi` is equivalent to `mozhi run hello.mozhi`.

## Interactive input

Save this as `greet.mozhi`:

```mozhi
per = kelu("Unga per? ") vechukko
"Vanakkam, " kooda per sollu
```

Run `mozhi run greet.mozhi` and type a name when prompted. `ketukko` is an
identical input alias. Both return strings; convert numeric answers with `enn`
or `padam`. See [input and output](../basics/io.md).

## Pipes and redirects

Input redirection supplies answers to a file program, not its source:

```sh
mozhi run greet.mozhi < answers.txt
mozhi run hello.mozhi > output.txt 2> errors.txt
```

These examples use a POSIX shell. In PowerShell, pipe answers with
`Get-Content answers.txt | mozhi run greet.mozhi`. Prompts are on stdout too,
so they appear in redirected output. Output may be buffered when redirected.
An exhausted input stream is reported as an input error if the program still
expects another answer.

After execution, inspect `$?` in a POSIX shell or `$LASTEXITCODE` in PowerShell.
The [command reference](index.md) lists the exit statuses.

## Working directory and file I/O

Save this as `notes.mozhi`:

```mozhi
# Ithu tharpoathaiya folder-il oru koppai uruvaakkum.
ezhuthu("notes.txt", "Vanakkam!\n")
padi("notes.txt") sollu
```

Running `mozhi run path/to/notes.mozhi` creates `notes.txt` in the shell's
current directory, not in `path/to/`. The parent folder must exist. Use absolute
paths in file built-ins if the destination must be independent of where the
terminal starts. See [standard library](../standard-library.md).

## Execution and stopping

File runs use a fresh environment each time. Variables from a previous run are
not retained. Functions and classes must be defined by that program; imports
and modules are not implemented. Use [the REPL](repl.md) for persistent
interactive experiments.

CLI execution has no ten-second limit. Ctrl+C stops a running file and normally
returns status 130. Programs can change files accessible to your account;
syntax checking does not execute those effects, but execution is not sandboxed.

Continue with [functions](../advanced/functions.md),
[example programs](../examples/cli-programs.md), or
[browser execution](../runtime.md#browser-playground).
