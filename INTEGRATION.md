# AegisCore Evidence-Grounded RAG System — Integration Guide

## 1. Module Interfaces and Programmatic Usage

The `evidence_rag` package provides high-level programmatic interfaces for integration into larger software systems, agent frameworks, or web APIs.

### 1.1 Basic Pipeline Execution
```python
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.config import load_config

# Load configuration and initialize pipeline
config = load_config("configs/default.yaml")
pipeline = RAGPipeline(config=config)

# Ensure vector index is built or loaded from disk
pipeline.ensure_index()

# Execute query
response = pipeline.query("What character encoding is mandatory for all incoming documents in AegisCore?")

print(f"Status: {response.status.value}")
print(f"Confidence: {response.confidence}")
print(f"Answer:\n{response.answer}")
for cit in response.citations:
    print(f"Citation: [{cit.document_id}:{cit.chunk_id}] Valid: {cit.is_valid}")
```

---

## 2. Structured Data Schemas (`schemas.py`)

All cross-module communication relies on typed Pydantic v2 schemas:

### 2.1 `ResponseStatus` (Enum)
```python
class ResponseStatus(str, Enum):
    ANSWERED = "ANSWERED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    INVALID_INPUT = "INVALID_INPUT"
    GENERATION_UNAVAILABLE = "GENERATION_UNAVAILABLE"
```

### 2.2 `RAGResponse` (Unified Response Model)
```python
class RAGResponse(BaseModel):
    query: str
    status: ResponseStatus
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

### 2.3 `Citation` (Attribution Model)
```python
class Citation(BaseModel):
    document_id: str
    chunk_id: str
    quote: Optional[str] = None
    is_valid: bool = True
    validation_reason: Optional[str] = None
```

---

## 3. Provider Configuration: Offline Mock vs Google Gemini

AegisCore explicitly separates semantic retrieval from generative LLM inference.

### 3.1 Offline Deterministic Mock Mode (Default)
- **Configuration:** Set `generation.mode: "mock"` in `configs/default.yaml` or set environment variable `RAG_GENERATION_MODE=mock`.
- **Characteristics:**
  - Fully offline, requires zero network connectivity.
  - Generates verifiable factual extractions strictly from retrieved passages.
  - Guaranteed 100% citation validity and deterministic reproducibility for testing.

### 3.2 Google Gemini GenAI Integration
- **Configuration:**
  - Set `generation.mode: "gemini"` in `configs/default.yaml` or set environment variable `RAG_GENERATION_MODE=gemini`.
  - Provide API key in environment:
    ```powershell
    $env:GEMINI_API_KEY="AIzaSyYourActualKeyHere"
    ```
- **Error Handling & 403 Isolation:**
  - If the Google project has not enabled Gemini API access (resulting in `403 PERMISSION_DENIED`), the pipeline catches the error gracefully and returns status `GENERATION_UNAVAILABLE` rather than crashing.

---

## 4. Extension Points

1. **Custom Vector Stores:** Replace `VectorIndex` in `src/evidence_rag/indexing.py` with an external vector database connector (e.g. Qdrant, Chroma, PGVector) by implementing the `search(query_vector, top_k)` interface.
2. **Dense Neural Embeddings:** Switch `embeddings.provider` to `"sentence_transformers"` and specify a HuggingFace model such as `all-MiniLM-L6-v2` or `bge-small-en-v1.5`.
3. **Custom Conflict Rules:** Add domain contradiction patterns to `ConflictDetector.KNOWN_CONFLICT_PAIRS` or extend `_detect_numerical_parameter_discrepancy()` in `src/evidence_rag/conflict_detection.py`.
4. **FastAPI Web Service:** Wrap `pipeline.query(req.query)` in a FastAPI POST endpoint `/api/v1/query` returning `response.model_dump()`.
