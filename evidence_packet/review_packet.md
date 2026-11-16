# Evidence Packet — Acceptance Criteria Mapping

This document maps all assignment requirements to verified code locations, commands, and empirical evidence.

| Requirement ID | Requirement Description | Implementation Location | Verification Method | Status | Evidence Reference |
|---|---|---|---|---|---|
| **REQ-01** | Audit repo and inspect environment | `pyproject.toml`, `.gitignore` | `python --version`, `git status` | **PASS** | `evidence_packet/metadata.md` |
| **REQ-02** | Exactly 20 knowledge documents | `data/documents/` (DOC-001 - DOC-020) | `python -m pytest tests/integration/test_ingestion.py` | **PASS** | 20 documents in `data/documents/` |
| **REQ-03** | Machine-readable manifest | `data/manifest.json` | Schema validation in `src/evidence_rag/ingestion.py` | **PASS** | `data/manifest.json` |
| **REQ-04** | Intentional conflicting pair | `DOC-009` vs `DOC-020` | `evidence-rag query "<conflict query>"` | **PASS** | `evidence_packet/api_samples/q02_conflict.json` |
| **REQ-05** | Text cleaning & sanitization | `src/evidence_rag/cleaning.py` | `python -m pytest tests/unit/test_cleaning.py` | **PASS** | 6 passed unit tests |
| **REQ-06** | Chunking with stable IDs | `src/evidence_rag/chunking.py` | `python -m pytest tests/unit/test_chunking.py` | **PASS** | 4 passed unit tests |
| **REQ-07** | Vector embedding generation | `src/evidence_rag/embeddings.py` | `python -m pytest tests/unit/test_embeddings.py` | **PASS** | 4 passed unit tests |
| **REQ-08** | Persistent vector index | `src/evidence_rag/indexing.py` | `evidence-rag index` | **PASS** | `data/index/vectors.npy` |
| **REQ-09** | Semantic retrieval & ranking | `src/evidence_rag/retrieval.py` | `python -m pytest tests/integration/test_retrieval.py` | **PASS** | 2 passed integration tests |
| **REQ-10** | Context construction & budgeting | `src/evidence_rag/context_builder.py` | `python -m pytest tests/integration/test_context_builder.py` | **PASS** | 2 passed integration tests |
| **REQ-11** | Grounded answer generation | `src/evidence_rag/generation.py` | `evidence-rag query "<query>"` | **PASS** | `evidence_packet/api_samples/q01_answerable.json` |
| **REQ-12** | Claim citation validation | `src/evidence_rag/evidence.py` | `python -m pytest tests/functional/test_citation_validation.py` | **PASS** | 100% citation validity rate |
| **REQ-13** | Unknown-question rejection | `src/evidence_rag/retrieval.py`, `pipeline.py` | `python -m pytest tests/functional/test_pipeline_qa.py` | **PASS** | Canonical refusal emitted |
| **REQ-14** | Conflict detection & status | `src/evidence_rag/conflict_detection.py` | `python -m pytest tests/functional/test_conflict_detection.py` | **PASS** | `CONFLICT_DETECTED` status emitted |
| **REQ-15** | Confidence & uncertainty scoring | `src/evidence_rag/confidence.py` | `python -m pytest tests/unit/test_confidence.py` | **PASS** | Confidence [0.0, 1.0] + limitation notes |
| **REQ-16** | Input validation & boundaries | `src/evidence_rag/pipeline.py` | `python -m pytest tests/boundary/test_input_validation.py` | **PASS** | 5 passed boundary tests |
| **REQ-17** | Security & prompt injection defense | `src/evidence_rag/logging_config.py`, `pipeline.py` | `python -m pytest tests/security/` | **PASS** | 2 passed security tests |
| **REQ-18** | Evaluation benchmark (>=20 questions) | `evaluation/questions.jsonl` | `evidence-rag evaluate` | **PASS** | 22 questions, 100% success rate |
| **REQ-19** | Full automated test suite | `tests/` (46 tests) | `python -m pytest tests -v` | **PASS** | 46/46 passed in 0.25s |
| **REQ-20** | Secret management & isolation | `.env.example`, `.gitignore` | `git status`, `.gitignore` verification | **PASS** | Zero secrets in repo or logs |

---

## 2. CMO V2 Commercial Test Scenario Verification Matrix ($30,000 LinkedIn Campaign)

