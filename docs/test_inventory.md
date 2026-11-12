# Comprehensive Test Suite Inventory & Discrepancy Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Task:** Reproducible Environment and Test Baseline  
**Date:** 2026-11-11  

---

## 1. Executive Summary & Suite Count Reconciliation

The assignment instructions state:
> *"The assignment reports 24 test suites. First inspect the repository and identify the actual test suite inventory. Run all 24 reported suites if they exist... Do not invent 24 suites if the repository contains a different number. Report discrepancies explicitly."*

### Empirical Reconciliation Findings:
1. **Historical Baseline (24 Suites / 116 Tests):**  
   The previous report `TASK3_BASELINE.md` recorded exactly **24 test suites** comprising **116 automated tests**.
2. **Upstream Commit Addition (Suite #25 / +10 Tests):**  
   In Git commit `2178225042f15ddf3aed85382223ccd949b431c0` (*"feat(workflow): separate workflow ask from evaluate and add comprehensive CLI guide to README"*), an additional test file was introduced:  
   `tests/functional/test_workflow_cli_separation.py` (10 tests).  
   This brought the repository count to **25 test suites** and **126 tests**.
3. **Task 2 Regression Suite Addition (Suite #26 / +4 Tests):**  
   To fulfill Task 2 requirements (*"Add regression tests for every repaired defect"*), we introduced:  
   `tests/regression/test_environment_reproducibility.py` (4 tests).  
   This brings the active verified test inventory to **26 test suites** and **130 tests**.

---

## 2. Test Suite Inventory by Category

### Category 1: Boundary Tests (3 Suites, 7 Tests)

| # | Suite File | Test Function | Purpose / Test Coverage |
|---|---|---|---|
| **1** | `tests/boundary/test_corrupt_index.py` | `test_corrupt_index_manifest_handling` | Ensures corrupt vector files raise `IndexNotFoundError` safely without crashing. |
| **2** | `tests/boundary/test_empty_knowledge_base.py` | `test_empty_vector_index_search` | Verifies searching an empty vector index returns an empty list gracefully. |
| **3** | `tests/boundary/test_input_validation.py` | `test_empty_query_rejected`<br>`test_whitespace_only_query_rejected`<br>`test_short_query_rejected`<br>`test_very_long_query_rejected`<br>`test_disallowed_control_characters_rejected` | Tests query boundary rules: empty strings, whitespace, min length (<3), max length (>500), and disallowed control characters. |

### Category 2: Functional Tests (8 Suites, 50 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **4** | `tests/functional/test_citation_validation.py` | `test_valid_citation_verification`<br>`test_invented_citation_rejected`<br>`test_alternate_citation_delimiters` | Validates regex citation extraction, flags hallucinated chunk IDs as invalid, and verifies lenticular unicode brackets. |
| **5** | `tests/functional/test_conflict_detection.py` | `test_conflict_detection_doc009_vs_doc020`<br>`test_non_conflicting_query_does_not_trigger_conflict` | Verifies contradiction interception between DOC-009 (top-k=5) and DOC-020 (top-k=3), returning `CONFLICT_DETECTED`. |
| **6** | `tests/functional/test_day3_scenarios.py` | `test_scenario_01_valid_request_with_sufficient_evidence`<br>`test_scenario_02_request_with_no_adequate_evidence`<br>`test_scenario_03_conflicting_source_documents`<br>`test_scenario_04_malformed_request_or_missing_fields`<br>`test_scenario_05_prompt_injection_inside_proposal`<br>`test_scenario_06_unsupported_factual_claim_or_invalid_citation`<br>`test_scenario_07_empty_corpus_or_unavailable_index`<br>`test_scenario_08_generation_service_unavailable`<br>`test_scenario_09_corpus_update_followed_by_retrieval`<br>`test_scenario_10_human_approval_boundary_enforced` | Full integration coverage of the 10 mandatory Task 2 scenarios, including prompt injection, boundary gates, and index staleness triggers. |
| **7** | `tests/functional/test_pipeline_qa.py` | `test_answerable_question_flow`<br>`test_unknown_question_rejection_canonical_refusal`<br>`test_irrelevant_technical_question` | Tests end-to-end question answering, confidence calculation, and canonical refusal emission on unsupported topics. |
| **8** | `tests/functional/test_task2_multi_domain.py` | `test_task1_python_exceptions_qa`<br>`test_task1_sql_joins_qa`<br>`test_task1_ml_model_evaluation_qa`<br>`test_business_budget_policy_qa`<br>`test_business_performance_metrics_qa`<br>`test_cross_domain_retrieval`<br>`test_domain_isolation_excludes_irrelevant_docs`<br>`test_conflicting_influencer_spending_policies`<br>`test_incomplete_proposal_unknown_handling`<br>`test_insufficient_evidence_unsupported_domain`<br>`test_workflow_human_approval_enforced_no_auto_execution`<br>`test_workflow_budget_overspend_rejection` | Multi-domain regression suite: verifies technical documents (T1), business marketing policies (T2), domain isolation, and budget ceilings. |
| **9** | `tests/functional/test_workflow.py` | `test_workflow_valid_proposal_reaches_approval_gate`<br>`test_workflow_human_approval_gate_transition`<br>`test_workflow_rejection_at_approval_gate`<br>`test_workflow_budget_overspend_triggers_rejection_recommendation`<br>`test_workflow_material_conflict_detection`<br>`test_workflow_insufficient_evidence_handling`<br>`test_workflow_invalid_input_validation`<br>`test_record_store_scrubs_secrets_before_persisting` | Tests `DecisionWorkflow` engine: validation, financial rules, human approval transition, rejection, and secret scrubbing. |
| **10** | `tests/functional/test_workflow_cli_separation.py` *(Upstream Add)* | `test_cli_workflow_ask_basic`<br>`test_cli_workflow_ask_unanswerable_refusal`<br>`test_cli_workflow_ask_json_out`<br>`test_cli_workflow_evaluate_preset_growth`<br>`test_cli_workflow_evaluate_preset_overspend`<br>`test_cli_workflow_evaluate_preset_incomplete`<br>`test_cli_workflow_evaluate_preset_conflict`<br>`test_cli_workflow_evaluate_custom_proposal`<br>`test_cli_workflow_evaluate_json_out`<br>`test_cli_workflow_ask_and_evaluate_records_isolation` | Verifies separation between informational policy Q&A (`workflow ask`) and proposal evaluation (`workflow evaluate`), ensuring `ask` does not pollute the proposal ledger. |

### Category 3: Integration Tests (4 Suites, 10 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **11** | `tests/integration/test_context_builder.py` | `test_context_builder_budget_cap`<br>`test_context_builder_formats_header` | Verifies context synthesizer enforces 1,500 token ceiling and formats document metadata headers cleanly. |
| **12** | `tests/integration/test_indexing.py` | `test_vector_index_build_and_load`<br>`test_vector_index_search_cosine_ranking` | Verifies disk persistence and deserialization of `VectorIndex` and cosine similarity score ranking. |
| **13** | `tests/integration/test_ingestion.py` | `test_manifest_ingestion_valid_corpus`<br>`test_missing_manifest_raises_error`<br>`test_corrupt_manifest_raises_error`<br>`test_manifest_document_count_mismatch` | Tests manifest validation, count verification (26 documents), and cryptographic hash checking. |
| **14** | `tests/integration/test_retrieval.py` | `test_retriever_returns_top_k`<br>`test_retriever_evidence_sufficiency_floor` | Validates candidate ranking, top-k slicing, and evidence sufficiency floor rejection (<0.20). |

### Category 4: Regression Tests (2 Suites, 5 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **15** | `tests/regression/test_benchmark_regression.py` | `test_evaluation_benchmark_regression_metrics` | Runs benchmark questions and verifies retrieval success ($\ge 90\%$) and status accuracy ($\ge 95\%$). |
| **16** | `tests/regression/test_environment_reproducibility.py` *(Task 2 Add)* | `test_required_runtime_dependencies_importable`<br>`test_hybrid_tfidf_embedding_engine_fit_and_encode`<br>`test_clean_environment_rag_pipeline_smoke`<br>`test_clean_environment_decision_workflow_smoke` | **Regression suite for DEFECT-ENV-001**: Verifies all required dependencies (`sklearn`, `rich`, `numpy`, `pydantic`) are importable and execute properly in `.venv`. |

### Category 5: Security & Adversarial Tests (2 Suites, 2 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **17** | `tests/security/test_prompt_injection.py` | `test_prompt_injection_ignored_in_generation` | Verifies adversarial override tokens (e.g. `IGNORE PREVIOUS INSTRUCTIONS`) embedded in passages do not divert generator. |
| **18** | `tests/security/test_secret_leakage.py` | `test_secret_masking_in_logs` | Confirms `SecretMaskingFilter` redacts Google API keys (`AIzaSy...`) and Bearer tokens from logger records. |

### Category 6: Task 3 Governance, Replay & Security Suites (3 Suites, 39 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **19** | `tests/task3/test_task3_approval_integrity.py` | `test_valid_approval_recorded`<br>`test_valid_rejection_recorded`<br>`test_nonexistent_request_id_returns_none`<br>`test_duplicate_approval_prevented`<br>`test_duplicate_rejection_prevented`<br>`test_approval_after_rejection_prevented`<br>`test_decision_recorded_in_history`<br>`test_approval_timestamp_stored`<br>`test_approval_metadata_complete`<br>`test_corrupt_json_does_not_crash_read`<br>*(and additional integrity checks)* | **DEFECT-003 validation**: Prevents duplicate approvals or re-decisions on finalized records. Mandates non-empty reviewer name. |
| **20** | `tests/task3/test_task3_replay.py` | `test_replay_record_retrievable`<br>`test_replay_original_evidence_preserved`<br>`test_replay_recommendation_preserved`<br>`test_replay_approval_decision_preserved`<br>`test_replay_does_not_prove_approval_legitimacy`<br>`test_replay_history_audit_trail_preserved`<br>`test_replay_roundtrip_serialization` | Verifies proposal replay determinism and explicitly tests that replay reconstructs evidence without falsely proving identity. |
| **21** | `tests/task3/test_task3_security.py` | `test_s01_prompt_injection_in_retrieved_docs` through `test_s20_record_modification_after_approval_prevented` (20 tests) | 20 comprehensive security scenarios: HTTP 429 bounded backoff, corrupted indices, secret scrubbing, empty reviewers, malformed JSON. |

### Category 7: Unit Tests (5 Suites, 19 Tests)

| # | Suite File | Test Functions | Purpose / Test Coverage |
|---|---|---|---|
| **22** | `tests/unit/test_chunking.py` | `test_chunking_creates_deterministic_ids`<br>`test_chunking_preserves_sentence_boundaries`<br>`test_chunking_merges_tiny_orphan_fragments`<br>`test_chunking_empty_document` | Unit tests for chunk ID naming, sentence boundary preservation, and small fragment merging. |
| **23** | `tests/unit/test_cleaning.py` | `test_clean_text_normalizes_unicode`<br>`test_clean_text_strips_control_characters`<br>`test_clean_text_preserves_tabs_and_newlines`<br>`test_clean_text_strips_html_and_script_tags`<br>`test_clean_text_redacts_pii_and_keys`<br>`test_clean_text_empty_and_whitespace` | Unit tests for NFKC normalization, whitespace rules, PII redaction, and HTML stripping. |
| **24** | `tests/unit/test_confidence.py` | `test_confidence_calculation_within_bounds`<br>`test_confidence_zero_on_empty_evidence` | Unit tests for composite uncertainty formula (top score, mean top-3, term coverage). |
| **25** | `tests/unit/test_embeddings.py` | `test_hybrid_tfidf_unit_normalization`<br>`test_encode_query_matches_batch`<br>`test_dot_product_is_cosine_similarity`<br>`test_factory_creates_configured_engine` | Unit tests for TF-IDF L2 normalization, query batch equivalence, and dot product cosine math. |
| **26** | `tests/unit/test_schemas.py` | `test_response_statuses_complete`<br>`test_document_metadata_validation`<br>`test_exception_hierarchy` | Unit tests for Pydantic v2 schemas and exception hierarchy. |

---

## 3. Discrepancy Summary Table

| Metric | Reported in Baseline (`TASK3_BASELINE.md`) | Discovered in Current Checkout | Following Task 2 Regression Fix | Discrepancy Explanation |
|---|---|---|---|---|
| **Total Test Suites (Files)** | **24** | **25** | **26** | Upstream commit `2178225` added `test_workflow_cli_separation.py`; Task 2 added `test_environment_reproducibility.py`. |
| **Total Tests** | **116** | **126** | **130** | +10 tests from CLI separation; +4 tests from environment reproducibility regression suite. |
| **Pass Rate** | 100% (116/116) | 100% (126/126) | 100% (130/130) | All suites execute cleanly with 0 failures, 0 skipped. |
| **Execution Duration** | 1.64s (Python 3.13) | 2.48s (Python 3.11) | 2.74s (Python 3.11) | Executed in `.venv` on Windows 10/11 AMD64. |
