# Example: Interactive Calculator

This example demonstrates a complete, interactive terminal-based Calculator app built in Mozhi. It showcases variables, custom classes (`vagai`), instance methods (`seiy`), while loops (`varaikum`), conditionals (`na`/`illana`), and interactive user input (`ketukko`).

---

## The Calculator Code

From the repository root, run `python src/mozhi.py examples/calculator.mozhi`, or paste the following code into the playground and click **Run Mozhi**. The input sequence `1`, `10`, `5`, `6` adds ten, shows the total, and exits the menu.

```text
# A simple Calculator in Mozhi

vagai Calculator:
    seiy initialize(ennoda):
        ennoda.total = 0 vechukko
    mudivu

    seiy add(ennoda, val):
        ennoda.total = ennoda.total + val vechukko
    mudivu

    seiy subtract(ennoda, val):
        ennoda.total = ennoda.total - val vechukko
    mudivu

    seiy multiply(ennoda, val):
        ennoda.total = ennoda.total * val vechukko
    mudivu

    seiy divide(ennoda, val):
        ennoda.total = ennoda.total / val vechukko
    mudivu

    seiy show(ennoda):
        "Ippo total: " kooda ennoda.total sollu
    mudivu
mudivu

# Main Program Execution
calc = Calculator porul vechukko
calc.initialize()

"Mozhi Calculator Ready!" sollu
"1. Add, 2. Subtract, 3. Multiply, 4. Divide, 5. Show, 6. Podhum" sollu

running = true vechukko
running varaikum:
    choice = ketukko("Enna operation? ") vechukko
    choice = enn(choice) vechukko

    choice == 1 na:
        val = ketukko("Amount? ") vechukko
        calc.add(enn(val))
    illana:
        choice == 2 na:
            val = ketukko("Amount? ") vechukko
            calc.subtract(enn(val))
        illana:
            choice == 3 na:
                val = ketukko("Amount? ") vechukko
                calc.multiply(enn(val))
            illana:
                choice == 4 na:
                    val = ketukko("Amount? ") vechukko
                    calc.divide(enn(val))
                illana:
                    choice == 5 na:
                        calc.show()
                    illana:
                        choice == 6 na:
                            running = false vechukko
                        mudivu
                    mudivu
                mudivu
            mudivu
        mudivu
    mudivu
mudivu

"Bye!" sollu
podhum
```

---

## How it Works

### 1. Blueprint Definition (`vagai`)
The calculator logic is encapsulated inside `vagai Calculator`. It defines mathematical operations (`add`, `subtract`, `multiply`, `divide`) and updates the internal state variable `ennoda.total` (where `ennoda` serves as the `self` reference).

### 2. State Initialization (`porul`)
We create a new instance of the Calculator blueprint using `calc = Calculator porul vechukko`. We then initialize the total value to `0` by calling `calc.initialize()`.

### 3. Loop Iteration (`varaikum`)
The menu remains active inside `running varaikum:`. The loop runs continuously until the user enters `6` ("Podhum"), which sets `running = false vechukko` and terminates iteration on the next check.

### 4. Interactive Prompts (`ketukko`)
The program prompts for selections and operands using `ketukko`. The inputs are returned as strings, which are then explicitly cast to numbers using the `enn()` builtin function so that addition is performed arithmetically instead of concatenating strings.

`kelu` is an equivalent input alias. Browser input waits pause the execution timer; use Enter or the input button to resume. The example does not validate menu choices, catch invalid numeric conversions, or prevent division by zero. Those failures stop the run with a line-numbered error; correct the input and start a new run. The final `podhum` ends the program in either adapter.
