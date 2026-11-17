# Rupam Patne Handover — WP2 Environment Test Report

**Canonical Reference:** See full detailed audit at [02_environment_test_report.md](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/02_environment_test_report.md)  
**Governing Authority / CMO Product Owner:** Prateek  
**Status:** WP2 Complete — 130/130 Tests Passed (100%), Environment Fully Reproduced  
**Date:** November 13, 2026  

## Summary of Environment Reproduction

1. **Virtual Environment:** Configured isolated Python 3.11.9 environment at `c:\Pratik_Bhuwad\CMO_Agent\.venv`.
2. **Critical Fix:** Resolved NumPy 2.x C-API ABI mismatch on host machine by pinning `numpy<2.0.0,>=1.24.0` (installed `numpy==1.26.4`), enabling error-free loading of `scipy==1.17.1` and `scikit-learn==1.9.1`.
3. **Test Suite Execution:**
   - **Collected:** 130 tests across 26 test files in 7 directories.
   - **Passed:** 130 / 130 (100% pass rate in 3.98 seconds).
   - **Statement Coverage:** 78% overall, with >90% coverage across all core RAG and workflow modules.
4. **CLI Validation:**
   - `evidence-rag verify`: Confirmed 26 documents and 348 passages indexed.
   - `evidence-rag evaluate`: Passed 25 benchmark queries with 94.7% retrieval success, 100% status/citation accuracy, and 8.3ms latency.
   - `evidence-rag workflow replay REQ-GROWTH-01`: Reconstructed evidence and preserved audit trail with exact status match (`AWAITING_APPROVAL`).
   - `evidence-rag workflow evaluate --preset growth`: Verified end-to-end policy evaluation and strict human approval boundary enforcement.
5. **Evidence Artifacts:**
   - Full test run & coverage log: [pytest_and_coverage.txt](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/test_results/pytest_and_coverage.txt)
   - Dependency freeze: [environment_freeze.txt](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/test_results/environment_freeze.txt)

WP2 is ready for review and handoff to WP3 (Evaluate RAG quality).

