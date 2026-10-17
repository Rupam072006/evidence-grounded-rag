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
