# AegisCore System Test Results Specification

## 1. Test Suite Summary
- **Test Framework:** Pytest 8.3.4 (Python 3.13.1 on Windows 64-bit)
- **Total Test Cases:** 46
- **Passed:** 46
- **Failed:** 0
- **Execution Time:** ~0.25 seconds

## 2. Test Breakdown by Category

| Category | Test File | Test Count | Result | Description |
|---|---|---|---|---|
| **Unit** | `test_cleaning.py` | 6 | 6 PASSED | Unicode NFKC normalization, control character stripping, tag removal, PII redaction, whitespace collapse. |
| **Unit** | `test_chunking.py` | 4 | 4 PASSED | Deterministic IDs (`DOC-XXX-C00Y`), paragraph boundary splitting, sentence preservation, orphan fragment merging. |
| **Unit** | `test_embeddings.py` | 4 | 4 PASSED | L2 unit normalization, dot product equivalence, batch consistency, engine factory. |
| **Unit** | `test_confidence.py` | 2 | 2 PASSED | Confidence score bounds [0.0, 1.0], zero-evidence edge case, limitation disclosures. |
| **Unit** | `test_schemas.py` | 3 | 3 PASSED | `ResponseStatus` enums, `DocumentMetadata` validation, typed exception hierarchy. |
| **Integration** | `test_ingestion.py` | 4 | 4 PASSED | Loading exactly 20 documents, metadata validation, missing manifest error, count mismatch error. |
| **Integration** | `test_indexing.py` | 2 | 2 PASSED | Index creation, persistent disk serialization, reload from disk, missing index error. |
| **Integration** | `test_retrieval.py` | 2 | 2 PASSED | Top-k behavior, relevance ranking, source document traceability. |
| **Integration** | `test_context_builder.py` | 2 | 2 PASSED | Explicit passage boundary delimiters, token budget capping (1,500 tokens). |
| **Functional** | `test_pipeline_qa.py` | 3 | 3 PASSED | End-to-end question answering, citation generation, canonical refusal on unknown questions, irrelevant technical queries. |
| **Functional** | `test_citation_validation.py` | 2 | 2 PASSED | Validation of authentic citations, detection and rejection of invented chunk IDs. |
| **Functional** | `test_conflict_detection.py` | 2 | 2 PASSED | Intentional contradiction detection (`DOC-009` vs `DOC-020`), non-conflicting query handling. |
| **Boundary** | `test_input_validation.py` | 5 | 5 PASSED | Empty string, whitespace-only, <3 characters, >500 characters, disallowed control characters. |
| **Boundary** | `test_empty_knowledge_base.py` | 1 | 1 PASSED | Behavior on empty vector index (returns empty candidate list cleanly without crashing). |
| **Boundary** | `test_corrupt_index.py` | 1 | 1 PASSED | Behavior on corrupted index manifest files (`IndexNotFoundError`). |
| **Security** | `test_prompt_injection.py` | 1 | 1 PASSED | Adversarial system override command rejected; maintains grounding without leaking keys. |
| **Security** | `test_secret_leakage.py` | 1 | 1 PASSED | Regex masking of API keys and bearer tokens in logs. |
| **Regression** | `test_benchmark_regression.py` | 1 | 1 PASSED | Verification that benchmark evaluation meets all acceptance thresholds. |

