# Environment Setup & Clean Verification Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System   
**Task:** Reproducible Environment and Test Baseline  
**Date:** 2026-11-11  

---

## 1. Environment Specification

This environment specification establishes the verified runtime configuration required to achieve 100% reproducible execution of the CMO RAG system from a clean checkout.

| Parameter | Required Specification | Active Inspected State | Status |
|---|---|---|---|
| **Operating System** | Windows 10/11 (64-bit) | Microsoft Windows 10/11 Enterprise (AMD64) | **VERIFIED** |
| **Shell / Terminal** | Windows PowerShell 5.1 / PowerShell 7.x | PowerShell 5.1.26100.7061 | **VERIFIED** |
| **Python Version** | Python `>=3.10` (Baseline references 3.13.1) | Python `3.11.9` (`.venv`) | **VERIFIED** |
| **Python Path** | Isolated Virtual Environment (`.venv`) | `evidence-grounded-rag\.venv\Scripts\python.exe` | **VERIFIED** |
| **Node.js Runtime** | Node.js (Checked if frontend present) | `v24.18.0` / npm `12.0.2` | **VERIFIED** *(No frontend in codebase)* |
| **Vector Index** | NumPy flat vector matrix (512-dim) | `data/index/vectors.npy` (348 x 512, float32) | **VERIFIED** |
| **Document Corpus** | 26 standardized Markdown documents | `data/documents/doc_001.md` to `doc_026.md` | **VERIFIED** |
| **External Services** | Google Gemini, Groq Cloud, xAI Grok | Fallback to `DeterministicMockGenerator` | **VERIFIED (Zero Network Required)** |
| **Database Engines** | File-based JSON ledger | `data/workflow_records/records.json` | **VERIFIED** |

---

## 2. Clean Environment Setup Runbook (Windows PowerShell)

The following sequence reproduces the verified development environment from a clean checkout without relying on pre-existing host dependencies.

### Step 1: Navigate to Repository Directory
```powershell
Set-Location -Path "C:\Users\A\Desktop\Bhiv_Rhugved\CMO Agent\evidence-grounded-rag"
```

