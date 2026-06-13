# Input and Output (I/O)

Mozhi provides clean, human-readable keywords to print statements to the screen (`sollu`) and fetch input from the user (`ketukko`).

---

## Output Keyword: `sollu`

### Syntax
```text
expression sollu
```

### Description
The interpreter evaluates the `expression` and immediately flushes the string representation to standard output (or appends it directly to the playground screen in real-time).

---

## Input Keyword: `ketukko`

### Syntax
```text
variable_name = ketukko("Prompt Message") vechukko
```

### Description
Calling `ketukko` pauses execution and displays an interactive input text box. In the playground:
* It temporarily renders the input container at the bottom of the Output tab.
* The optional argument passed to `ketukko` is printed as log history and sets the text box's placeholder.
* Execution resumes once the user types their input and presses **Enter** on their keyboard or clicks the **Enter** button.

---

## String Concatenation: `kooda`

To join strings, use the `kooda` keyword (or the `+` operator).

### Syntax
```text
string1 kooda string2
```

---

## Code Examples

### Standard Printing
```text
"Mozhi programming language-ku varaverkirom!" sollu
```

### Prompting and Printing Inputs
```text
# Prompt the user for their name
per = ketukko("Enna per? ") vechukko

# Greet the user by joining strings
message = "Varaverkirom, " kooda per vechukko
message sollu
```

### Printing Numbers
```text
score = 100 vechukko
"Score: " kooda score sollu
```

---

## Next Steps
* Add decision logic with [Conditionals](../control-flow/conditionals.md).
* Repeat operations with [Loops](../control-flow/loops.md).
