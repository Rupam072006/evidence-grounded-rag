# AegisCore Evidence-Grounded RAG System — Integration Guide

## 1. Module Connections and Pipeline Flow

The `evidence_rag` package is organized as a modular, decoupled Python library. The components communicate using typed Pydantic models and immutable dataclasses:

```
[data/documents/*.md] + [data/manifest.json]
       │
       ▼
1. IngestionEngine (src/evidence_rag/ingestion.py)
       │  Outputs: List[Document] (with DocumentMetadata & SHA-256 hash)
       ▼
2. Chunker (src/evidence_rag/chunking.py)
       │  Outputs: List[Chunk] (with ChunkMetadata & sequential IDs)
       ▼
3. VectorIndex (src/evidence_rag/indexing.py)
       │  Encodes via HybridTfidfEmbeddingEngine (512-dim unit norm)
       │  Persists to: vectors.npy, knowledge_index.json, embedding_model.pkl
       ▼
4. Retriever (src/evidence_rag/retrieval.py)
       │  Inputs: query (str)
       │  Outputs: List[RetrievedChunk] (ranked with cosine similarity scores)
       ▼
5. ConflictDetector (src/evidence_rag/conflict_detection.py)
       │  Inputs: query, List[RetrievedChunk]
       │  Outputs: Optional[ConflictEvidence]
       ▼
6. ContextBuilder (src/evidence_rag/context_builder.py)
       │  Inputs: List[RetrievedChunk]
       │  Outputs: Formatted prompt context string within 1,500 token budget
       ▼
7. BaseGenerator (src/evidence_rag/generation.py)
       │  Generators: DeterministicMockGenerator, GroqGenerator, GeminiGenerator
       │  Outputs: answer (str), ResponseStatus
       ▼
8. CitationValidator (src/evidence_rag/evidence.py)
       │  Inputs: answer, List[RetrievedChunk]
       │  Outputs: List[Citation] (verifying [DOC-ID:CHUNK-ID] against retrieved context)
       ▼
RAGResponse (Final Structured Output Model)
```

---

## 2. Programmatic Python API

### 2.1 Basic Pipeline Execution
```python
from pathlib import Path
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.config import load_config

# 1. Initialize pipeline with default or custom configuration
config = load_config("configs/default.yaml")
pipeline = RAGPipeline(config=config, base_dir=Path.cwd())

# 2. Ensure vector index is built and loaded
pipeline.ensure_index()

# 3. Execute query
response = pipeline.query("What character encoding is mandatory for all incoming documents in AegisCore?")

# 4. Access structured fields
print(f"Status: {response.status.value}")
print(f"Confidence: {response.confidence:.4f}")
print(f"Answer:\n{response.answer}")

for cit in response.citations:
    print(f"Citation: [{cit.document_id}:{cit.chunk_id}] Valid: {cit.is_valid}")
```

### 2.2 CLI Integration Points
The project installs the `evidence-rag` command-line executable with four primary subcommands:
```powershell
# Rebuild the vector index from data/documents/ and data/manifest.json
evidence-rag index

# Verify corpus and index integrity (confirms 20 documents and persistent files)
evidence-rag verify

# Query the pipeline interactively
evidence-rag query "What is the primary operational mission of AegisCore and what uptime SLA does it target?"

# Run the 22-question automated evaluation benchmark
evidence-rag evaluate
```

---

## 3. Data Schemas and Serialization Formats

### 3.1 Input Formats
- **Knowledge Documents (`data/documents/*.md`):** Markdown files containing a `## Metadata` section with 8 required fields:
  - `document_id`: String matching `DOC-001` through `DOC-020`.
  - `title`: Descriptive document title.
  - `source`: Relative filesystem path (e.g., `data/documents/doc_001_python_basics.md`).
  - `source_type`: Category identifier (e.g., `programming_guide`, `technical_guide`).
  - `version`: Semantic version string (e.g., `1.0.0`).
  - `created_at`: ISO-8601 UTC timestamp.
  - `updated_at`: ISO-8601 UTC timestamp.
  - `topic`: Primary subject area.
- **Corpus Manifest (`data/manifest.json`):** JSON dictionary mapping `documents` to metadata entries and declaring `total_documents: 20`.
- **User Query:** String containing between 3 and 500 printable characters. Empty or whitespace-only queries are rejected with `INVALID_INPUT`.

### 3.2 Output Model (`RAGResponse`)
```python
class RAGResponse(BaseModel):
    query: str
    status: ResponseStatus  # ANSWERED, INSUFFICIENT_EVIDENCE, CONFLICT_DETECTED, INVALID_INPUT, GENERATION_UNAVAILABLE
    answer: str
    evidence: List[RetrievedChunk]
    source_document_ids: List[str]
    source_chunk_ids: List[str]
    citations: List[Citation]
    confidence: float
    limitations: List[str]
    conflicting_evidence: Optional[ConflictEvidence] = None
    latency_ms: float
    model_name: Optional[str] = None
```

