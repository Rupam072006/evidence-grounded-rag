# AegisCore System Runtime Flow

This document details the step-by-step runtime execution flow during a query invocation.

## Step-by-Step Execution Lifecycle

```
[User Query]
      │
      ▼
1. Input Validation (`pipeline.py:validate_input`)
   ├── Check query is non-empty string
   ├── Check minimum length >= 3 chars
   ├── Check maximum length <= 500 chars
   └── Check for forbidden control characters / null bytes
   [Violation] ──► Return Status `INVALID_INPUT` (Early Interception)
      │
      ▼ (Valid Query)
2. Index Access (`pipeline.py:ensure_index`)
   └── Load persistent vectors and metadata from `data/index/`
      │
      ▼
3. Semantic Vector Retrieval (`retrieval.py:retrieve`)
   ├── Vectorize query using `embedding_engine.encode_query(query)`
   ├── Calculate dot product against stored normalized vectors
   ├── Apply keyword calibration boost (+0.08 max) for exact key-terms
   └── Filter candidates with similarity >= 0.12
      │
      ▼
4. Evidence Sufficiency Floor Check (`retrieval.py:assess_evidence_sufficiency`)
   ├── Check top retrieval score >= 0.20
   └── Check query term coverage across retrieved passages >= 28%
   [Insufficient] ──► Return Status `INSUFFICIENT_EVIDENCE` + Canonical Refusal
      │
      ▼ (Sufficient Evidence)
5. Contradiction Detection (`conflict_detection.py:detect_conflicts`)
   ├── Check known contradiction pairs (`DOC-009` vs `DOC-020`)
   └── Check numerical parameter divergence across distinct sources
   [Conflict Found] ──► Return Status `CONFLICT_DETECTED` + Dual Perspectives
      │
      ▼ (Coherent Evidence)
6. Context Construction & Quarantine (`context_builder.py:build_context`)
   ├── Delimit chunks with explicit passage boundaries
   └── Cap total character count under 1,500 token budget (6,000 chars)
      │
      ▼
7. Grounded Generation (`generation.py:generate_answer`)
   ├── Deterministic mock extraction or Gemini GenAI
   └── Append citations using format `[DOCUMENT_ID:CHUNK_ID]`
      │
      ▼
8. Citation Validation (`evidence.py:validate_citations`)
   ├── Extract all cited chunk references
   └── Verify presence in runtime retrieved candidate passages
      │
      ▼
9. Confidence & Latency Calculation (`confidence.py:calculate_confidence`)
   ├── Calculate composite confidence score (0.0 to 1.0)
   ├── Attach technical limitation disclaimers
   └── Measure total elapsed latency in milliseconds
      │
      ▼
[Unified `RAGResponse` Payload Emitted]
```
