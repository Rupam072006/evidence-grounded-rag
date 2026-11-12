# Baseline Test Execution Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Task:**Reproducible Environment and Test Baseline  
**Date:** 2026-11-11  
**Platform:** Windows 10/11 Enterprise (AMD64)  
**Python Environment:** Python 3.11.9 (`.venv`)  
**Pytest Version:** pytest 9.2.0 (plugins: anyio-4.16.0, cov-7.1.0)  

---

## 1. Overall Test Execution Summary

The baseline test battery was executed across all active test suites in the reproducible virtual environment (`.venv`).

```text
============================= 130 passed in 2.74s =============================
```

| Summary Metric | Empirical Result |
|---|---|
| **Total Test Suites Executed** | **26 Suites** |
| **Total Tests Executed** | **130 Tests** |
| **Passed Tests** | **130** (100.0%) |
| **Failed Tests** | **0** (0.0%) |
| **Skipped Tests** | **0** (0.0%) |
| **Errors / Crashes** | **0** |
| **Cumulative Execution Duration** | **2.74 seconds** |
| **Baseline Status** | **ALL PASSED (VERIFIED)** |

---

## 2. Granular Suite-by-Suite Test Execution Results

The following table records the individual execution of each test suite file:

| # | Suite Name | Test Suite File | Command Executed | Total Tests | Passed | Failed | Skipped | Duration (s) | Error Details |
|---|---|---|---|---|---|---|---|---|---|
| **1** | `test_corrupt_index` | `tests/boundary/test_corrupt_index.py` | `pytest tests/boundary/test_corrupt_index.py` | 1 | 1 | 0 | 0 | 0.04s | None |
| **2** | `test_empty_knowledge_base` | `tests/boundary/test_empty_knowledge_base.py` | `pytest tests/boundary/test_empty_knowledge_base.py` | 1 | 1 | 0 | 0 | 0.04s | None |
| **3** | `test_input_validation` | `tests/boundary/test_input_validation.py` | `pytest tests/boundary/test_input_validation.py` | 5 | 5 | 0 | 0 | 0.12s | None |
| **4** | `test_citation_validation` | `tests/functional/test_citation_validation.py` | `pytest tests/functional/test_citation_validation.py` | 3 | 3 | 0 | 0 | 0.04s | None |
| **5** | `test_conflict_detection` | `tests/functional/test_conflict_detection.py` | `pytest tests/functional/test_conflict_detection.py` | 2 | 2 | 0 | 0 | 0.12s | None |
| **6** | `test_day3_scenarios` | `tests/functional/test_day3_scenarios.py` | `pytest tests/functional/test_day3_scenarios.py` | 10 | 10 | 0 | 0 | 0.27s | None |
| **7** | `test_pipeline_qa` | `tests/functional/test_pipeline_qa.py` | `pytest tests/functional/test_pipeline_qa.py` | 3 | 3 | 0 | 0 | 0.14s | None |
| **8** | `test_task2_multi_domain` | `tests/functional/test_task2_multi_domain.py` | `pytest tests/functional/test_task2_multi_domain.py` | 12 | 12 | 0 | 0 | 0.47s | None |
| **9** | `test_workflow` | `tests/functional/test_workflow.py` | `pytest tests/functional/test_workflow.py` | 8 | 8 | 0 | 0 | 0.25s | None |
| **10** | `test_workflow_cli_separation` | `tests/functional/test_workflow_cli_separation.py` | `pytest tests/functional/test_workflow_cli_separation.py` | 10 | 10 | 0 | 0 | 0.64s | None |
| **11** | `test_context_builder` | `tests/integration/test_context_builder.py` | `pytest tests/integration/test_context_builder.py` | 2 | 2 | 0 | 0 | 0.04s | None |
| **12** | `test_indexing` | `tests/integration/test_indexing.py` | `pytest tests/integration/test_indexing.py` | 2 | 2 | 0 | 0 | 0.07s | None |
| **13** | `test_ingestion` | `tests/integration/test_ingestion.py` | `pytest tests/integration/test_ingestion.py` | 4 | 4 | 0 | 0 | 0.07s | None |
| **14** | `test_retrieval` | `tests/integration/test_retrieval.py` | `pytest tests/integration/test_retrieval.py` | 2 | 2 | 0 | 0 | 0.10s | None |
| **15** | `test_benchmark_regression` | `tests/regression/test_benchmark_regression.py` | `pytest tests/regression/test_benchmark_regression.py` | 1 | 1 | 0 | 0 | 0.30s | None |
| **16** | `test_environment_reproducibility` | `tests/regression/test_environment_reproducibility.py` | `pytest tests/regression/test_environment_reproducibility.py` | 4 | 4 | 0 | 0 | 0.18s | None |
| **17** | `test_prompt_injection` | `tests/security/test_prompt_injection.py` | `pytest tests/security/test_prompt_injection.py` | 1 | 1 | 0 | 0 | 0.09s | None |
| **18** | `test_secret_leakage` | `tests/security/test_secret_leakage.py` | `pytest tests/security/test_secret_leakage.py` | 1 | 1 | 0 | 0 | 0.04s | None |
| **19** | `test_task3_approval_integrity` | `tests/task3/test_task3_approval_integrity.py` | `pytest tests/task3/test_task3_approval_integrity.py` | 12 | 12 | 0 | 0 | 0.14s | None |
| **20** | `test_task3_replay` | `tests/task3/test_task3_replay.py` | `pytest tests/task3/test_task3_replay.py` | 7 | 7 | 0 | 0 | 0.12s | None |
| **21** | `test_task3_security` | `tests/task3/test_task3_security.py` | `pytest tests/task3/test_task3_security.py` | 20 | 20 | 0 | 0 | 0.12s | None |
| **22** | `test_chunking` | `tests/unit/test_chunking.py` | `pytest tests/unit/test_chunking.py` | 4 | 4 | 0 | 0 | 0.05s | None |
| **23** | `test_cleaning` | `tests/unit/test_cleaning.py` | `pytest tests/unit/test_cleaning.py` | 6 | 6 | 0 | 0 | 0.05s | None |
| **24** | `test_confidence` | `tests/unit/test_confidence.py` | `pytest tests/unit/test_confidence.py` | 2 | 2 | 0 | 0 | 0.04s | None |
| **25** | `test_embeddings` | `tests/unit/test_embeddings.py` | `pytest tests/unit/test_embeddings.py` | 4 | 4 | 0 | 0 | 0.07s | None |
| **26** | `test_schemas` | `tests/unit/test_schemas.py` | `pytest tests/unit/test_schemas.py` | 3 | 3 | 0 | 0 | 0.04s | None |
| **TOTAL** | **26 Suites** | **26 Files** | `pytest -v` | **130** | **130** | **0** | **0** | **2.74s** | **ALL PASSED** |

