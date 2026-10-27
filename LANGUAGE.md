# Mozhi language notes

This describes the current CLI and generated asynchronous browser adapter unless a distinction is stated. It is a working language note, not a complete formal specification.

## Grammar shape

```mozhi
score = 10 vechukko
"Score: " kooda score sollu

score >= 10 na:
    "Ready" sollu
illana:
    "Try again" sollu
mudivu
```

Expressions precede output, return and conditional/loop keywords; assignment combines infix `=` with trailing `vechukko`. Colons, indentation and `mudivu` delimit blocks. Identifiers use ASCII letters, digits and underscore. `#` starts a comment outside strings. Literals include numbers, quoted strings, `true`, `false`, and arrays.

## Loops, functions and arrays

```mozhi
seiy double(x):
    x * 2 thirumbu
mudivu
double(5) sollu

items = [1, 2] vechukko
3 ullapodu items
items veliyapodu
items[0] sollu

i = 0 vechukko
i < 3 varaikum:
    i = i + 1 vechukko
    i sollu
mudivu
```

`nillu` breaks a loop; `thodaru` continues it. Pop is postfix: `items veliyapodu`. Indexed reads are supported; indexed assignment is not implemented. Both adapters update existing variables through the parent scope chain; function and method parameters bind locally.

## Objects

```mozhi
vagai Counter:
    seiy start(naan):
        naan.value = 0 vechukko
    mudivu
    seiy show(naan):
        naan.value sollu
    mudivu
mudivu
c = Counter porul vechukko
c.start()
c.show()
```

The first method parameter receives the instance. Initializer methods are called explicitly, not automatically. Property reads, assignments and method closures work in both adapters. Missing properties and invalid method arguments report errors.

## Builtins and operators

Both adapters support `kelu("Prompt")` and `ketukko("Prompt")` as aliases. Browser input is asynchronously awaited; CLI input is synchronous. Input returns a string. `enn` converts to integer, `padam` to float, `vaari` to string, and `neelam` returns length. `+`/`kooda` concatenate if either operand is a string. `mattrum`, `illaiyal`, `illa` are and/or/not, with short-circuit evaluation of binary operands. They still return `true` or `false`, rather than returning an operand value. Comparison operators and `+ - * / %` are implemented. Exponentiation is right-associative and follows Python precedence: `2 ** 3 ** 2` is `512`, `-2 ** 2` is `-4`, and `2 ** -2` is `0.25`. `podhum` stops the entire current program, including nested calls, in either adapter; it does not kill the reusable browser engine.

Block updates in both adapters search parent environments; new variables are created locally. Function/method parameters bind locally. These are current implementation observations, not a promise of Python semantics.


## Validation and execution controls

Indentation must follow a colon and dedent to an existing block level. Tabs expand to four columns; mixing tabs and spaces in a single indentation prefix is rejected. Function/method parameters must be unique and supplied in the correct count. Methods require an instance parameter. `nillu` and `thodaru` must belong to a loop in the current function; `thirumbu` requires a function or method. Array indices must be integers, not booleans. Errors include the failing statement line.

The playground's worker can be stopped or automatically terminated after its configurable execution budget (10 seconds by default). Input waits pause that budget. The CLI has no execution limit; intentionally endless programs require Ctrl+C or an external timeout. Runtime errors stop the current run and leave the playground ready for another program.
