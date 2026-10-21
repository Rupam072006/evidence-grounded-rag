# Python Exceptions, Error Handling, and Provenance Verification

## Metadata
- **document_id:** DOC-003
- **title:** Python Exceptions, Error Handling, and Provenance Verification
- **source:** data/documents/python_exceptions.md
- **source_type:** engineering_guide
- **version:** 1.0.0
- **created_at:** 2026-01-11T09:00:00Z
- **updated_at:** 2026-01-17T11:00:00Z
- **topic:** Python Exceptions

## 1. Overview
Robust software architectures handle operational anomalies gracefully using structured exception handling. In the AegisCore ingestion pipeline, exceptions intercept missing manifest entries, unreadable files, corrupt payloads, and data tampering. AegisCore performs SHA-256 cryptographic hashing on each document to verify file provenance and detect unauthorized tampering or bitrot before documents are accepted into the knowledge index.

## 2. Main Concepts

### Common Python Exceptions
- **`FileNotFoundError` / `IOError`:** Raised when an ingestion path cannot be located on disk.
- **`ValueError`:** Raised when an argument receives an inappropriate value (e.g., negative token budgets).
- **`KeyError`:** Raised when attempting to access a missing key in a dictionary or metadata mapping.
- **`TypeError`:** Raised when an operation is executed on an incompatible data type.

### The `try`, `except`, `else`, and `finally` Blocks
- **`try`:** Wraps code blocks that may trigger runtime exceptions.
- **`except [ExceptionType]`:** Traps and resolves specific exception classes without terminating the process.
- **`else`:** Executes only when the `try` block completes successfully without raising exceptions.
- **`finally`:** Guaranteed to execute regardless of whether an exception occurred, ensuring resources (such as file handles or database connections) are closed.

### Custom Exception Hierarchies
Enterprise systems define application-specific exceptions inheriting from Python's base `Exception` class (for example, `CorpusError`, `IndexNotFoundError`, and `IngestionValidationError`), enabling precise error classification and structured reporting.

## 3. Explanation of Important Terms
- **Traceback:** The formatted record of active execution stack frames generated when an unhandled exception halts execution.
- **Fail-Fast Principle:** Immediately raising exceptions upon detecting invalid state or cryptographic mismatches rather than propagating corrupted data downstream.
- **Idempotency:** An operation that can be applied multiple times without changing the result beyond the initial execution.

## 4. Practical Example
```python
import hashlib

def verify_document_provenance(filepath: str, expected_sha256: str) -> bool:
    """Verify document integrity using SHA-256 cryptographic hashing."""
    try:
        with open(filepath, "rb") as f:
            calculated_hash = hashlib.sha256(f.read()).hexdigest()
        if calculated_hash != expected_sha256:
            raise ValueError(f"Hash mismatch: computed {calculated_hash} != expected {expected_sha256}")
        return True
    except FileNotFoundError:
        print(f"Error: Target file {filepath} not found.")
        return False
    except ValueError as err:
        print(f"Provenance verification failed: {err}")
        return False
```

## 5. Limitations and Common Mistakes
- **Bare `except:` Clauses:** Catching unqualified `Exception` or bare `except:` suppresses critical system signals like `KeyboardInterrupt` and `SystemExit`.
- **Silent Exception Swallowing:** Catching exceptions with empty `pass` blocks obscures bugs and makes debugging impossible.
- **Improper Exception Chaining:** Raising new exceptions without `from err` loses the original root-cause traceback.

## 6. Source References
- Python Software Foundation. *Errors and Exceptions*. https://docs.python.org/3/tutorial/errors.html
- Python Software Foundation. *Built-in Exceptions*. https://docs.python.org/3/library/exceptions.html

