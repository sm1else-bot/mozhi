# Variables

Mozhi currently has mutable variables; it does not provide a separate constant-declaration construct.

In Mozhi, variables are declared and updated using a trailing assignment style that utilizes the `vechukko` keyword. This corresponds to saying *"keep/store this"* in conversational Tanglish.

---

## The Assignment Keyword: `vechukko`

### Syntax
```text
name = expression vechukko
```

### Description
The interpreter evaluates the `expression` on the right side of the `=` operator and registers the resulting value in the current local scope under the key `name`. 

If `name` is already defined in the local scope or any parent scope (such as outer loops or conditional blocks), the interpreter searches up the parent environment chain and updates the variable in its original scope rather than defining a new local duplicate.

---

## Supported Value Types

Mozhi supports four primary literal types:

| Literal Type | Examples | Description |
| :--- | :--- | :--- |
| **Number** | `10`, `3.14` | Integer and floating-point numeric values. |
| **String** | `"Vanakka-m"`, `'Nanba'` | Character sequences enclosed in single or double quotes. |
| **Boolean** | `true`, `false` | Logical true and false representations. |
| **Arrays (Varisai)** | `[1, 2, 3]` | Ordered list structures. |

---

## Code Examples

### Variable Initialization
```text
# Store a numeric score
marks = 95 vechukko

# Store a string greeting
greeting = "Hello, world!" vechukko

# Store a boolean flag
isValid = true vechukko
```

### Variable Updates
```text
# Updating an existing variable
counter = 0 vechukko
counter = counter + 1 vechukko
```

---

## Next Steps
* Learn how to output variables to the screen in [Input & Output](io.md).
* See how variables control conditions in [Conditionals](../control-flow/conditionals.md).
