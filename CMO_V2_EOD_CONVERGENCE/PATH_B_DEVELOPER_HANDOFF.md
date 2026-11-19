# Path B Implementation Developer Handoff Packet

| Field | Value |
|---|---|
| **Target Developer / Owner** | **Rhugved** (Runtime / Backend Integration Lead) |
| **Product Owner / Author** | **Pratik Bhuwad** (CMO Product Owner & Sprint Lead) |
| **Governing Post-EOD Task** | **Post-EOD Task 1** (`CMO_V2_EOD_CONVERGENCE/09_NEXT_THREE_TASKS.md`) |
| **Timestamp** | `2026-11-19T12:45:00+05:30` |
| **Canonical Repo & Commit** | `evidence-grounded-rag-main` (Baseline: `db032d6`, Current HEAD: `0df0990`) |
| **Python Environment** | Python `3.11.9`, isolated `.venv`, pinned `numpy==1.26.4`, `pytest 9.2.0` |
| **Approved Retrieval Path** | **Path B:** Wrap existing `src/evidence_rag/` kernel with a stateless FastAPI microservice and connect persistence to local MASTERDB (`cap-cmo-marketing-intelligence`). |

---

## 1. Welcome & Mission (Read This First, Rhugved!)

Welcome back from exams! Leadership has **formally accepted** our 18 November EOD convergence submission as the foundation for this next phase. 

Your mission for Post-EOD Task 1 is **not** to write another report or design document. Your goal is to **convert the verified kernel into a running, containerized, testable FastAPI microservice** that connects to MASTERDB.

### Non-Negotiable Invariants & Guardrails
1. **Zero Parallel RAG or Shadow Databases:** Do NOT install ChromaDB, Pinecone, FAISS, Weaviate, or any parallel vector/RAG engine. We must reuse the 136-test verified `src/evidence_rag/` retrieval engine.
2. **Zero Direct Real-World Publishing or Spending:** The CMO service must halt strictly at `AWAITING_APPROVAL`. Even after human `APPROVED` status, **no campaign is published and no ad spend is executed**. `Workflow Executor` remains strictly disconnected.
3. **Preserve Verified Baselines:** All 136 existing automated tests in `tests/` must remain green (100% pass rate).
4. **Fix Relative Path CWD Fragility (`DEF-REPRO-001`):** Ensure tests and runtime can be invoked from any directory without throwing `IndexNotFoundError`.

---

## 2. Existing Kernel Modules to Reuse Directly

All core logic is already written, verified, and passing in `src/evidence_rag/`:

```
src/evidence_rag/
├── pipeline.py            --> RAGPipeline (HybridTfidf 512-dim, ensure_index, query, abstention)
├── workflow.py            --> DecisionWorkflow & WorkflowManager (evaluates proposals against DOC-MKT-001..003)
├── workflow_schemas.py    --> WorkflowRequest, WorkflowRecord, WorkflowStatus, EvaluationResult
├── schemas.py             --> Chunk, VerifiedFact, Citation, ResponseStatus
├── conflict_detection.py  --> ConflictDetector (DOC-009/020 & DOC-024/025 policy conflict pairs)
├── evidence.py            --> CitationValidator (validates bracketed citations against candidate chunks)
├── confidence.py          --> DomainGuard & Semantic Abstention (Linear TV -> INSUFFICIENT_EVIDENCE)
├── logging_config.py      --> Secret-scrubbing audit logger (strips tokens, API keys, and raw PII)
└── record_store.py        --> Current flat-file store (TO BE ADAPTED to MASTERDB)
```

---

## 3. Exact FastAPI REST API Endpoints to Implement

Create a new submodule `src/evidence_rag/api/` with FastAPI router routes:

```
src/evidence_rag/api/
├── __init__.py
├── app.py                 --> FastAPI application factory, lifespan, CORS, middleware
├── routes/
│   ├── health.py          --> /api/v1/health
│   ├── query.py           --> /api/v1/query
│   └── proposals.py       --> /api/v1/proposals/*
├── dependencies.py        --> TANTRA RS256 JWT auth verification & dependency injection
└── masterdb_client.py     --> MasterDBPersistenceAdapter
```

