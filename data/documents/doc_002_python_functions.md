# Python Functions, Scoping, and Modular Code Structure

## Metadata
- **document_id:** DOC-002
- **title:** Python Functions, Scoping, and Modular Code Structure
- **source:** data/documents/python_functions.md
- **source_type:** programming_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:30:00Z
- **updated_at:** 2026-01-16T09:15:00Z
- **topic:** Python Functions

## 1. Overview
Functions in Python encapsulate reusable blocks of computational logic, promote code modularity, and establish clear operational boundaries. In complex software architectures such as AegisCore, modular functions decompose ingestion, chunking, embedding, vector retrieval, and grounded answer generation into discrete, testable units that maintain complete state isolation.

## 2. Main Concepts

### Defining and Calling Functions
Functions are declared using the `def` keyword, followed by the function identifier, parameter lists enclosed in parentheses, and a colon. Execution occurs when the function is invoked by name with appropriate arguments.

### Parameters, Arguments, and Return Values
- **Positional and Keyword Arguments:** Positional arguments map by sequence; keyword arguments map by parameter name.
- **Default Parameters:** Provide fallback values when an argument is omitted during invocation.
- **Arbitrary Argument Lists:** `*args` captures excess positional arguments as a tuple; `**kwargs` captures keyword arguments as a dictionary.
- **Return Values:** The `return` statement hands computational results back to the caller. Omitting `return` causes the function to return `None`.

### Scope and the LEGB Rule
Variable resolution follows the LEGB hierarchy:
1. **Local (L):** Names defined inside the active function body.
2. **Enclosing (E):** Names defined in enclosing function closures.
3. **Global (G):** Names defined at the module top level.
4. **Built-in (B):** Predefined built-in names (e.g., `len`, `range`, `print`).

## 3. Explanation of Important Terms
- **Pure Function:** A function that produces the same output for identical inputs and causes zero side effects on external state.
- **Closure:** A nested function object that retains bindings to variables in its enclosing lexical scope.
- **Type Hinting:** Annotations (e.g., `def process(text: str) -> list[str]:`) that improve code clarity and enable static type checking.

## 4. Practical Example
```python
from typing import List

def build_chunk_identifiers(document_id: str, count: int) -> List[str]:
    """Generate deterministic chunk IDs for a document."""
    return [f"{document_id}-C{idx:03d}" for idx in range(1, count + 1)]

ids = build_chunk_identifiers("DOC-002", 3)
print(ids)
# Output: ['DOC-002-C001', 'DOC-002-C002', 'DOC-002-C003']
```

## 5. Limitations and Common Mistakes
- **Side Effect Pollution:** Modifying mutable data structures passed as arguments can unexpectedly alter the caller's environment.
- **Late Binding Closures:** Functions created inside loops that reference loop variables bind to the variable's final value, not its value at iteration time.
- **Excessive Function Complexity:** Overloading a single function with multiple responsibilities violates single-responsibility principles.

## 6. Source References
- Python Software Foundation. *Defining Functions*. https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Real Python. *Namespaces and Scope in Python*. https://realpython.com/python-namespaces-scope/

