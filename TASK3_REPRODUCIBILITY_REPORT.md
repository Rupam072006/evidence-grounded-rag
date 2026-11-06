# TASK3_REPRODUCIBILITY_REPORT.md
## AegisCore — Clean-Install Reproducibility Report

**Project:** AegisCore — Evidence-Grounded RAG System  
**Commit Hash:** `3703c514418f76586a08a30cf341c6d14f441fff`  
**Date:** 2026-11-06  
**Auditor:** Task 3 Reliability & SRE Audit Harness  
**Environment:** Windows 10/11 (x64), Python 3.13.1  
**Evidence Reference:** `evidence_packet/clean_install_output.txt`, `evidence_packet/corpus_index_manifest.json`

---

## 1. Executive Summary

AegisCore has been comprehensively audited to ensure zero dependency on local developer configurations, hardcoded machine paths, or specific IDE runtimes. The entire pipeline—from corpus loading, text cleaning, chunking, 512-dimensional vector indexing, retrieval, groundness verification, decision-support workflow, and human approval enforcement—is 100% reproducible on a fresh machine following standard Windows PowerShell procedures.

---

## 2. Clean-Environment Installation Procedure

The following ten-step sequence provides an end-to-end verification pathway on any clean machine equipped with Python 3.10+ (tested on Python 3.13.1):

```powershell
# 1. Clone repository from GitHub
git clone https://github.com/Rupam072006/evidence-grounded-rag.git RAG_CLEAN
cd RAG_CLEAN

# 2. Initialize an isolated virtual environment
python -m venv .venv

# 3. Activate the environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# 4. Upgrade pip and install declared production & testing dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 5. Initialize environment variables from example template
Copy-Item .env.example .env

# 6. Execute system integrity and manifest verification
python -m evidence_rag.cli verify

# 7. Build fresh vector index from canonical Markdown documents
python -m evidence_rag.cli index

# 8. Run full test suite (116 automated tests)
python -m pytest tests -v

# 9. Execute benchmark evaluation across all 25 benchmark questions
python -m evidence_rag.cli evaluate

# 10. Run marketing campaign decision-support workflow
python -m evidence_rag.cli workflow evaluate --preset growth
```

---

## 3. Step-by-Step Execution Verification

### Step 5 & 6: Configuration & Integrity Verification (`verify`)
```
[INFO] Loading manifest from data/manifest.json...
Corpus Check Passed: Exactly 26 documents validated.
Index Check Passed: Loaded index with 348 passages.
All system integrity checks PASSED successfully!
```
- **Manifest Document Count:** Exactly 26 documents (DOC-001 through DOC-026).
- **All Document Hashes:** Re-hashed using SHA-256 and matched with `data/manifest.json`.
- **Index Dimensions:** Shape `(348, 512)` verified matching `HybridTfidfEmbeddingEngine`.

### Step 7: Index Rebuild from Scratch (`index`)
```
Ingesting 26 documents...
Chunking into sentence-aligned passages (chunk_size=400, overlap=60)...
Generated 348 chunks across 26 documents.
Fitting HybridTfidfEmbeddingEngine (dimension=512)...
Saving vectors.npy and knowledge_index.json...
Index rebuilt successfully!
```
- **Chunk Count:** 348 chunks generated deterministically.
- **Vector Count:** 348 vectors generated (0 missing, 0 orphan vectors).
- **Corpus Fingerprint:** `97693e876f4ded12487642bf7612fc5766e85e6f05e43aedbe11dec14bf10d11`.

### Step 8: Full Test Suite Execution
```
pytest tests -v
============================= 116 passed in 6.35s =============================
```
- **Total Collected:** 116 tests.
- **Status:** 116 passed, 0 failed, 0 skipped, 0 xfailed.

### Step 9: Benchmark Evaluation Execution
```
python -m evidence_rag.cli evaluate
       Benchmark Evaluation Metrics       
+----------------------------------------+
| Metric                 | Score / Value |
|------------------------+---------------|
| Total Questions        |            25 |
| Retrieval Success Rate |         94.7% |
| Status Accuracy        |        100.0% |
| Failure Detection Rate |        100.0% |
| Citation Validity Rate |        100.0% |
| Average Latency        |       33.7 ms |
+----------------------------------------+
```

### Step 10: Workflow & Human Approval Lifecycle
```powershell
# Evaluate proposal
python -m evidence_rag.cli workflow evaluate --preset growth
# Result: Status AWAITING_APPROVAL, paused at human approval gate

# Submit human approval
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Lead_Auditor"
# Result: Status APPROVED, reviewer and timestamp saved

# Attempt duplicate approval
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Attacker"
# Result: ValueError: Request REQ-GROWTH-01 is already finalized with status 'APPROVED'. Duplicate decisions are not permitted.
```

---

## 4. Dependencies Verification

All declared dependencies in `requirements.txt` and `pyproject.toml` were audited for compatibility with Python 3.10 through 3.13:

| Package | Declared Version | Installed Version | Role | Verification |
|---|---|---|---|---|
| `pydantic` | `>=2.0.0` | `2.14.1` | Schema models & validation | PASSED |
| `numpy` | `>=1.24.0` | `2.5.4` | Vector storage & dot products | PASSED |
| `scikit-learn` | `>=1.3.0` | `1.9.1` | TF-IDF SVD hybrid embeddings | PASSED |
| `httpx` | `>=0.24.0` | `0.28.1` | HTTP client for external providers | PASSED (Correction 1) |
| `click` | `>=8.0.0` | `8.5.0` | Command line interface | PASSED |
| `rich` | `>=13.0.0` | `15.0.0` | Terminal formatting & tables | PASSED |
| `python-dotenv`| `>=1.0.0` | `1.2.4` | Environment variable management | PASSED |
| `PyYAML` | `>=6.0` | `6.0.3` | YAML configuration parsing | PASSED |
| `pytest` | `>=7.4.0` | `9.1.1` | Automated testing framework | PASSED |

---

## 5. Offline Mock vs. Live Online Modes

| Operational Mode | Prerequisites | Deterministic? | Network Needed? | Purpose |
|---|---|---|---|---|
| **Mock Mode** (`default`) | None (Zero API keys required) | Yes (100% deterministic) | No (Fully air-gapped) | CI/CD, local testing, reproducible evaluations |
| **Groq Cloud Mode** | `GROQ_API_KEY` set in `.env` | No (LLM stochastic sampling) | Yes (External API calls) | Live natural language answers |
| **xAI Grok Mode** | `GROK_API_KEY` set in `.env` | No (LLM stochastic sampling) | Yes (External API calls) | Live xAI Beta generation |
| **Google Gemini Mode** | `GEMINI_API_KEY` set in `.env` | No (LLM stochastic sampling) | Yes (External API calls) | Live Google GenAI integration |

> [!NOTE]
> All evaluation benchmarks and automated tests in AegisCore execute under **Mock Mode** by default. This guarantees 100% offline reproducibility without leaking API keys, failing due to network latency, or exhausting external rate limits.
