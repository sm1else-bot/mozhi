# Conditionals (na / illana)

Mozhi supports decision-making branch execution using the `na` ("if") and `illana` ("else") block structure, closed by the `mudivu` ("end") keyword.

---

## The Decision Block: `na` / `illana` / `mudivu`

### Syntax
```text
condition na:
    # block executes if condition is true
illana:
    # block executes if condition is false
mudivu
```

### Description
1. The interpreter evaluates the `condition` expression. 
2. A value is considered **truthy** if it is not `None`, `False`, `0`, `0.0`, `""` (empty string), or `[]` (empty list).
3. If truthy, the body block under `na:` is executed. It runs inside a block-scoped environment. Any variables updated inside this block that are already defined in the outer scope will mutate the outer variables.
4. If falsy and an `illana:` branch is present, the else body runs in its own child block scope.
5. The block ends with the keyword `mudivu`.

---

## Comparison Operators

Mozhi supports standard comparison operators:

* `==` (equals)
* `!=` (does not equal)
* `<` (less than)
* `>` (greater than)
* `<=` (less than or equal to)
* `>=` (greater than or equal to)

---

## Code Examples

### Simple If Branch
```text
age = 20 vechukko

age >= 18 na:
    "Apply pannalam!" sollu
mudivu
```

### If-Else Branch
```text
choice = ketukko("1 or 2? ") vechukko
choice = enn(choice) vechukko

choice == 1 na:
    "Option 1 selected!" sollu
illana:
    "Option 2 (or other) selected!" sollu
mudivu
```

### Nested Conditionals
```text
val = 10 vechukko

val > 5 na:
    val == 10 na:
        "Double jackpot!" sollu
    illana:
        "Jackpot!" sollu
    mudivu
mudivu
```

---

## Next Steps
* Learn how to repeat instructions using [Loops](loops.md).
* Explore list variables in [Arrays (Varisai)](../advanced/arrays.md).
