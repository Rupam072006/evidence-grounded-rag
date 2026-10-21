# Pandas Data Cleaning and Text Chunking Boundaries

## Metadata
- **document_id:** DOC-006
- **title:** Pandas Data Cleaning and Text Chunking Boundaries
- **source:** data/documents/pandas_cleaning.md
- **source_type:** engineering_guide
- **version:** 1.0.0
- **created_at:** 2026-01-12T09:00:00Z
- **updated_at:** 2026-01-19T11:30:00Z
- **topic:** Pandas Cleaning

## 1. Overview
Data cleaning transforms noisy, incomplete tabular datasets into reliable formats suitable for modeling and indexing. In retrieval-augmented generation systems, data hygiene pairs with structured document segmentation. To balance semantic granularity with context coherence, the AegisCore chunker enforces a target chunk size of 400 characters and a sliding overlap window of 60 characters across all ingested knowledge documents.

## 2. Main Concepts

### Missing Value Imputation and Removal
Real-world datasets contain missing values represented as `NaN`, `None`, or empty strings.
- **Detection (`isna`, `notna`):** Identifies positions of missing records across columns.
- **Dropping Records (`dropna`):** Removes rows or columns exceeding null tolerance thresholds.
- **Imputation (`fillna`):** Replaces missing entries with statistical values (mean, median, mode) or business constants (e.g., `"UNKNOWN"`).

### Duplicate Record Deduplication
Duplicate records distort statistical analyses and cause redundant passages in vector indices.
- **Identification (`duplicated`):** Flags duplicate rows based on subset column keys.
- **Purging (`drop_duplicates`):** Retains initial or terminal occurrences while dropping duplicates.

### Data Type Casting and Transformation
- **Type Coercion (`astype`):** Converts data types (e.g., casting string dates to `pd.to_datetime` or numerical floats to integers).
- **String Sanitization:** Uses `.str.strip()`, `.str.lower()`, and regular expressions to normalize raw text fields.

### Chunking Strategy and Boundary Mechanics
Documents are segmented along natural paragraph double-newlines and sentence punctuation (`.`, `!`, `?`). The target chunk size is 400 characters, and the sliding overlap window is 60 characters. Each resulting chunk receives a unique, deterministic Chunk ID in the format `[DOCUMENT_ID]-C[SEQUENCE_NUMBER]` (for example, `DOC-006-C001`).

## 3. Explanation of Important Terms
- **Sliding Overlap:** A 60-character buffer retained across consecutive chunks to prevent information fragmentation at boundary cuts.
- **Orphan Fragment Merging:** Chunks smaller than 40 characters are merged into preceding passages to prevent uninformative index vectors.
- **Deterministic Identifier:** A stable chunk identifier derived mathematically from document ID and sequential position.

## 4. Practical Example
```python
import pandas as pd

# Cleaning tabular metadata records
raw_data = {"id": ["DOC-1", "DOC-2", "DOC-2", "DOC-3"], "chunk_size": [400, 400, 400, None]}
df = pd.DataFrame(raw_data)

# Deduplicate and impute missing values
clean_df = df.drop_duplicates(subset=["id"]).copy()
clean_df["chunk_size"] = clean_df["chunk_size"].fillna(400).astype(int)

print(clean_df)
# Output: Exactly 3 unique records with 400 chunk size
```

## 5. Limitations and Common Mistakes
- **Premature Dropping:** Aggressively dropping all rows with any null value (`dropna(how='any')`) can inadvertently purge large portions of usable data.
- **Silent Downcasting:** Converting numeric floats to integer types truncates decimal coordinates without warning.
- **Boundary Fragmentation:** Arbitrary character slicing that ignores sentence boundaries cuts words in half, corrupting semantic embedding quality.

## 6. Source References
- McKinney, W. (2017). *Python for Data Analysis* (2nd ed.). O'Reilly Media.
- Pandas Development Team. *Working with Missing Data*. https://pandas.pydata.org/docs/user_guide/missing_data.html