## 3. Actual Command Line Execution Record
```powershell
PS C:\Users\rupam\OneDrive\Desktop\RAG> python -m pytest tests -v
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-8.3.4, pluggy-1.6.0 -- C:\Users\rupam\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\rupam\OneDrive\Desktop\RAG
configfile: pyproject.toml
plugins: anyio-4.15.1
collecting ... collected 46 items

tests/boundary/test_corrupt_index.py::test_corrupt_index_manifest_handling PASSED [  2%]
tests/boundary/test_empty_knowledge_base.py::test_empty_vector_index_search PASSED [  4%]
tests/boundary/test_input_validation.py::test_empty_query_rejected PASSED [  6%]
tests/boundary/test_input_validation.py::test_whitespace_only_query_rejected PASSED [  8%]
tests/boundary/test_input_validation.py::test_short_query_rejected PASSED [ 10%]
tests/boundary/test_input_validation.py::test_very_long_query_rejected PASSED [ 13%]
tests/boundary/test_input_validation.py::test_disallowed_control_characters_rejected PASSED [ 15%]
tests/functional/test_citation_validation.py::test_valid_citation_verification PASSED [ 17%]
tests/functional/test_citation_validation.py::test_invented_citation_rejected PASSED [ 19%]
tests/functional/test_conflict_detection.py::test_conflict_detection_doc009_vs_doc020 PASSED [ 21%]
tests/functional/test_conflict_detection.py::test_non_conflicting_query_does_not_trigger_conflict PASSED [ 23%]
tests/functional/test_pipeline_qa.py::test_answerable_question_flow PASSED [ 26%]
tests/functional/test_pipeline_qa.py::test_unknown_question_rejection_canonical_refusal PASSED [ 28%]
tests/functional/test_pipeline_qa.py::test_irrelevant_technical_question PASSED [ 30%]
tests/integration/test_context_builder.py::test_context_construction_boundaries PASSED [ 32%]
tests/integration/test_context_builder.py::test_context_budget_capping PASSED [ 34%]
tests/integration/test_indexing.py::test_index_build_persistence_and_reload PASSED [ 36%]
tests/integration/test_indexing.py::test_load_index_missing_raises_error PASSED [ 39%]
tests/integration/test_ingestion.py::test_ingestion_loads_exactly_20_documents PASSED [ 41%]
tests/integration/test_ingestion.py::test_ingestion_validates_all_metadata_fields PASSED [ 43%]
tests/integration/test_ingestion.py::test_ingestion_fails_on_missing_manifest PASSED [ 45%]
tests/integration/test_ingestion.py::test_ingestion_fails_on_count_mismatch PASSED [ 47%]
tests/integration/test_retrieval.py::test_retrieval_relevance_and_top_k PASSED [ 50%]
tests/integration/test_retrieval.py::test_retrieval_traceability PASSED  [ 52%]
tests/regression/test_benchmark_regression.py::test_benchmark_regression_performance PASSED [ 54%]
tests/security/test_prompt_injection.py::test_prompt_injection_attempt_handled_safely PASSED [ 56%]
tests/security/test_secret_leakage.py::test_secret_masking_filter_scrubs_api_keys PASSED [ 58%]
tests/unit/test_chunking.py::test_chunking_creates_deterministic_ids PASSED [ 60%]
tests/unit/test_chunking.py::test_chunking_preserves_sentence_boundaries PASSED [ 63%]
tests/unit/test_chunking.py::test_chunking_merges_tiny_orphan_fragments PASSED [ 65%]
tests/unit/test_chunking.py::test_chunking_empty_document PASSED         [ 67%]
tests/unit/test_cleaning.py::test_clean_text_normalizes_unicode PASSED   [ 69%]
tests/unit/test_cleaning.py::test_clean_text_strips_control_characters PASSED [ 71%]
tests/unit/test_cleaning.py::test_clean_text_preserves_tabs_and_newlines PASSED [ 73%]
tests/unit/test_cleaning.py::test_clean_text_strips_html_and_script_tags PASSED [ 76%]
tests/unit/test_cleaning.py::test_clean_text_redacts_pii_and_keys PASSED [ 78%]
tests/unit/test_cleaning.py::test_clean_text_empty_and_whitespace PASSED [ 80%]
tests/unit/test_confidence.py::test_confidence_calculation_within_bounds PASSED [ 82%]
tests/unit/test_confidence.py::test_confidence_zero_on_empty_evidence PASSED [ 84%]
tests/unit/test_embeddings.py::test_hybrid_tfidf_unit_normalization PASSED [ 86%]
tests/unit/test_embeddings.py::test_encode_query_matches_batch PASSED    [ 89%]
tests/unit/test_embeddings.py::test_dot_product_is_cosine_similarity PASSED [ 91%]
tests/unit/test_embeddings.py::test_factory_creates_configured_engine PASSED [ 93%]
tests/unit/test_schemas.py::test_response_statuses_complete PASSED       [ 95%]
tests/unit/test_schemas.py::test_document_metadata_validation PASSED     [ 97%]
tests/unit/test_schemas.py::test_exception_hierarchy PASSED              [100%]

============================= 46 passed in 0.25s ==============================
```
