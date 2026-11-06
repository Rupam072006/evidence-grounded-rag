# TASK3_BASELINE.md
## AegisCore — Day 1 Baseline Verification Report
**Date:** 2026-11-05  
**Commit:** 3703c514418f76586a08a30cf341c6d14f441fff  
**Python:** 3.13.1  
**Platform:** Windows 10/11

---

## 1. Test Suite Baseline

### Test Collection
```
pytest --collect-only tests
========================= 116 tests collected =========================
```

| Category | File | Tests |
|---|---|---|
| Boundary | test_corrupt_index.py | 1 |
| Boundary | test_empty_knowledge_base.py | 1 |
| Boundary | test_input_validation.py | 5 |
| Functional | test_citation_validation.py | 3 |
| Functional | test_conflict_detection.py | 2 |
| Functional | test_day3_scenarios.py | 10 |
| Functional | test_pipeline_qa.py | 3 |
| Functional | test_task2_multi_domain.py | 12 |
| Functional | test_workflow.py | 8 |
| Integration | test_context_builder.py | 2 |
| Integration | test_indexing.py | 2 |
| Integration | test_ingestion.py | 4 |
| Integration | test_retrieval.py | 2 |
| Regression | test_benchmark_regression.py | 1 |
| Security | test_prompt_injection.py | 1 |
| Security | test_secret_leakage.py | 1 |
| Unit | test_chunking.py | 4 |
| Unit | test_cleaning.py | 6 |
| Unit | test_confidence.py | 2 |
| Unit | test_embeddings.py | 4 |
| Unit | test_schemas.py | 3 |
| **Task 3 New** | **test_task3_approval_integrity.py** | **12** |
| **Task 3 New** | **test_task3_security.py** | **20** |
| **Task 3 New** | **test_task3_replay.py** | **7** |
| **TOTAL** | | **116** |

### Test Execution Result
```
============================= 116 passed in 1.64s =============================
```
**Status: ALL PASSED ✓**

---

## 2. Corpus Baseline

| Metric | Verified Value |
|---|---|
| Total documents | 26 |
| Technical documents (T1) | 20 (DOC-001 to DOC-020) |
| Marketing documents (T2) | 6 (DOC-021 to DOC-026) |
| Documents with missing files | 0 |
| Duplicate document IDs | 0 |
| Empty documents | 0 |
| Corpus fingerprint | 97693e876f4ded12... (SHA-256 of all 26 docs) |

---

## 3. Index Baseline

| Metric | Verified Value |
|---|---|
| Total chunks | 348 |
| Total vectors | 348 |
| Embedding dimensions | 512 |
| Missing vectors | 0 |
| Orphan vectors | 0 |
| Vector-chunk alignment | VERIFIED |
| Embedding model | HybridTfidfEmbeddingEngine |
| Index created at | 2026-11-05T07:09:49Z |
| Index fingerprint | 6f9ff58432410528 |

---

## 4. Configuration Baseline

**Default configuration (`configs/default.yaml`):**

| Setting | Value |
|---|---|
| Embedding dimension | 512 |
| Top-k retrieval | 5 |
| Max context tokens | 2000 |
| Confidence threshold | 0.20 |
| Generation mode | mock (offline, deterministic) |
| Corpus path | data/documents |
| Manifest path | data/manifest.json |
| Index path | data/index |
| Record store | data/workflow_records/records.json |

---

## 5. CLI Commands Baseline

All commands verified functional:

| Command | Status |
|---|---|
| `python -m evidence_rag.cli query "..."` | ✓ WORKING |
| `python -m evidence_rag.cli index` | ✓ WORKING |
| `python -m evidence_rag.cli verify` | ✓ WORKING |
| `python -m evidence_rag.cli evaluate` | ✓ WORKING |
| `python -m evidence_rag.cli demo` | ✓ WORKING |
| `python -m evidence_rag.cli workflow evaluate --preset growth` | ✓ WORKING |
| `python -m evidence_rag.cli workflow evaluate --preset conflict` | ✓ WORKING |
| `python -m evidence_rag.cli workflow ask` | ✓ WORKING |
| `python -m evidence_rag.cli workflow approve REQ-GROWTH-01` | ✓ WORKING |
| `python -m evidence_rag.cli workflow reject REQ-GROWTH-01 --reason "..."` | ✓ WORKING |
| `python -m evidence_rag.cli workflow list` | ✓ WORKING |
| `python -m evidence_rag.cli workflow list-records` | ✓ WORKING (alias) |
| `python -m evidence_rag.cli workflow show REQ-GROWTH-01` | ✓ WORKING |
| `python -m evidence_rag.cli workflow replay REQ-GROWTH-01` | ✓ WORKING (Task 3 new) |

---

## 6. Defects Identified at Baseline

| ID | Defect | Severity | Status After Task 3 |
|---|---|---|---|
| DEFECT-001 | No formal replay CLI | MEDIUM | **FIXED** — `workflow replay` added |
| DEFECT-002 | Reviewer identity not authenticated | LOW | **DOCUMENTED** — Accepted limitation |
| DEFECT-003 | No duplicate approval prevention | HIGH | **FIXED** — State machine guard added |
| DEFECT-004 | Insufficient adversarial tests | MEDIUM | **FIXED** — 20 security scenarios added |
| DEFECT-005 | Evidence packet incomplete | HIGH | **FIXED** — All 12 required files generated |
| DEFECT-006 | Task 3 reports missing | HIGH | **FIXED** — All 11 reports created |
| DEFECT-007 | Marketing docs untracked in git | MEDIUM | **FIXED** — Added to git in final commit |