### 3.1. Health Probe (`GET /api/v1/health`)
- **Method / Route:** `GET /api/v1/health`
- **Auth:** Public / Unauthenticated
- **Expected Response (`200 OK`):**
  ```json
  {
    "status": "healthy",
    "service": "cmo-agent-v2",
    "version": "2.0.0",
    "canonical_path": "Path B",
    "kernel_status": "READY",
    "index_fingerprint": "<corpus_sha256_hash>",
    "masterdb_adapter": "CONNECTED_LOCAL"
  }
  ```

### 3.2. Knowledge QA (`POST /api/v1/query`)
- **Method / Route:** `POST /api/v1/query`
- **Request Body:**
  ```json
  {
    "query": "What is the maximum allowable budget allocation for any individual marketing campaign?",
    "top_k": 4,
    "mode": "mock"
  }
  ```
- **Response Body (`200 OK`):**
  ```json
  {
    "query": "What is the maximum allowable budget allocation for any individual marketing campaign?",
    "status": "ANSWERED",
    "answer": "The maximum allowable budget allocation for any individual marketing campaign or initiative is $50,000.00. [DOC-022:DOC-022-C004]",
    "confidence": 0.78,
    "citations": [
      {
        "document_id": "DOC-022",
        "chunk_id": "DOC-022-C004",
        "is_valid": true,
        "validation_reason": "Verified in candidate pool."
      }
    ],
    "latency_ms": 9.4
  }
  ```

### 3.3. Proposal Evaluation (`POST /api/v1/proposals/evaluate`)
- **Method / Route:** `POST /api/v1/proposals/evaluate`
- **Request Body:**
  ```json
  {
    "request_id": "REQ-MKT-2026-LI-01",
    "title": "Q4 Enterprise LinkedIn Lead Gen Campaign",
    "proposal_text": "Deploy targeted sponsored content on LinkedIn targeting technical decision makers (Engineering Managers, VP of Engineering, CTOs), aiming to drive a 25% increase in sales-qualified enterprise leads (SQLs) via Paid Social (LinkedIn Ads) with requested budget of $30,000.00 USD.",
    "department": "Marketing",
    "requested_budget": 30000.0,
    "submitted_by": "analyst@bhiv.internal",
    "metadata": {
      "channel": "Paid Social (LinkedIn Ads)",
      "objective": "25% increase in SQLs"
    }
  }
  ```
- **Behavior & Invariants:**
  1. Generates unique `trace_id` (`TRC-*`).
  2. Runs retrieval across canonical marketing docs (`DOC-MKT-001`, `DOC-MKT-002`, `DOC-MKT-003`).
  3. Detects channel cap variance ($30,000 requested vs. $15,000 LinkedIn limit from `DOC-MKT-002 Sec 2`).
  4. Emits `recommended_action: "APPROVE_WITH_CONDITIONS"`.
  5. **MANDATORY GOVERNANCE HARD STOP:** Halts state strictly at `status: "AWAITING_APPROVAL"`, sets `approval: null`, and makes zero external activation calls.
  6. Writes record to `MasterDBPersistenceAdapter`.
- **Response Body (`201 Created`):**
  Matches `evidence_packet/api_samples/req_mkt_2026_li_01_proposal_evaluated.json`.

### 3.4. Human Approval (`POST /api/v1/proposals/{id}/approve`)
- **Method / Route:** `POST /api/v1/proposals/{request_id}/approve`
- **Request Body:**
  ```json
  {
    "reviewer": "Pratik Bhuwad - CMO Product Owner",
    "decision": "APPROVED",
    "notes": "Approved with condition that $15,000 excess is reallocated to Paid Search or approved by VP."
  }
  ```
- **Behavior & Negative Validation (AC-5, AC-6):**
  - If `reviewer` is empty or whitespace -> return `HTTP 422 Unprocessable Entity` (`Reviewer identity cannot be blank`).
  - If `reviewer == "Prof_Evaluator"` (placeholder) -> return `HTTP 422 Unprocessable Entity` (`Default placeholder Prof_Evaluator is rejected`).
  - If request is already finalized (`APPROVED` or `REJECTED`) -> return `HTTP 409 Conflict` (`Request already finalized. Duplicate decisions are prohibited`).
  - If valid -> transitions state to `APPROVED`, records UTC timestamp, updates MASTERDB, and logs audit trace.
  - **ZERO SIDE EFFECTS:** Still does NOT publish ads or execute spend.

