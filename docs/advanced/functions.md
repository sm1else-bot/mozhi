# Functions

Define a function with `seiy`, parameters in parentheses, an indented body and
`mudivu`. Return an expression with trailing `thirumbu`:

```mozhi
seiy double(x):
    x * 2 thirumbu
mudivu

double(7) sollu
```

This prints `14`. Functions without an executed return expression produce no
value. Parameter names must be unique and calls must supply the exact declared
argument count. Default arguments, keyword arguments and variadic parameters
are not implemented.

## Recursion

```mozhi
seiy factorial(n):
    n <= 1 na:
        1 thirumbu
    mudivu
    n * factorial(n - 1) thirumbu
mudivu

factorial(6) sollu
```

This prints `720`. Recursion uses the host interpreter's call stack; there is
no promise of unlimited depth or tail-call optimization.

## Scope

Parameters bind locally and can shadow an outer variable. Assignment to an
already defined non-parameter variable searches enclosing environments and
updates its defining scope. A new name is local to the environment where it is
created. Functions retain their defining environment.

```mozhi
count = 0 vechukko
seiy bump():
    count = count + 1 vechukko
mudivu
bump()
count sollu
```

This prints `1`. `thirumbu` is valid only in functions and methods. A function
called from a loop cannot use `nillu` or `thodaru` to break or continue the
caller's loop. `podhum` stops the whole current program, including nested calls.

See [methods and objects](oop.md), [standard built-ins](../standard-library.md),
[CLI examples](../examples/cli-programs.md) and the [REPL](../cli/repl.md).
