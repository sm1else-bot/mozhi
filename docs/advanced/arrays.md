# Arrays (Varisai)

In Mozhi, lists are referred to as a **Varisai** (array). They store ordered lists of variables and support dynamic indexing, appends, and pops.

---

## Array Definition & Indexing

### Syntax
```text
# Literal definition
arr = [val1, val2, val3] vechukko

# Accessing an element (0-indexed)
item = arr[0] vechukko
```

### Description
Arrays are 0-indexed sequences. The interpreter stores them internally as Python lists, meaning they support arbitrary value types (including nested arrays or objects).

Use `neelam(arr)` for length. Negative indices count from the end; indices must
be integers, not booleans, and within bounds. Indexed assignment such as
`arr[0] = 5 vechukko` is not implemented.

---

## Modifying Arrays: `ullapodu` and `veliyapodu`

Mozhi includes dedicated statements to push to and pop from arrays.

### 1. Pushing: `ullapodu` (Push)
Appends a value to the end of the list.

#### Syntax
```text
value ullapodu array_variable
```

### 2. Popping: `veliyapodu` (Pop)
Removes the last element from the list.

Pop is a statement, not a value-returning expression. Popping an empty array
reports an error. Both operations mutate the existing array.

#### Syntax
```text
array_variable veliyapodu
```

---

## Code Examples

### Defining and Printing Arrays
```text
numbers = [10, 20, 30] vechukko
"Array elements: " kooda numbers sollu
```

### Dynamic Appends (`ullapodu`)
```text
fruits = ["Apple", "Banana"] vechukko

# Add a fruit
"Orange" ullapodu fruits

# Prints ["Apple", "Banana", "Orange"]
fruits sollu
```

### Dynamic Pops (`veliyapodu`)
```text
scores = [100, 200, 300] vechukko

# Remove the last item (300)
scores veliyapodu

# Prints [100, 200]
scores sollu
```

---

## Next Steps
* Create structures and classes with [Object-Oriented Programming (OOP)](oop.md).
* Walk through a complete app example in the [Interactive Calculator](../examples/calculator.md).
* Run `arrays_loops.mozhi` from the [CLI example collection](../examples/cli-programs.md).
