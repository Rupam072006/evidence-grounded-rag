# Metadata Management, Schema Preservation, and Testing Framework

## Metadata
- **document_id:** DOC-019
- **title:** Metadata Management, Schema Preservation, and Testing Framework
- **source:** data/documents/metadata_management.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Metadata Management and Testing

## 1. Overview
Metadata represents structured descriptive data that defines the identity, origin, version, temporal validity, and topical category of ingested knowledge assets. In enterprise Retrieval-Augmented Generation systems, text content alone is insufficient; without metadata, systems cannot perform access control, detect conflicting information across versions, or provide verifiable citations. AegisCore implements strict schema validation across eight core metadata attributes and preserves these attributes through ingestion, chunking, indexing, and retrieval. Furthermore, the platform maintains an automated test suite of 46 test cases and an evaluation benchmark containing 22 test questions to ensure full pipeline integrity.

## 2. Main Concepts

### The Eight Mandatory Metadata Fields
AegisCore enforces eight mandatory metadata fields for every document entering the knowledge base:
1. **`document_id`:** Unique canonical identifier (e.g., `DOC-001` through `DOC-020`).
2. **`title`:** Human-readable title summarizing the document's subject matter.
3. **`source`:** Relative or absolute filesystem path or authoritative URL pointing to the raw file.
4. **`source_type`:** Categorical source classification (e.g., `technical_guide`, `programming_guide`, `operational_standard`).
5. **`version`:** Semantic version string (e.g., `1.0.0`) tracking document revisions and governing tie-breaking precedence.
6. **`created_at`:** ISO-8601 UTC creation timestamp (e.g., `2026-01-10T08:00:00Z`).
7. **`updated_at`:** ISO-8601 UTC last modification timestamp.
8. **`topic`:** Primary conceptual domain facilitating topical filtering and manifest indexing.

### Metadata Preservation Across Pipeline Stages
- **Ingestion:** Metadata is extracted from YAML frontmatter or Markdown header blocks and validated against Pydantic models. Missing required fields abort ingestion immediately.
- **Chunking:** Each generated chunk inherits the parent document's `document_id`, `version`, and `source`, appending a deterministic chunk sequence index (e.g., `DOC-001-C001`).
- **Indexing:** Chunk vectors are stored in matrix format (`vectors.npy`), while chunk metadata, text, and document references are serialized into `knowledge_index.json`.
- **Retrieval:** When chunks are retrieved, their full metadata context is reconstituted, enabling downstream components to evaluate version precedence, source citations, and conflict detection.

### Testing and Evaluation Framework
AegisCore enforces continuous quality gates:
- **Unit and Integration Test Suite:** A suite of 46 automated pytest test cases validating document loading, UTF-8 integrity, text cleaning, chunking boundaries, vector normalization, tie-breaking, citation formatting, and conflict detection.
- **Evaluation Benchmark:** A standardized benchmark of 22 questions across seven diagnostic categories:
  - *Answerable (single-document factual queries)*
  - *Multi-document synthesis*
  - *Ambiguous operational queries*
  - *Insufficient evidence (out-of-domain rejection)*
  - *Conflicting evidence (contradiction detection)*
  - *Adversarial (prompt injection defense)*
  - *Boundary validation (whitespace and character length limits)*

## 3. Explanation of Important Terms
- **Schema Validation:** Automated structural verification ensuring incoming data objects adhere to expected types and field requirements.
- **Provenance Tracking:** The complete historical record of an asset's origin, custody, transformations, and revisions.
- **Regression Testing:** Executing automated test suites following code or data changes to verify existing functionality remains intact.

## 4. Practical Example
The following Python script illustrates Pydantic schema validation for document metadata:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentMetadata(BaseModel):
    document_id: str = Field(..., pattern=r"^DOC-\d{3}$")
    title: str
    source: str
    source_type: str
    version: str
    created_at: datetime
    updated_at: datetime
    topic: str

raw_meta = {
    "document_id": "DOC-019",
    "title": "Metadata Management",
    "source": "data/documents/metadata_management.md",
    "source_type": "technical_guide",
    "version": "1.0.0",
    "created_at": "2026-01-10T08:00:00Z",
    "updated_at": "2026-01-15T10:30:00Z",
    "topic": "Metadata Management"
}

doc = DocumentMetadata(**raw_meta)
print(f"Validated Document: {doc.document_id} - {doc.title}")
```

## 5. Limitations or Common Mistakes
- **Dropping Metadata During Chunking:** Storing chunk text in vector stores without linking back to document ID, source path, and version makes citation generation and conflict detection impossible.
- **Inconsistent Timestamps:** Using local non-UTC timestamps causes temporal comparison errors across distributed worker nodes.
- **Skipping Regression Suites:** Modifying chunking or retrieval parameters without running the 46 tests and 22-question benchmark leads to silent accuracy regressions.

## 6. Source References
- Pydantic Data Validation and Settings Management: https://docs.pydantic.dev/latest/
- Dublin Core Metadata Initiative: Metadata Basics: https://www.dublincore.org/specifications/dublin-core/usageguide/
- Pytest Documentation: Automated Testing in Python: https://docs.pytest.org/en/stable/

