# Input and Output (I/O)

Both `ketukko` and `kelu` are input aliases in the CLI and browser. Input returns strings in both adapters. The browser waits asynchronously and pauses its execution budget while waiting.

Mozhi provides clean, human-readable keywords to print statements to the screen (`sollu`) and fetch input from the user (`ketukko`).

---

## Output Keyword: `sollu`

### Syntax
```text
expression sollu
```

### Description
The interpreter evaluates the expression and writes its representation followed
by a newline to stdout. Redirected terminal output can be buffered. The browser
streams output through its worker and updates the Output panel in batches.

---

## Input Keyword: `ketukko`

### Syntax
```text
variable_name = ketukko("Prompt Message") vechukko
```

### Description
Calling `ketukko` pauses execution until an answer is available. In the playground:
* It temporarily renders the input container at the bottom of the Output tab.
* The optional argument passed to `ketukko` is printed as log history and sets the text box's placeholder.
* Execution resumes once the user types their input and presses **Enter** on their keyboard or clicks the **Enter** button.

In the CLI, it reads a line from stdin and writes the optional prompt to stdout.
It can read answers from a pipe or redirected file. Both aliases accept zero or
one prompt argument. Exhausted input is an error if another answer is expected.
See [CLI streams and pipes](../cli/programs.md#pipes-and-redirects).

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
# Peyarai ketkalam.
per = ketukko("Enna per? ") vechukko

# Varaverpu sarathai inaikkalam.
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
* Read and write local UTF-8 files with the [standard library](../standard-library.md).
