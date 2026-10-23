# Defect Register — Task 2 Day 1 Audit

**Project:** Evidence-Grounded RAG System  
**Audit Date:** October 2026  
**Auditor:** Rupam Patne  

---

## Confirmed Defect Summary

| Defect ID | Defect Title | Severity | Impacted Component | Regression Test |
|---|---|---|---|---|
| **DEF-001** | Missing core dependency `httpx` in packaging | High | `pyproject.toml`, `requirements.txt` | Clean virtual environment import check |
| **DEF-002** | Corpus fingerprint hashing only first document | High | `src/evidence_rag/pipeline.py` | `scripts/day1_audit.py` Check 4 & 5 |
| **DEF-003** | Semantic conflation of index error as generation error | Medium | `src/evidence_rag/schemas.py`, `pipeline.py` | `tests/unit/test_schemas.py` |
| **DEF-004** | Regex failure on unicode lenticular citation brackets | Medium | `src/evidence_rag/evidence.py` | `tests/functional/test_citation_validation.py` (`test_alternate_citation_delimiters`) |
| **DEF-005** | Unhandled HTTP 429 rate limit causing generation abort | Medium | `src/evidence_rag/generation.py` | `scripts/day1_audit.py` Check 16 |
| **DEF-006** | Hard-coded single pair in conflict detector | Low | `src/evidence_rag/conflict_detection.py` | `scripts/day1_audit.py` Check 15 |

---

## Detailed Defect Records

### DEF-001: Missing `httpx` Runtime Dependency
* **Description:** The package requires `httpx` for all cloud LLM API requests in `generation.py`, but it was omitted from `pyproject.toml` dependencies and `requirements.txt`.
* **Reproduction:** Created a fresh virtual environment `.venv_audit` and ran `pip install -e .`. Running `python -c "import evidence_rag"` immediately threw `ModuleNotFoundError: No module named 'httpx'`.
* **Correction:** Added `"httpx>=0.24.0"` to `project.dependencies` in `pyproject.toml` and to `requirements.txt`.
* **Regression Test:** Clean installation verification in `.venv_audit`.

### DEF-002: Incomplete Corpus Fingerprint Calculation
* **Description:** `corpus_fingerprint` was computed as `documents[0].content_hash[:16]`. Editing any document other than `DOC-001` left the fingerprint unchanged, failing to trigger index invalidation or notify users of index staleness.
* **Reproduction:** Modified `doc_002_python_functions.md` with an audit comment. Computed index fingerprint remained `4e1ab47fa16f5470`.
* **Correction:** Computed combined SHA-256 over all documents sorted by `document_id`. Added `compute_corpus_fingerprint()` and `is_index_stale()` to `RAGPipeline`.
* **Regression Test:** `day1_audit.py` Check 4 & Check 5.

### DEF-003: Semantic Conflation of Index and Generation Errors
* **Description:** When index loading failed (e.g. index corrupted or absent), `pipeline.query()` caught the exception and emitted `ResponseStatus.GENERATION_UNAVAILABLE`. This misleadingly signaled that the LLM was down, when in fact the vector index was inaccessible.
* **Correction:** Added `INDEX_UNAVAILABLE` to `ResponseStatus` enum in `schemas.py` and returned it on index access failure.
* **Regression Test:** `tests/unit/test_schemas.py` (`test_response_statuses_complete`).

### DEF-004: Citation Regex Incompatibility with Unicode Lenticular Brackets
* **Description:** Cloud models often wrap citations in unicode brackets `【DOC-006-C007】` or use hyphen delimiters instead of colons. The regex `\[(DOC-\d{3})(?::([A-Za-z0-9\-_]+))?\]` failed to match these, resulting in 0 extracted citations and false compliance failures.
* **Reproduction:** Queried pipeline with "What is the target chunk size and sliding overlap window used by the chunker?". LLM returned valid citations formatted as `【DOC-006-C007】`. Citation extractor returned `[]`.
* **Correction:** Updated pattern to `re.compile(r"[\[\u3010](DOC-\d{3})(?:[:-]([A-Za-z0-9\-_]+))?[\]\u3011]")`.
* **Regression Test:** `tests/functional/test_citation_validation.py::test_alternate_citation_delimiters`.

### DEF-005: Unhandled HTTP 429 Rate Limiting
* **Description:** Sequential evaluation runs against Groq Cloud exceeded the 8,000 TPM limit, returning HTTP 429. The pipeline treated this as an unrecoverable failure and aborted the question.
* **Correction:** Added 3-attempt exponential backoff retry in `OpenAICompatibleGenerator.generate_answer()` with a 2.0s initial delay.
* **Regression Test:** `day1_audit.py` Check 16 (18 questions with 0 rate limit failures).

### DEF-006: Inflexible Conflict Detection Configuration
* **Description:** `ConflictDetector` relied on a static class attribute `KNOWN_CONFLICT_PAIRS = [("DOC-009", "DOC-020", ...)]`.
* **Correction:** Added `register_conflict_pair()` method and `__init__(known_pairs=...)` constructor argument so new conflict rules can be dynamically registered without modifying source code.
* **Regression Test:** `day1_audit.py` Check 15.
