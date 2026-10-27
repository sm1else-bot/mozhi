# Mozhi language notes

This describes the preserved browser runtime unless a CLI distinction is stated. It is a working language note, not a complete formal specification.

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

`nillu` breaks a loop; `thodaru` continues it. Pop is postfix: `items veliyapodu`. Indexed reads are supported; indexed assignment is not implemented. The CLI's scope bug can make the loop above nonterminating; use the browser for loop examples until it is repaired.

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

The first method parameter receives the instance. Initializer methods are called explicitly, not automatically. Browser property reads/assignments work; the earlier CLI lacks those fixes.

## Builtins and operators

Browser input is `ketukko("Prompt")`; CLI input is `kelu("Prompt")`. Input returns a string. `enn` converts to integer, `padam` to float, `vaari` to string, and `neelam` returns length. `+`/`kooda` concatenate if either operand is a string. `mattrum`, `illaiyal`, `illa` are and/or/not, with eager evaluation of binary operands. Comparison operators and `+ - * / %` are implemented. Exponentiation currently fails tokenization. `podhum` exits the CLI process but only logs a message in the browser.

Block updates in the browser search parent environments; new variables are created locally. Function/method parameters bind locally. These are current implementation observations, not a promise of Python semantics.
