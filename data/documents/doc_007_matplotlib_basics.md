# Matplotlib Basics, Data Visualization, and Vector Spaces

## Metadata
- **document_id:** DOC-007
- **title:** Matplotlib Basics, Data Visualization, and Vector Spaces
- **source:** data/documents/matplotlib_basics.md
- **source_type:** technical_specification
- **version:** 1.0.0
- **created_at:** 2026-01-13T08:00:00Z
- **updated_at:** 2026-01-20T09:30:00Z
- **topic:** Matplotlib Basics

## 1. Overview
Matplotlib is the core visualization library in the Python data ecosystem, enabling static, animated, and interactive plotting. Visualizing vector spaces, loss curves, and retrieval metric distributions provides essential insights during system evaluation. In vector search architectures, documents are mapped to geometric vector spaces where all embedding vectors are strictly normalized to unit length (L2 norm = 1.0) so cosine similarity equals vector dot product.

## 2. Main Concepts

### Core Plot Types and Applications
- **Line Plots (`plt.plot`):** Display continuous trends over time (e.g., query latency percentiles across benchmark iterations).
- **Scatter Plots (`plt.scatter`):** Display relationships between two numerical features or two-dimensional projections of embedding vectors (e.g., PCA or t-SNE projections).
- **Bar Charts (`plt.bar`):** Compare discrete categories (e.g., retrieval precision across document topics).
- **Histograms (`plt.hist`):** Visualize frequency distributions of similarity scores across candidate pools.

### Anatomy of a Plot
- **Figure and Axes:** The `Figure` represents the overall canvas, while `Axes` represents the individual coordinate plane containing data points, labels, and ticks.
- **Labels, Titles, and Legends:** `set_xlabel()`, `set_ylabel()`, `set_title()`, and `legend()` ensure plots convey unambiguous context.
- **Color Palettes and Grids:** Grid lines (`plt.grid(True)`) and color choices enhance visual readability and accessibility.

### Vector Space Normalization
In default reproducible environments, AegisCore employs an advanced Sublinear TF-IDF + Character/Word N-Gram hybrid vectorizer producing 512-dimensional representations. All embedding vectors are strictly normalized to unit length (L2 norm = 1.0), which guarantees that the cosine similarity metric reduces directly to an efficient vector dot product.

## 3. Explanation of Important Terms
- **L2 Unit Normalization:** Scaling vector coordinates such that the Euclidean norm $\sqrt{\sum x_i^2} = 1.0$.
- **Dot Product Equivalence:** For unit vectors $u$ and $v$, $\cos(\theta) = \frac{u \cdot v}{\|u\| \|v\|} = u \cdot v$, eliminating division operations during similarity scoring.
- **Subplots (`plt.subplots`):** A helper function creating multiple axes on a single figure for side-by-side comparative visualization.

## 4. Practical Example
```python
import matplotlib.pyplot as plt
import numpy as np

# Plotting similarity distribution
scores = np.array([0.85, 0.72, 0.65, 0.58, 0.42, 0.31, 0.18, 0.09])

plt.figure(figsize=(6, 4))
plt.hist(scores, bins=5, color="skyblue", edgecolor="black")
plt.axvline(0.20, color="red", linestyle="--", label="Sufficiency Floor (0.20)")
plt.title("Candidate Retrieval Scores")
plt.xlabel("Cosine Similarity")
plt.ylabel("Passage Count")
plt.legend()
plt.tight_layout()
# plt.show() saves or displays visual figure
```

## 5. Limitations and Common Mistakes
- **Implicit vs. Explicit API:** Mixing pyplot state-machine calls (`plt.plot()`) with object-oriented axes calls (`ax.plot()`) introduces unexpected plotting state across threads.
- **Unlabeled Axes:** Omitting units or labels produces ambiguous graphs that cannot be interpreted accurately in scientific reports.
- **Overplotting in High Dimensions:** Directly plotting 512-dimensional vectors without dimensionality reduction (PCA or UMAP) yields uninterpretable scatter plots.

## 6. Source References
- Hunter, J. D. (2007). *Matplotlib: A 2D graphics environment*. Computing in Science & Engineering, 9(3), 90–95.
- Matplotlib Development Team. *Matplotlib Documentation*. https://matplotlib.org/stable/index.html

