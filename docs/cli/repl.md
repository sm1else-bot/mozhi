# Interactive REPL

Start a session with:

```sh
mozhi repl
```

The prompt is `mozhi> `. Type one entry at a time. Assignments and function or
class definitions remain available until the session ends. Bare expressions
show their value; file programs need `sollu` for explicit output.

```text
mozhi> count = 5 vechukko
mozhi> count + 1
6
mozhi> "Vanakkam!" sollu
Vanakkam!
```

## Multiline blocks

The `... ` prompt means more input is needed. Indent block bodies and close
with `mudivu`, just as in a file:

```text
mozhi> seiy double(x):
...     x * 2 thirumbu
... mudivu
mozhi> double(6)
12
```

Blank lines do not replace `mudivu`. Nested loops, conditions and methods each
need their own terminator. Closing a complete block executes it immediately.
See [functions](../advanced/functions.md) and [loops](../control-flow/loops.md).

## Recovery and stopping

Syntax and runtime errors are printed on stderr with `<repl>` as the filename.
The session continues with its previous environment. Changes already executed
before an error are retained; entries do not run inside transactions.

Ctrl+C cancels pending input or interrupts a running entry and returns to the
prompt. It does not clear previously defined variables. This differs from a
file run, where Ctrl+C ends the process with status 130.

`podhum` ends the current entry's program; it does not close the REPL.
There is no REPL execution timeout. Ctrl+C is the way to interrupt a runaway
entry when the terminal can deliver the interrupt.

## Ending a session

At a fresh prompt, enter `quit`, `exit`, `:quit` or `:exit`. EOF also exits:
Ctrl+D on many Unix terminals, or Ctrl+Z followed by Enter on Windows. Terminal
bindings can vary.

EOF during an unfinished block reports incomplete input and returns status 1;
a normal exit returns 0. Interactive errors alone do not force a nonzero process
status when the session later exits normally.

Sessions are in memory. Mozhi does not currently provide persistent REPL history,
auto-completion, a save-session command, or automatic loading of a startup file.
Save reusable work in `.mozhi` files and [run it from the CLI](programs.md).
