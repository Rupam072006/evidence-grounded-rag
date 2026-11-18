# Test Reconciliation, Live Local Reproduction & Commercial Trace Index

| Field | Value |
|---|---|
| **Compiled By** | Pratik Bhuwad (CMO Product Owner / Sprint Lead) |
| **Timestamp** | `2026-11-18T13:09:09+05:30` |
| **Canonical Repo** | `c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main` |
| **Branch / Commit** | `main` @ `db032d6` (`docs(closure): add CMO V2 closure submission and PO deliverable`) |
| **Verification Status** | `VERIFIED NON-PRODUCTION` *(Local kernel reproduction completed; **independent verification by Tester is REQUIRED** per non-self-verification control rule)* |

---

## 1. Test-Count Reconciliation (Complete Audit Trail)

Historical documents cited several different test counts (`46`, `47`, `100`, `126`, `130`, `132`, `136`, `960`). Every number is reconciled below to its exact repository, commit, and scope:

| Count | Repository | Commit / Date | Scope & Root Cause | Status |
|---:|---|---|---|---|
| **46 → 47 → 126** | `evidence-grounded-rag-main` | Historical Task 1–3 (`2026-11-05`) | Incremental test growth reconciled in `evidence_packet/reconciliation_summary.json` (`DISC-001`): 46 T1 baseline + T2 multi-domain + T3 security/approval/replay = 126. | Reconciled |
| **130** | `evidence-grounded-rag-main` | Hariom local run (Nov 2026) | Executed across 26 test suites before the 4 LinkedIn V2 acceptance tests + 2 minor additions were committed. Hariom's raw 7 files are **pending git push** (exam leave). | Reconciled (Raw scripts `PENDING`) |
| **132** | `evidence-grounded-rag-main` | `9e551e25` / `0de4b52` (`2026-11-14`) | `evidence_packet/test_execution_summary.json` & `rupam_handover/02_environment_test_report.md` (26 test files). | Reconciled |
| **136** | `evidence-grounded-rag-main` | `b7a795c` → `db032d6` (`2026-11-18`) | **Current canonical HEAD count:** 132 prior tests + **4 new tests** in `tests/functional/test_v2_linkedin_acceptance.py` across **27 test files**. Reproduced live today: **136 passed in 3.04s**. | **Current Canonical Baseline (`VERIFIED NON-PRODUCTION`)** |
| **100 (of 960)** | `masterdb-ingestion-certification-service` | `284ef75` (`2026-11-17`) | Separate MASTERDB repository audited by Kavy (`Kavy/masterdb_test_report.md`): 960 total repo tests; 100 targeted CMO/auth/capability integration-scope tests executed, **100/100 passed** (including 20/20 `test_cmo_data_validation.py`). | Reconciled (Separate Repo) |

---

## 2. Live Local Reproduction Command & Output (18 Nov 2026)

### Environment
- **OS:** Windows (`win32`)
- **Python:** `3.11.9` (`c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe`, isolated venv with `numpy==1.26.4`)
- **Pytest:** `9.2.0` (`pluggy-1.7.0`, plugins: `anyio-4.16.0`, `cov-7.1.0`)
- **Working Directory (CRITICAL):** Must run from `c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main` *(running from parent directory fails with `IndexNotFoundError` because relative `data/index` resolves from CWD — logged as reproducibility caveat in `08_DEFECTS_RISKS_AND_BLOCKERS.md`)*.

### Exact Command for Independent Tester Reproduction
```powershell
Push-Location "c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main"
& "c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe" -m pytest tests -q --tb=short
Pop-Location
```

### Observed Output (`2026-11-18T13:09:09+05:30`, Exit Code `0`)
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 136 items

