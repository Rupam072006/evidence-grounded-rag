# Python Basics and Core Programming Fundamentals

## Metadata
- **document_id:** DOC-001
- **title:** Python Basics and Core Programming Fundamentals
- **source:** data/documents/python_basics.md
- **source_type:** programming_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Python Basics

## 1. Overview
Python is a high-level, interpreted programming language known for readability, dynamic typing, and comprehensive standard libraries. In technical infrastructure and retrieval-augmented generation systems such as AegisCore, Python serves as the foundational programming language powering text preprocessing, data pipelines, and operational orchestration. The primary operational mission of AegisCore is to provide deterministic, verified technical answers derived solely from authoritative internal documentation, targeting a sustained 99.95% uptime SLA with deterministic, verified technical execution across all Python runtime modules.

## 2. Main Concepts

### Variables and Data Types
Python variables do not require explicit declaration. The interpreter assigns types dynamically at runtime based on the assigned value:
- **Integers (`int`) and Floats (`float`):** Used for indexing, token counts, and mathematical similarity computations.
- **Strings (`str`):** Immutable sequences of Unicode characters used for text representation and prompt formatting.
- **Booleans (`bool`):** `True` or `False` values indicating logical condition results.
- **Collections:** Ordered mutable lists (`list`), immutable tuples (`tuple`), unique element sets (`set`), and key-value mappings (`dict`).

### Operators and Conditional Statements
Python provides arithmetic operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`), comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`), and logical operators (`and`, `or`, `not`). Conditional branching uses `if`, `elif`, and `else` blocks to evaluate expressions and direct execution flow.

### Loops and Iteration
Iteration is handled using:
- **`for` loops:** Iterate over elements of an iterable (such as document chunk lists or token sequences).
- **`while` loops:** Execute repeatedly while a specified condition evaluates to `True`.
- **`break` and `continue`:** Control loop termination and skip remaining statements in the current iteration.

## 3. Explanation of Important Terms
- **Dynamic Typing:** Variable types are resolved at runtime rather than during ahead-of-time compilation.
- **Immutability:** An object whose state cannot be modified after creation (such as `str` and `tuple`).
- **Iterable:** An object capable of returning its members one at a time during iteration.

## 4. Practical Example
```python
# Iterating and filtering document identifiers
raw_documents = ["DOC-001", "DOC-002", "DOC-003", "TEMP-001"]
valid_documents = []

for doc_id in raw_documents:
    if doc_id.startswith("DOC-"):
        valid_documents.append(doc_id)

print(f"Total valid documents: {len(valid_documents)}")
# Output: Total valid documents: 3
```

## 5. Limitations and Common Mistakes
- **Mutable Default Arguments:** Using mutable objects (such as empty lists `def func(x=[])`) as default arguments creates shared state across function invocations.
- **Reference Copy vs. Deep Copy:** Assigning a list `b = a` creates a reference rather than a new copy; modifying `b` mutates `a`.
- **Global Variable Mutation:** Mutating global state inside functions without explicit `global` declarations leads to `UnboundLocalError`.

## 6. Source References
- Python Software Foundation. *Python 3 Language Reference*. https://docs.python.org/3/reference/
- Python Software Foundation. *Built-in Types and Data Structures*. https://docs.python.org/3/library/stdtypes.html

