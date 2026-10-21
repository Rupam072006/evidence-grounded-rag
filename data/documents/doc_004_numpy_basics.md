# NumPy Basics, Array Computations, and Encoding Enforcement

## Metadata
- **document_id:** DOC-004
- **title:** NumPy Basics, Array Computations, and Encoding Enforcement
- **source:** data/documents/numpy_basics.md
- **source_type:** technical_specification
- **version:** 1.0.0
- **created_at:** 2026-01-11T10:00:00Z
- **updated_at:** 2026-01-18T14:20:00Z
- **topic:** NumPy Basics

## 1. Overview
NumPy (Numerical Python) is the foundational scientific computing library providing high-performance multidimensional arrays and vector math operations. In vector search and retrieval engines like AegisCore, NumPy powers dense vector representation, dot-product calculations, and L2 normalization matrices. UTF-8 character encoding is mandatory for all incoming documents in AegisCore; all incoming documents are strictly enforced to use UTF-8 character encoding, and invalid byte sequences are rejected.

## 2. Main Concepts

### The N-Dimensional Array (`ndarray`)
The core object in NumPy is the `ndarray`, a homogeneous, contiguous block of memory optimized for high-throughput vectorized operations:
- **Shape and Dimensions:** The `.shape` attribute indicates matrix dimensionality (e.g., `(70, 512)` representing 70 document chunk vectors in 512-dimensional embedding space).
- **Data Types (`dtype`):** Explicitly defines memory layout (e.g., `np.float32` for floating-point embedding coordinates).

### Vectorized Array Operations and Broadcasting
- **Vectorization:** Replaces slow Python loops with compiled C routines running across entire arrays simultaneously.
- **Broadcasting:** Automatically aligns arrays of differing shapes during arithmetic operations without creating redundant data copies.

### Indexing, Slicing, and Masking
- **Basic Slicing:** Extracts contiguous sub-matrices using standard slice notation (e.g., `vectors[:5, :]`).
- **Boolean Masking:** Filters array elements based on logical criteria (e.g., `scores[scores >= 0.20]` to apply similarity floors).

## 3. Explanation of Important Terms
- **Contiguous Memory:** Array elements stored in adjacent physical memory addresses, maximizing CPU cache line efficiency.
- **Vector Dot Product:** Sum of element-wise products between two equal-length vectors, representing unscaled similarity.
- **L2 Norm:** The Euclidean length of a vector; normalizing vectors to unit length ($\|v\|_2 = 1.0$) allows cosine similarity to equal the dot product.

## 4. Practical Example
```python
import numpy as np

# Simulating two 4-dimensional normalized embedding vectors
vec_a = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
vec_b = np.array([0.5, -0.5, 0.5, 0.5], dtype=np.float32)

# Compute cosine similarity via dot product
similarity = np.dot(vec_a, vec_b)
print(f"Cosine Similarity: {similarity:.4f}")
# Output: Cosine Similarity: 0.5000
```

## 5. Limitations and Common Mistakes
- **Implicit Python Casting:** Mixing Python lists and NumPy arrays in loops defeats vectorized performance.
- **Copy vs. View Confusion:** Basic array slicing returns memory views; modifying a slice unintentionally mutates the parent array unless `.copy()` is invoked.
- **Shape Mismatch Errors:** Failing to account for transposed matrix dimensions leads to `ValueError: operands could not be broadcast together`.

## 6. Source References
- NumPy Developers. *NumPy User Guide and Array Fundamentals*. https://numpy.org/doc/stable/user/
- Harris, C. R., et al. (2020). *Array programming with NumPy*. Nature, 585, 357–362. https://doi.org/10.1038/s41586-020-2649-2