### 3.3 Citation Schema
```python
class Citation(BaseModel):
    document_id: str
    chunk_id: str
    quote: Optional[str] = None
    is_valid: bool = True
    validation_reason: Optional[str] = None
```

---

## 4. Configuration Variables & Environment Settings

Configuration is loaded hierarchically from `configs/default.yaml` and overridden by environment variables:

| Environment Variable | Default Value | Description |
|---|---|---|
| `RAG_GENERATION_MODE` | `mock` | Generation backend: `mock` (offline deterministic), `groq` (Groq Cloud), `gemini` (Google GenAI) |
| `GROQ_API_KEY` | *(None)* | API key for Groq Cloud LLM inference (e.g., `gsk_...`) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Target model name on Groq Cloud platform |
| `GEMINI_API_KEY` | *(None)* | API key for Google Gemini GenAI integration |
| `RAG_SIMILARITY_FLOOR` | `0.20` | Minimum cosine similarity threshold for passage consideration |
| `RAG_TERM_COVERAGE_FLOOR` | `0.28` | Minimum fraction of query words that must appear in retrieved passages |
| `RAG_MAX_CONTEXT_TOKENS` | `1500` | Context token cap (approx. 6,000 characters) |
| `RAG_TOP_K` | `5` | Number of candidate chunks returned to generator |
| `RAG_CANDIDATE_POOL` | `20` | Initial candidate retrieval pool size |

---

## 5. Integration Verification Steps

To verify that the integration is functioning correctly across all modules:

1. **Verify Ingestion and Corpus:**
   ```powershell
   evidence-rag verify
   ```
   *Expected output:* `Corpus Check Passed: Exactly 20 documents validated.` and `Index Check Passed: Loaded index with 299 passages.`

2. **Verify Offline Test Suite:**
   ```powershell
   python -m pytest tests -q
   ```
   *Expected output:* `46 passed in <1s`

3. **Verify Refusal on Insufficient Evidence:**
   ```powershell
   evidence-rag query "What is the secret recipe for Aunt May's chocolate chip cookies?"
   ```
   *Expected status:* `INSUFFICIENT_EVIDENCE` with canonical refusal text.

4. **Verify Conflict Detection:**
   ```powershell
   evidence-rag query "What is the default production top-k parameter and candidate pool size for the retrieval service?"
   ```
   *Expected status:* `CONFLICT_DETECTED` with both DOC-009 and DOC-020 cited.

---

## 6. Decision-Support Workflow Integration (Task 2)

The decision-support workflow extends the core RAG pipeline into a governed recommendation system with an explicit human approval gate.

### 6.1 Workflow Execution Flow
```text
WorkflowRequest -> Validation -> Retrieval -> Evidence Set -> Sufficiency Assessment -> Conflict Detection -> Grounded Recommendation Synthesis -> Awaiting Approval Gate -> Human Decision -> Audit Record
```

### 6.2 Python API Usage

```python
from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import WorkflowRequest

# 1. Initialize workflow engine
wf = DecisionWorkflow()

# 2. Submit proposal request
request = WorkflowRequest(
    request_id="REQ-2026-001",
    title="Q4 Enterprise LinkedIn Lead Gen Campaign",
    proposal_text="Deploy targeted sponsored content on LinkedIn targeting technical decision makers, aiming for a 25 percent increase in SQLs with a budget of $30,000.",
    department="Marketing",
    requested_budget=30000.0,
    submitted_by="growth_lead"
)

# 3. Evaluate proposal (stops at Human Approval Gate)
record = wf.evaluate_proposal(request)
print("Status:", record.status)  # WorkflowStatus.AWAITING_APPROVAL
print("Recommended Action:", record.recommendation.recommended_action)  # APPROVE

# 4. Human Approval Gate: Submit manager decision
decision_record = wf.submit_approval(
    request_id="REQ-2026-001",
    decision="APPROVED",
    reviewer="Rupam Patne",
    notes="Proposal verified against Q4 budget ceilings ($50k) and lead targets."
)
print("Final Status:", decision_record.status)  # WorkflowStatus.APPROVED
```

### 6.3 Workflow Status Lifecycle

| Status | Trigger Condition | Consequential Action Permitted |
|---|---|---|
| `INVALID_REQUEST` | Validation boundary failed (empty ID, short title, negative budget) | None (Rejected prior to retrieval) |
| `INDEX_UNAVAILABLE` | Vector index corrupted, missing, or inaccessible | None (Safe degradation) |
| `INSUFFICIENT_EVIDENCE` | Retrieval similarity below floor or domain not covered | None (Refusal emitted) |
| `CONFLICT_DETECTED` | Material factual contradiction between policy sources | None (Contradiction surfaced for human review) |
| `AWAITING_APPROVAL` | Recommendation synthesized; halted at human gate | **No external action without human sign-off** |
| `APPROVED` | Explicit human reviewer approval recorded | Action authorized according to approved proposal |
| `REJECTED` | Explicit human reviewer rejection recorded | Action halted and archived |

