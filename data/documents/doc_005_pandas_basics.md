# Pandas Basics, Tabular Data Structures, and Text Sanitization

## Metadata
- **document_id:** DOC-005
- **title:** Pandas Basics, Tabular Data Structures, and Text Sanitization
- **source:** data/documents/pandas_basics.md
- **source_type:** security_standard
- **version:** 1.0.0
- **created_at:** 2026-01-12T08:00:00Z
- **updated_at:** 2026-01-19T10:00:00Z
- **topic:** Pandas Basics

## 1. Overview
Pandas is a data manipulation and analysis library built on NumPy, providing flexible tabular data structures. In retrieval systems and data engineering workflows, pandas inspects document catalogs, verifies manifest schemas, and tabulates benchmark evaluation metrics. Before storing or chunking document corpora, raw text undergoes rigorous multi-stage cleaning: the four sequential stages of the text cleaning pipeline are Unicode Normalization, Control Character Removal, Whitespace Consolidation, and Security Tag Stripping.

## 2. Main Concepts

### Series and DataFrames
- **Series:** A one-dimensional labeled array capable of holding any data type (integers, strings, floating-point numbers).
- **DataFrame:** A two-dimensional, size-mutable tabular data structure with labeled axes (rows and columns), analogous to a database table or spreadsheet.

### Ingestion and Inspection
- **Loading Data (`pd.read_csv`):** Reads delimited tabular files into DataFrame structures with automated type inference.
- **Inspection Methods:**
  - `df.head(n)` / `df.tail(n)`: Preview initial or terminal rows.
  - `df.info()`: Displays non-null counts, column data types, and memory consumption.
  - `df.describe()`: Computes summary statistics (count, mean, standard deviation, quartiles).

### Filtering and Selection
- **Label-Based Indexing (`.loc`):** Accesses rows and columns by name or boolean conditions.
- **Positional Indexing (`.iloc`):** Accesses rows and columns by integer positions (0-indexed).
- **Boolean Masking:** Subsets records satisfying criteria (e.g., `df[df['score'] >= 0.20]`).

## 3. Explanation of Important Terms
- **Index:** Immutable sequence of row identifiers supporting alignment and fast label lookups.
- **Unicode Normalization (NFKC):** Stage 1 of text cleaning; standardizes decomposed characters and ligatures into canonical compatibility forms.
- **Security Tag Stripping:** Stage 4 of text cleaning; sanitizes HTML and executable script injection tags (`<script>`, `<iframe>`) from untrusted text.

## 4. Practical Example
```python
import pandas as pd

# Creating a document manifest DataFrame
data = {
    "document_id": ["DOC-001", "DOC-002", "DOC-003"],
    "topic": ["Overview", "Architecture", "Ingestion"],
    "verified": [True, True, True]
}
df = pd.DataFrame(data)

# Filter verified documents
verified_docs = df.loc[df["verified"] == True, ["document_id", "topic"]]
print(verified_docs)
```

## 5. Limitations and Common Mistakes
- **`SettingWithCopyWarning`:** Chained indexing (`df['col'][0] = val`) creates ambiguity about modifying a view versus a copy; always use `.loc` for assignment.
- **Memory Overhead:** Object-dtype columns storing Python strings incur high memory overhead compared to typed categorical or string arrays.
- **In-Place Mutation Misconceptions:** Many pandas operations return new DataFrames rather than mutating in place unless `inplace=True` is provided.

## 6. Source References
- McKinney, W. (2010). *Data Structures for Statistical Computing in Python*. Proceedings of the 9th Python in Science Conference, 56–61.
- Pandas Development Team. *Pandas Documentation*. https://pandas.pydata.org/docs/

