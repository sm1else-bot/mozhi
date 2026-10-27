# Operators

Arithmetic operators are `+`, `-`, `*`, `/`, `%`, and `**`. Division uses Python numeric division. `+` or `kooda` concatenates when either operand is a string.

```text
2 + 3 * 4 sollu
2 ** 3 ** 2 sollu
-2 ** 2 sollu
(-2) ** 2 sollu
2 ** -2 sollu
```

This prints `14`, `512`, `-4`, `4`, and `0.25`, on separate lines. Exponentiation is right-associative. It binds more tightly than a unary sign on its left and allows a signed exponent on its right, following Python's power precedence.

Comparisons are `==`, `!=`, `<`, `>`, `<=`, and `>=`. Write separate comparisons joined by `mattrum` rather than assuming Python-style chained-comparison semantics.

## Logical operators

- `mattrum` means and. The right operand is evaluated only if the left is truthy.
- `illaiyal` means or. The right operand is evaluated only if the left is falsy.
- `illa` means not.

```text
false mattrum (1 / 0) sollu
true illaiyal missing_variable sollu
```

This prints `false` then `true` without evaluating the division or missing variable. The binary logical operators return booleans, not operand values. The CLI and browser use the same rules.