tests\boundary\test_corrupt_index.py .                                   [  0%]
tests\boundary\test_empty_knowledge_base.py .                            [  1%]
tests\boundary\test_input_validation.py .....                            [  5%]
tests\functional\test_citation_validation.py ...                         [  7%]
tests\functional\test_conflict_detection.py ..                           [  8%]
tests\functional\test_day3_scenarios.py ..........                       [ 16%]
tests\functional\test_pipeline_qa.py ....                                [ 19%]
tests\functional\test_task2_multi_domain.py ............                 [ 27%]
tests\functional\test_v2_linkedin_acceptance.py ....                     [ 30%]
tests\functional\test_workflow.py .........                              [ 37%]
tests\functional\test_workflow_cli_separation.py ..........              [ 44%]
tests\integration\test_context_builder.py ..                             [ 46%]
tests\integration\test_indexing.py ..                                    [ 47%]
tests\integration\test_ingestion.py ....                                 [ 50%]
tests\integration\test_retrieval.py ..                                   [ 52%]
tests\regression\test_benchmark_regression.py .                          [ 52%]
tests\regression\test_environment_reproducibility.py ....                [ 55%]
tests\security\test_prompt_injection.py .                                [ 56%]
tests\security\test_secret_leakage.py .                                  [ 57%]
tests\task3\test_task3_approval_integrity.py ............                [ 66%]
tests\task3\test_task3_replay.py .......                                 [ 71%]
tests\task3\test_task3_security.py ....................                  [ 86%]
tests\unit\test_chunking.py ....                                         [ 88%]
tests\unit\test_cleaning.py ......                                       [ 93%]
tests\unit\test_confidence.py ..                                         [ 94%]
tests\unit\test_embeddings.py ....                                       [ 97%]
tests\unit\test_schemas.py ...                                           [100%]

============================= 136 passed in 3.04s =============================
```

---

## 3. Commercial Traces — Separate Hard-Stop vs. Approval Path Index (AC-03)

All original historical artifacts are preserved untouched at `c:\Pratik_Bhuwad\CMO_Agent\evidence_packet\`:

| Path Verified | Request / Trace ID | Source Evidence Artifact | Key Proof |
|---|---|---|---|
| **Path A — Governance Hard Stop (No Side Effects)** | `REQ-MKT-2026-LI-01` / `TRC-20261116-1833C82E` | `evidence_packet/api_samples/req_mkt_2026_li_01_proposal_evaluated.json` & `evidence_packet/runtime_logs/REQ-MKT-2026-LI-01_execution_trace.txt` | Cites `DOC-MKT-001-C004`, `DOC-MKT-002-C005`, `DOC-MKT-003-C006`; detects $30k vs. $15k LinkedIn cap variance (`APPROVE_WITH_CONDITIONS`); **halts at `status: "AWAITING_APPROVAL"`, `approval: null`**, zero outbound calls/spend. |
| **Path B — Negative Reviewer Rejection (Placeholder / Blank)** | `REQ-MKT-2026-LI-01` / `TRC-20261116-1833C82E` | `evidence_packet/api_samples/req_mkt_2026_li_01_approval_rejected_default_reviewer.json` & `..._blank_reviewer.json` | Both `Prof_Evaluator` and blank reviewer strings rejected with `ValueError`. |
| **Path C — Explicit Human Approval (Still Zero Real-World Publish)** | `REQ-MKT-2026-LI-01` / `TRC-20261116-1833C82E` | `evidence_packet/api_samples/req_mkt_2026_li_01_approved_record.json` | Explicit named human reviewer (`Pratik Bhuwad - CMO Product Owner`) recorded with condition notes; Workflow Executor remains blocked/unconnected (zero real-world execution). |
| **Path D — Duplicate Decision Immutability** | `REQ-MKT-2026-LI-01` / `TRC-20261116-1833C82E` | `evidence_packet/api_samples/req_mkt_2026_li_01_duplicate_approval_rejected.json` | Second approval attempt raises `ValueError: Request already finalized`. |
| **Path E — Semantic Abstention (`DEFECT-SEMANTIC-001`)** | `TEST-TV-DEFECT-CHECK` | `evidence_packet/api_samples/defect_semantic_001_linear_tv_blocked.json` | Linear TV proposal halts with `status: "INSUFFICIENT_EVIDENCE"` and `null` metrics; zero hallucinated ROI. |

> **Discrepancy Flagged for Tester:** Narrative Nov 17 documents (`PRATIK_BHUWAD_PO_DELIVERABLE_V2.md`) cited an earlier run Trace ID `TRC-20261116-6C7BDA95`, whereas all persisted JSON/log artifacts in `evidence_packet/` carry `TRC-20261116-1833C82E`. This doc-vs-artifact mismatch is explicitly recorded for independent audit rather than hidden.