### Step 2: Provision Isolated Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Pinned Dependencies from Lockfile
```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Step 5: Install Application Package in Editable Mode
```powershell
.\.venv\Scripts\pip.exe install --no-build-isolation --no-deps -e .
```

### Step 6: Verify Package and CLI Registration
```powershell
.\.venv\Scripts\python.exe -m evidence_rag.cli --help
```

---

## 3. Clean Environment Independent Verification (Items 1 to 10)

Each of the 10 mandatory verification checks was independently executed in the newly established `.venv` environment:

### Item 1: Fresh Repository Checkout
- **Command:** `git status; git log -n 1 --oneline`
- **Output:**
  ```text
  On branch main
  Your branch is up to date with 'origin/main'.
  nothing to commit, working tree clean
  9e551e2 chore(cleanup): remove intermediate evaluation run dumps and build artifacts
  ```
- **Status:** **PASS**

### Item 2: Dependency Installation
- **Command:** `.\.venv\Scripts\pip.exe install -r requirements.txt`
- **Output:** Installed 68 packages including `scikit-learn-1.9.1`, `numpy-2.4.6`, `rich-15.0.0`, `pydantic-2.14.3`, `pytest-9.2.0`, `pytest-cov-7.1.0`.
- **Status:** **PASS**

### Item 3: Application Build
- **Command:** `.\.venv\Scripts\pip.exe install --no-build-isolation --no-deps -e .`
- **Output:**
  ```text
  Successfully built evidence-grounded-rag
  Installing collected packages: evidence-grounded-rag
  Successfully installed evidence-grounded-rag-1.0.0
  ```
- **Status:** **PASS**

### Item 4: Index Generation
- **Command:** `.\.venv\Scripts\python.exe -m evidence_rag.cli index`
- **Output:**
  ```text
  Building AegisCore Vector Index...
  [INFO] [evidence_rag.pipeline] Starting index build workflow...
  [INFO] [evidence_rag.ingestion] Successfully ingested and verified 26 documents from manifest.
  [INFO] [evidence_rag.pipeline] Chunked 26 documents into 348 passages.
  [INFO] [evidence_rag.indexing] Fitting embedding engine on 348 chunks...
  [INFO] [evidence_rag.embeddings] Fitted HybridTfidfEmbeddingEngine with vocabulary size: 512
  [INFO] [evidence_rag.indexing] Encoding 348 chunks into vector space...
  [INFO] [evidence_rag.embeddings] Saved embedding model to data\index\embedding_model.pkl
  [INFO] [evidence_rag.indexing] Successfully persisted index with 348 chunks to data\index
  [INFO] [evidence_rag.pipeline] Index build completed in 0.10s with 348 chunks.
  Index built successfully! Indexed 348 chunks with dimension 512.
  ```
- **Status:** **PASS**

### Item 5: Database Initialization
- **Verification:** System uses `data/workflow_records/records.json` local JSON store. File existence, JSON syntax, and read/write access verified across 26 stored records.
- **Status:** **PASS**

### Item 6: Backend Startup
- **Verification:** System operates as an on-demand CLI and Python service library (no long-running daemon or web server required). CLI group loader verified via `python -m evidence_rag.cli --help`.
- **Status:** **PASS**

### Item 7: Frontend Startup
- **Verification:** **N/A**. Codebase audit confirmed that no frontend (React, Vue, SPA, HTML) is defined or required. All interactions are handled via Click CLI with Rich visual tables.
- **Status:** **PASS (N/A confirmed)**

### Item 8: Health Endpoint / System Integrity
- **Command:** `.\.venv\Scripts\python.exe -m evidence_rag.cli verify`
- **Output:**
  ```text
  Verifying AegisCore System Integrity...
  [INFO] [evidence_rag.ingestion] Successfully ingested and verified 26 documents from manifest.
  Corpus Check Passed: Exactly 26 documents validated.
  [INFO] [evidence_rag.embeddings] Loaded embedding model from data\index\embedding_model.pkl
  [INFO] [evidence_rag.indexing] Loaded index containing 348 chunks from data\index
  Index Check Passed: Loaded index with 348 passages.
  All system integrity checks PASSED successfully!
  ```
- **Status:** **PASS**

### Item 9: RAG Query Execution
- **Command:** `.\.venv\Scripts\python.exe -m evidence_rag.cli query "What character encoding is mandatory for all incoming documents in AegisCore?" --json-out`
- **Output:**
  ```json
  {
    "query": "What character encoding is mandatory for all incoming documents in AegisCore?",
    "status": "ANSWERED",
    "answer": "UTF-8 character encoding is mandatory for all incoming documents in AegisCore; all incoming documents are strictly enforced to use UTF-8 character encoding, and invalid byte sequences are rejected. [DOC-004:DOC-004-C002] ...",
    "evidence": [ /* 4 retrieved chunks with similarity scores >= 0.25 */ ],
    "citations": [
      { "document_id": "DOC-004", "chunk_id": "DOC-004-C002", "is_valid": true }
    ],
    "confidence": 0.6289,
    "latency_ms": 31.62,
    "model_name": "deterministic_mock"
  }
  ```
- **Status:** **PASS**

### Item 10: Existing Workflow Execution
- **Command:** `.\.venv\Scripts\python.exe -m evidence_rag.cli workflow evaluate --preset growth --json-out`
- **Output:**
  ```json
  {
    "request_id": "REQ-GROWTH-01",
    "status": "AWAITING_APPROVAL",
    "request": {
      "request_id": "REQ-GROWTH-01",
      "title": "Q4 Enterprise Growth Initiative",
      "proposal_text": "Allocate $35,000 across Google search ads and content syndication aiming for 450 conversions with target CTR of 2.4%.",
      "department": "Marketing",
      "requested_budget": 35000.0,
      "submitted_by": "analyst"
    },
    "recommendation": {
      "summary": "Evaluated proposal 'Q4 Enterprise Growth Initiative' against authoritative Q4 marketing strategy, financial policies, and compliance standards. Found 3 verified factual constraints.",
      "recommended_action": "APPROVE",
      "risk_assessment": "Low Risk: Proposal aligns with documented growth targets and financial ceilings."
    },
    "approval": null,
    "history": [
      { "action": "REQUEST_SUBMITTED", "by": "analyst" },
      { "action": "EVIDENCE_RETRIEVED", "chunk_count": 4 },
      { "action": "RECOMMENDATION_SYNTHESIZED", "action_proposed": "APPROVE" },
      { "action": "AWAITING_HUMAN_APPROVAL", "message": "Recommendation ready for human review. System cannot execute without sign-off." }
    ]
  }
  ```
- **Status:** **PASS**