---

## 3. Comparative Baseline Analysis

| Dimension | Previous Baseline (`TASK3_BASELINE.md`) | Active Baseline (Task 2) | Variance |
|---|---|---|---|
| **Python Version** | Python 3.13.1 | Python 3.11.9 (`.venv`) | -0.2 (Supported `>=3.10`) |
| **Total Suites** | 24 | 26 | +2 Suites (`test_workflow_cli_separation.py` and `test_environment_reproducibility.py`) |
| **Total Tests** | 116 | 130 | +14 Tests |
| **Passing Tests** | 116 (100%) | 130 (100%) | +14 Passing |
| **Failing Tests** | 0 | 0 | 0 |
| **Skipped Tests** | 0 | 0 | 0 |
| **Corpus Documents** | 26 (DOC-001 to DOC-026) | 26 (DOC-001 to DOC-026) | Unchanged |
| **Vector Chunks** | 348 passages (512-dim) | 348 passages (512-dim) | Unchanged |
| **Record Store Items** | 26 historical records | 26 historical records | Unchanged |

---

## 4. Test Health Verification & Conclusion

- **Flakiness Assessment:** Zero intermittent test failures were observed across repeated runs.
- **Determinism:** Tests run 100% offline using `DeterministicMockGenerator` and local vectorized indices.
- **Test Integrity:** No test assertion, threshold, or mock was weakened or silently modified to force a pass.
- **Conclusion:** The baseline is empirically established and ready for subsequent CMO proposal workflow enhancements.
