# CLI example programs

The examples live in the repository, not in the current directory after a wheel
or native install. Clone the source or download individual `.mozhi` files from
[the examples directory](https://github.com/sm1else-bot/mozhi/tree/main/examples).

From a checkout:

```sh
mozhi check examples/fibonacci.mozhi
mozhi run examples/fibonacci.mozhi
```

Without a checkout, download a program and run that file:

```sh
curl -fLO https://raw.githubusercontent.com/sm1else-bot/mozhi/main/examples/fibonacci.mozhi
mozhi run fibonacci.mozhi
```

## Small programs

| File | Demonstrates | Expected result |
| --- | --- | --- |
| `hello_world.mozhi` | Output | A greeting |
| `fibonacci.mozhi` | Loops and arithmetic | `55` |
| `arrays_loops.mozhi` | Array indexing and iteration | `20` |
| `recursion.mozhi` | Recursive factorial | `720` |
| `standard_library.mozhi` | Split/join, replacement, square root and random numbers | Includes `9.0` and `7`; equal random bounds make this example deterministic |
| `file_io.mozhi` | UTF-8 write, append and read | Creates `mozhi-example.txt` in the working directory |
| `benchmark.mozhi` | A sum and elapsed time | Sum `49995000`; duration varies |
| `long_running.mozhi` | Local execution beyond the browser's default limit | Runs for about 11 seconds, then prints `Mudinthathu` |

The long-running example has no CLI timeout. In the browser, raise the execution
limit above its duration. File I/O is local-only and is rejected in the browser.

## Preserved examples

`demo.mozhi`, `gossip.mozhi`, `library.mozhi` and `calculator.mozhi` remain in the
source checkout. [The calculator walkthrough](calculator.md) includes a complete
program and input sequence. The browser's [program gallery](https://projects.jessenth.com/mozhi/examples/)
contains its curated selection; it is not the entire CLI example collection.

There are no neural-network, attention or MozhiBERT example programs in this
release. See [functions](../advanced/functions.md), [arrays](../advanced/arrays.md),
and the [command reference](../cli/index.md) for the supported language.
