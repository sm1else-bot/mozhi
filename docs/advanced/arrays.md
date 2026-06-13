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

#### Syntax
```text
veliyapodu array_variable
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
veliyapodu scores

# Prints [100, 200]
scores sollu
```

---

## Next Steps
* Create structures and classes with [Object-Oriented Programming (OOP)](oop.md).
* Walk through a complete app example in the [Interactive Calculator](../examples/calculator.md).
