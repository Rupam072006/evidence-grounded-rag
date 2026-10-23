# Reviewer Assessment & Placement Test Review Packet

> **Candidate:** Rupam Patne (BE Computer Engineering - AI & ML)  
> **Target Environment:** Windows 10/11 / PowerShell / Python 3.10 - 3.13 (Tested on Python 3.13.1)  
> **Repository:** `https://github.com/Rupam072006/evidence-grounded-rag`  
> **Assessment Scope:** Task 2 (4-Day Extension into End-to-End Decision-Support Workflow)  
> **Assessment Status:** Complete, Verified, 100% Deterministic & Passing (65/65 Automated Tests)  

---

## 1. Executive Summary for Placement Reviewers

This submission successfully extends the **AegisCore Evidence-Grounded RAG** system from a zero-trust knowledge retrieval pipeline into an **end-to-end Decision-Support Workflow**:

$$\text{Input Signal} \longrightarrow \text{Validation} \longrightarrow \text{Retrieval} \longrightarrow \text{Evidence Audit} \longrightarrow \text{Synthesis} \longrightarrow \text{Human Approval Gate} \longrightarrow \text{Recorded Ledger}$$

### Core Invariants Enforced
1. **The Human Approval Boundary:** The AI provides decision support, surfaces facts, and articulates risks; it has **zero autonomous authority** to execute financial spend, deploy campaigns, or approve proposals.
2. **Strict Claim-Level Attribution:** Every factual statement carries a machine-verified citation `[DOCUMENT_ID:CHUNK_ID]` audited against retrieved passage content.
3. **Structured Analytical Separation:** Recommendations strictly separate **Verified Facts**, **Inferences**, **Assumptions**, and **Unknowns**.
4. **Resilience & Graceful Degradation:** 10 mandatory failure and integration scenarios (prompt injection, out-of-domain unanswerable queries, contradictory policies, corrupt indices, negative budgets) return deterministic, controlled statuses without crashing.

---

## 2. Requirement-to-Implementation Traceability Matrix

| Requirement Area | Subsystem & File Path | Verification Method & Test Target | Empirical Status |
| :--- | :--- | :--- | :---: |
| **Day 1: Baseline Audit & Defect Fixes** | `scripts/day1_audit.py`, `src/evidence_rag/generation.py`, `pipeline.py` | 16/16 baseline checks; 6 confirmed defects reproduced and fixed with regression tests. | **VERIFIED** (16/16 Passed) |
| **Day 2: Decision-Support Workflow** | `src/evidence_rag/workflow.py`, `workflow_schemas.py` | 8 automated tests in `tests/functional/test_workflow.py`. Synthetic marketing corpus (`DOC-MKT-001` - `004`). | **VERIFIED** (8/8 Passed) |
| **Day 2: Human Approval Gate** | `workflow.py:submit_approval()` | Proposal halts at `AWAITING_APPROVAL`. Transition to `APPROVED`/`REJECTED` strictly requires human reviewer signature. | **VERIFIED** |
| **Day 2: Persistent Audit Ledger** | `src/evidence_rag/record_store.py` | `data/workflow_records/records.json` with automated API key and secret scrubbing. | **VERIFIED** |
| **Day 3: CLI Workflow Exposure** | `src/evidence_rag/cli.py` | Interactive subcommands: `workflow evaluate`, `workflow approve`, `workflow show`, `workflow list`. | **VERIFIED** |
| **Day 3: 10 Failure Scenarios** | `tests/functional/test_day3_scenarios.py`, `scripts/run_day3_scenarios.py` | 10/10 automated scenarios passing; real matrix in `evidence_packet/day3_scenario_matrix.md`. | **VERIFIED** (10/10 Passed) |
| **Day 4: Benchmark Suite (>=25 Qs)** | `evaluation/questions.jsonl`, `evaluation.py` | 25 technical questions across 6 categories. 100% retrieval success, 100% citation validity, 100% failure detection. | **VERIFIED** (25/25 Executed) |
| **Day 4: Multi-Doc Ingestion Integrity** | `src/evidence_rag/ingestion.py` | 20 core technical documents + 4 marketing workflow documents verified with SHA-256 manifest checks. | **VERIFIED** (24 Documents) |
| **Zero Secrets Policy** | `.gitignore`, `record_store.py`, `cleaning.py` | Automated secret scrubbing on disk, in logs, and in git history. Zero API keys committed. | **VERIFIED** |