**Governing Specification:** *BHIV / BHQ CMO Agent Technical Execution Assignment v2 (Section 6.1)*  
**Product Owner:** Pratik Bhuwad (referenced as Prateek)  
**PMC & Delivery Lead:** Nupur  
**Execution Timestamp:** 2026-11-16T10:30:00Z  
**Request ID:** `REQ-MKT-2026-LI-01`  
**Execution Trace ID:** `TRC-20261116-6C7BDA95`  
**Overall Verdict:** **100% PASS (ALL 6 CHECKPOINTS SATISFIED)**  

| Checkpoint ID | Product Owner Checkpoint | Specification & Success Criteria | Runtime Result | Checkpoint Status | Evidence Artifact Pointer |
|---|---|---|---|:---:|---|
| **AC-1** | **Clean Intake & Trace** | Proposal evaluates successfully and logs unique `request_id` and `trace_id`. | Validated input schema; generated and logged `trace_id: TRC-20261116-6C7BDA95`. History contains intake record. | **PASS** | `api_samples/req_mkt_2026_li_01_proposal_evaluated.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |
| **AC-2** | **Evidence Grounding** | Output extracts and verifies facts with valid citations citing `DOC-MKT-001`, `DOC-MKT-002`, and `DOC-MKT-003`. | Extracted verified facts citing: `DOC-MKT-001-C004` (Q4 strategy), `DOC-MKT-002-C005` (budget policy), `DOC-MKT-003-C006` (benchmarks). All citations structurally valid. | **PASS** | `api_samples/req_mkt_2026_li_01_proposal_evaluated.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |
| **AC-3** | **Channel Cap Variance Detection** | System correctly flags that $30,000 exceeds the $15,000 LinkedIn channel cap in DOC-MKT-002 (Sec 2) and recommends `APPROVE_WITH_CONDITIONS` or `REVIEW`. | Emitted inference: "Channel Cap Variance: Requested budget of $30,000.00 for Paid Social (LinkedIn Ads) exceeds the $15,000.00 channel cap specified in DOC-MKT-002 (Section 2) by $15,000.00." Emitted `recommended_action: APPROVE_WITH_CONDITIONS`. | **PASS** | `api_samples/req_mkt_2026_li_01_proposal_evaluated.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |
| **AC-4** | **Governance Hard Stop** | Proposal must halt at `AWAITING_APPROVAL`. Zero external API calls, zero ad activation, zero purchase orders, zero ledger mutations. $30,000 is test input only. | Execution paused strictly at `AWAITING_APPROVAL`. `approval` object is `null`. Workflow executor integration blocked; zero side effects. | **PASS** | `api_samples/req_mkt_2026_li_01_proposal_evaluated.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |
| **AC-5** | **Reviewer Identity Integrity** | Approving with blank reviewer or CLI default (`Prof_Evaluator`) must fail. Approval must record explicit named human reviewer (`Pratik Bhuwad - CMO Product Owner`) with decision notes. | Negative test 1 (`Prof_Evaluator`) blocked with `ValueError`. Negative test 2 (blank reviewer) blocked with `ValueError`. Managerial approval recorded by `Pratik Bhuwad - CMO Product Owner` with auditable condition notes. | **PASS** | `api_samples/req_mkt_2026_li_01_approval_rejected_default_reviewer.json`<br>`api_samples/req_mkt_2026_li_01_approval_rejected_blank_reviewer.json`<br>`api_samples/req_mkt_2026_li_01_approved_record.json` |
| **AC-6** | **Duplicate Decision Rejection** | Attempting to re-approve or re-decide finalized proposal must throw explicit duplicate error (`ValueError: Request already finalized`). | Re-approval attempt raised `ValueError: Request already finalized: Request REQ-MKT-2026-LI-01 has status 'APPROVED'. Duplicate decisions are not permitted.` State remains immutable. | **PASS** | `api_samples/req_mkt_2026_li_01_duplicate_approval_rejected.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |
| **HARIOM-CHECK** | **Semantic Abstention (`DEFECT-SEMANTIC-001`)** | Linear TV metrics must remain null and proposals allocating spend to Linear TV must abstain with `INSUFFICIENT_EVIDENCE`. | Tested proposal `TEST-TV-DEFECT-CHECK` with Linear TV broadcast request. State halted at `INSUFFICIENT_EVIDENCE` with `recommendation: null`. No metrics hallucinated. | **PASS** | `api_samples/defect_semantic_001_linear_tv_blocked.json`<br>`runtime_logs/commercial_scenario_runtime_trace.log` |

