# Object-Oriented Programming (OOP)

Mozhi supports object-oriented programming, allowing you to define custom data types with classes (`vagai`), methods (`seiy`), and instance properties (`naan.property`).

---

## Class Definitions: `vagai`

Classes represent structures or blueprints in Mozhi.

### Syntax
```text
vagai ClassName:
    # methods are defined here
mudivu
```

### Description
The interpreter registers `ClassName` in the current scope as a `MozhiClass` entity. Each method retains the environment in which the class was defined; its first parameter is bound to the object when called. Method parameters are local and do not overwrite outer variables of the same name.

---

## Object Instantiation: `porul`

To create an instance of a class, use the `porul` ("object") keyword.

### Syntax
```text
object_variable = ClassName porul vechukko
```

---

## Instance Methods and properties

* **`seiy`**: Methods inside classes are declared using the standard function keyword `seiy`.
* **`naan`**: The first parameter of any class method represents the current object instance (equivalent to `self` in Python or `this` in JavaScript). By convention, we name it `naan` ("me/myself").
* **Properties**: Instance fields are assigned inside methods using dot syntax (e.g., `naan.attribute = value vechukko`).
* **Dot Notation**: Attributes and methods are accessed using the dot (`.`) operator (e.g., `instance.method()` or `instance.attribute`).

Initializers are ordinary methods and must be called explicitly after `ClassName porul`. Method parameter names must be unique, a method needs an instance parameter, and calls must supply the declared number of arguments. Missing properties and methods produce line-numbered errors in both adapters.

---

## Code Examples

### Full OOP Definition
This code showcases defining a class, initializing properties, calling methods, and reading properties.

```text
# 1. Define a class
vagai Pusthagam:
    # Initializer method
    seiy thodangu(naan, title, author):
        naan.title = title vechukko
        naan.author = author vechukko
    mudivu

    # Method to describe the book
    seiy vilaku(naan):
        "Book title: " kooda naan.title sollu
        "Author: " kooda naan.author sollu
    mudivu
mudivu

# 2. Instantiate the class
book = Pusthagam porul vechukko

# 3. Call initializer method
book.thodangu("Mozhi Guide", "Jesse")

# 4. Invoke methods
book.vilaku()

# 5. Read properties directly
"Direct Read Title: " kooda book.title sollu
```

---

## Next Steps
* See a complete interactive application using OOP in the [Interactive Calculator](../examples/calculator.md).