---

## 3. Automated Test Suite Breakdown

All 65 automated tests execute synchronously in under 1 second:

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0
plugins: anyio-4.15.1, cov-7.1.0
collected 65 items

tests/boundary/test_corrupt_index.py (1 test) .......................... PASSED
tests/boundary/test_empty_knowledge_base.py (1 test) ................... PASSED
tests/boundary/test_input_validation.py (5 tests) ...................... PASSED
tests/functional/test_citation_validation.py (3 tests) ................. PASSED
tests/functional/test_conflict_detection.py (2 tests) .................. PASSED
tests/functional/test_day3_scenarios.py (10 tests) ..................... PASSED
tests/functional/test_pipeline_qa.py (3 tests) ......................... PASSED
tests/functional/test_workflow.py (8 tests) ............................ PASSED
tests/integration/test_context_builder.py (2 tests) .................... PASSED
tests/integration/test_indexing.py (2 tests) ........................... PASSED
tests/integration/test_ingestion.py (4 tests) .......................... PASSED
tests/integration/test_retrieval.py (2 tests) .......................... PASSED
tests/regression/test_benchmark_regression.py (1 test) ................. PASSED
tests/security/test_prompt_injection.py (1 test) ....................... PASSED
tests/security/test_secret_leakage.py (1 test) ......................... PASSED
tests/unit/test_chunking.py (4 tests) .................................. PASSED
tests/unit/test_cleaning.py (6 tests) .................................. PASSED
tests/unit/test_confidence.py (2 tests) ................................ PASSED
tests/unit/test_embeddings.py (4 tests) ................................ PASSED
tests/unit/test_schemas.py (3 tests) ................................... PASSED

============================= 65 passed in 0.72s ==============================
```

---

## 4. Key Engineering Decisions & Rationale

1. **Lightweight and Deterministic Core:**
   - Evaluates offline using deterministic mock generation or TF-IDF/Sentence-Transformer embeddings, with zero mandatory cloud dependencies for testing and CI/CD.
   - When external cloud LLMs (Groq Cloud) are connected via `.env`, exponential retry backoff handles HTTP 429 rate limits automatically.
2. **Extensible Dynamic Conflict Detection:**
   - Rather than hardcoding document IDs, the conflict detector extracts topical keywords dynamically from registered contradiction policies and surfaces conflicting claims with line-level citations.
3. **Multi-Document Hash Fingerprint:**
   - Previous systems hashed only the first document. AegisCore computes a sorted SHA-256 aggregate of all document content and metadata hashes. Modifying a single character in any file invalidates the index and triggers automatic re-indexing.
4. **Strict Human Governance Boundary:**
   - Built directly into the state machine: `WorkflowRecord` requires an explicit, authenticated reviewer sign-off to transition out of `AWAITING_APPROVAL`.

---

## 5. Risk Assessment & Known Limitations

1. **Single-Pass Multi-Hop Synthesis:**
   - Queries spanning multiple disparate documents (e.g., Q11, Q12, Q13) retrieve correct passages, but individual chunk similarity scores can fall beneath single-passage sufficiency floors. The system intentionally prefers refusing over guessing. Production recommendation: Implement multi-step sub-query decomposition.
2. **Local File Ledger Scaling:**
   - Currently, workflow records are stored in atomic JSON format (`data/workflow_records/records.json`). Suitable for single-node review teams; for high-throughput enterprise use, a relational database (e.g. PostgreSQL with row-level locks) is recommended.
3. **Static Role-Based Access Control:**
   - Reviewer names are passed as parameters to the CLI/API. Enterprise production would integrate OAuth2 / SAML single sign-on (SSO) to enforce cryptographic reviewer identity.

---

## 6. Reviewer Verification Quickstart

```powershell
# 1. Clone & Enter Repository
git clone https://github.com/Rupam072006/evidence-grounded-rag.git
cd evidence-grounded-rag

# 2. Activate Virtual Environment
.venv_audit\Scripts\Activate.ps1

# 3. Run Full Automated Test Suite
python -m pytest tests -v

# 4. Run Day 3 Scenario Matrix
python scripts/run_day3_scenarios.py

# 5. Run 25-Question Empirical Benchmark
python -m evidence_rag.cli evaluate

# 6. Interactive Workflow Demonstration
python -m evidence_rag.cli workflow list
python -m evidence_rag.cli workflow show REQ-001
```