### 3.5. Linear TV Semantic Abstention Check (`DEFECT-SEMANTIC-001`)
- When proposal channel is `"Linear TV Broadcasting"`:
  - System must return `status: "INSUFFICIENT_EVIDENCE"`.
  - All projected metrics (CTR, CAC, conversions, ROAS) must be strictly `null`.
  - Recommendation must be `null`.

---

## 4. MASTERDB Ingestion & Persistence Client (`MasterDBPersistenceAdapter`)

Replace `record_store.py`'s flat JSON file writes with a persistent HTTP client calling the local MASTERDB service audited by Kavy (`masterdb-ingestion-certification-service` @ `284ef75`):

```python
# src/evidence_rag/api/masterdb_client.py
import httpx
from typing import Dict, Any, Optional

class MasterDBPersistenceAdapter:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or "bba66e2f02cc8b6375669da242b91790f09377ce927d0eea5008da749e11557f"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Application-ID": "CMO_AGENT"
        }

    async def get_capability(self, capability_id: str = "cap-cmo-marketing-intelligence") -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/capabilities/{capability_id}", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def request_access_grant(self, capability_id: str = "cap-cmo-marketing-intelligence") -> str:
        payload = {
            "application_id": "CMO_AGENT",
            "capability_id": capability_id,
            "purpose": "marketing_intelligence_evaluation"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/access/request", json=payload, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("grant_id")

    async def persist_record(self, record: Dict[str, Any]) -> bool:
        # Posts verified proposal record into MASTERDB dataset storage
        ...
```

---

## 5. Bug Fix Required: Relative CWD Path Fragility (`DEF-REPRO-001`)

### The Problem
Currently, running `pytest tests` from `evidence-grounded-rag-main` succeeds (136/136 pass). But running `pytest evidence-grounded-rag-main/tests` from the parent directory fails with `IndexNotFoundError: Index files missing at ...\data\index` because `data/index` is resolved relative to the current working directory (`Path("data/index")`).

### The Fix
In `src/evidence_rag/config.py` and wherever `data_dir` or `index_dir` are resolved:
```python
# Pin paths to the repository root directory relative to __file__:
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_INDEX_DIR = DEFAULT_DATA_DIR / "index"
DEFAULT_MANIFEST_PATH = DEFAULT_DATA_DIR / "manifest.json"
```
After making this change, `pytest` will pass 100% from any working directory!

---

## 6. Dockerfile & Containerization Specification

Create `Dockerfile` in `evidence-grounded-rag-main/`:

```dockerfile
FROM python:3.11.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install pinned numpy
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "numpy==1.26.4"

# Copy source and data
COPY src/ ./src/
COPY data/ ./data/
COPY configs/ ./configs/

# Create non-root user
RUN useradd -m -u 1000 cmo && chown -R cmo:cmo /app
USER cmo

ENV PORT=8080
ENV PYTHONPATH=/app/src
ENV ENVIRONMENT=development

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

CMD ["uvicorn", "evidence_rag.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 7. Developer Step-by-Step Execution Sequence

1. **Activate Environment & Run Baseline:**
   ```powershell
   cd c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main
   ..\.venv\Scripts\Activate.ps1
   pytest tests -q --tb=short
   # Confirm 136 passed
   ```
2. **Apply `DEF-REPRO-001` Path Fix:**
   - Update `config.py` & `pipeline.py` to use `REPO_ROOT`-anchored paths.
   - Run `pytest` from parent folder to verify clean pass.
3. **Build FastAPI Module:**
   - Implement `src/evidence_rag/api/app.py` and routers.
   - Implement `MasterDBPersistenceAdapter`.
4. **Add Unit/Integration Tests for API Endpoints:**
   - Create `tests/api/test_fastapi_endpoints.py` testing:
     - `GET /api/v1/health` -> 200 OK
     - `POST /api/v1/proposals/evaluate` -> 201 Created (halts at `AWAITING_APPROVAL`)
     - `POST /api/v1/proposals/{id}/approve` with blank/Prof_Evaluator -> 422
     - `POST /api/v1/proposals/{id}/approve` duplicate -> 409
     - Linear TV evaluate -> `INSUFFICIENT_EVIDENCE`
5. **Build and Test Docker Container:**
   ```powershell
   docker build -t cmo-agent-v2:latest .
   docker run -p 8080:8080 cmo-agent-v2:latest
   curl http://localhost:8080/api/v1/health
   ```
6. **Open PR & Handover to Tester:**
   - Commit changes cleanly.
   - Notify Pratik Bhuwad and Tester for independent sign-off.
