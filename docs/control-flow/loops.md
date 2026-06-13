# Loops (varaikum)

Mozhi supports loop iteration using the `varaikum` ("until/while") block. This runs statements repeatedly as long as a condition holds true.

---

## Iteration Block: `varaikum`

### Syntax
```text
condition varaikum:
    # statements to repeat
mudivu
```

### Description
The interpreter evaluates the `condition` on each iteration:
1. If the condition is truthy, a new child environment block is created, and the body executes.
2. If `nillu` ("break") is encountered, iteration terminates immediately.
3. If `thodaru` ("continue") is encountered, the current iteration halts, and execution jumps back to evaluate the condition again.
4. Any variable assignments to outer variables (like `i = i + 1 vechukko`) correctly bubble up to update the original variable in the parent scope.

---

## Loop Controls: `nillu` & `thodaru`

* **`nillu`**: Immediately exits the loop.
* **`thodaru`**: Skips the rest of the current loop iteration and proceeds to the next check.

---

## Code Examples

### Simple Counter Loop
```text
i = 1 vechukko
i <= 3 varaikum:
    "Val: " kooda i sollu
    i = i + 1 vechukko
mudivu
```

### Loop with Break (`nillu`)
```text
# Run infinitely until broken
running = true vechukko
i = 1 vechukko

running varaikum:
    i sollu
    i == 3 na:
        nillu
    mudivu
    i = i + 1 vechukko
mudivu
```

### Loop with Continue (`thodaru`)
```text
i = 0 vechukko
i < 5 varaikum:
    i = i + 1 vechukko
    
    # Skip printing 3
    i == 3 na:
        thodaru
    mudivu
    
    i sollu
mudivu
```

---

## Next Steps
* Learn to group variables in [Arrays (Varisai)](../advanced/arrays.md).
* Structure complex objects using [Object-Oriented Programming (OOP)](../advanced/oop.md).
