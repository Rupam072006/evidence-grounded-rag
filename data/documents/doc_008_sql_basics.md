# SQL Basics, Relational Queries, and Persistent Storage Layout

## Metadata
- **document_id:** DOC-008
- **title:** SQL Basics, Relational Queries, and Persistent Storage Layout
- **source:** data/documents/sql_basics.md
- **source_type:** engineering_guide
- **version:** 1.0.0
- **created_at:** 2026-01-13T09:00:00Z
- **updated_at:** 2026-01-20T10:45:00Z
- **topic:** SQL Basics

## 1. Overview
Structured Query Language (SQL) is the international standard for defining, querying, and managing data held in relational database management systems. In knowledge retrieval platforms, relational principles guide persistent catalog schemas, metadata indexing, and query evaluation. AegisCore maintains a persistent storage layout comprising exactly two files: the Vector Matrix (`vectors.npy`) and the Knowledge Index Metadata (`knowledge_index.json`).

## 2. Main Concepts

### Basic Query Structure
A standard SQL query retrieves specified columns from one or more tables:
- **`SELECT`:** Designates attributes or computational expressions to return.
- **`FROM`:** Identifies target database tables or views.
- **`WHERE`:** Filters rows against logical criteria (e.g., `WHERE status = 'ACTIVE'`).
- **`ORDER BY`:** Sorts resulting records ascending (`ASC`) or descending (`DESC`).

### Aggregations and Grouping
- **Aggregate Functions:** `COUNT()`, `SUM()`, `AVG()`, `MIN()`, and `MAX()` compute statistical summaries across sets of rows.
- **`GROUP BY`:** Partitions records into summary buckets based on distinct column values (e.g., counting chunks per document ID).
- **`HAVING`:** Filters aggregate groups after `GROUP BY` execution.

### Relational Joins
Joins combine columns from multiple tables using shared primary and foreign keys:
- **`INNER JOIN`:** Returns rows having matching values in both tables.
- **`LEFT JOIN`:** Returns all records from the left table and matched records from the right table (filling unmatched fields with `NULL`).

### Persistent Index Architecture
AegisCore decouples raw vector geometry from textual metadata across two files:
1. **Vector Matrix (`vectors.npy`):** A dense NumPy binary array storing the complete matrix of unit-normalized chunk embeddings with shape $(N, D)$ ($N=70$ chunks, $D=512$ dimensions).
2. **Knowledge Index Metadata (`knowledge_index.json`):** A structured JSON payload containing document metadata mappings, chunk texts, character offsets, and SHA-256 fingerprint hashes.

## 3. Explanation of Important Terms
- **Primary Key:** A column or combination of columns that uniquely identifies each row in a database table.
- **Foreign Key:** An attribute referencing the primary key of another table, enforcing referential integrity.
- **Index Serialization:** Persisting in-memory vector arrays and metadata to durable disk storage for sub-millisecond cold startups.

## 4. Practical Example
```sql
-- Querying chunk distribution and character lengths
SELECT 
    document_id,
    COUNT(chunk_id) AS total_chunks,
    AVG(character_length) AS avg_chunk_length
FROM document_chunks
WHERE is_active = 1
GROUP BY document_id
HAVING COUNT(chunk_id) > 1
ORDER BY total_chunks DESC;
```

## 5. Limitations and Common Mistakes
- **`WHERE` vs. `HAVING` Confusion:** Using `WHERE` to filter aggregate calculations produces syntax errors; aggregates must be filtered using `HAVING`.
- **Cartesian Products:** Forgetting the `ON` clause in joins results in an unintended cross-join combining every row with every other row.
- **Unindexed Lookups:** Querying millions of unindexed rows forces expensive full-table scans, increasing disk I/O and query latency.

## 6. Source References
- ISO/IEC. (2016). *Information technology — Database languages — SQL* (ISO/IEC 9075:2016). International Organization for Standardization.
- PostgreSQL Global Development Group. *PostgreSQL Documentation*. https://www.postgresql.org/docs/

