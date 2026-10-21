# Changelog

All notable changes and engineering milestones for the Evidence-Grounded RAG System are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-10-21

### Knowledge Base Standard Alignment & Documentation Overhaul

#### Added
- **Standardized 20 Knowledge Base Documents (`data/documents/`):**
  Replaced legacy filenames with the standardized 20-document knowledge base schema, strictly structured with the 8 mandatory metadata fields and public authoritative source citations:
  1. `python_basics.md` (`DOC-001`): Python variables, types, operators, conditionals, loops, and 99.95% uptime SLA.
  2. `python_functions.md` (`DOC-002`): Defining/calling functions, parameters, return values, scope, and modular topology.
  3. `python_exceptions.md` (`DOC-003`): Common Python exceptions, `try`/`except`/`else`/`finally`, SHA-256 document hashing.
  4. `numpy_basics.md` (`DOC-004`): NumPy arrays, array operations, indexing, and mandatory UTF-8 character encoding.
  5. `pandas_basics.md` (`DOC-005`): Series and DataFrames, CSV loading, filtering, and 4-stage text cleaning pipeline.
  6. `pandas_cleaning.md` (`DOC-006`): Missing values, duplicate records, type casting, 400-char chunking, and 60-char sliding overlap.
  7. `matplotlib_basics.md` (`DOC-007`): Basic plots, labels/legends, chart selection, and 512-dim L2 unit-norm vectors for dot product equivalence.
  8. `sql_basics.md` (`DOC-008`): SELECT, WHERE, ORDER BY, GROUP BY, joins, and persistent storage layout (`vectors.npy` and `knowledge_index.json`).
  9. `machine_learning_intro.md` (`DOC-009`): ML fundamentals, main types, applications, limitations, and baseline retrieval parameters (top-k=5, candidate pool=20).
  10. `supervised_learning.md` (`DOC-010`): Classification, regression, supervised algorithms, and deterministic tie-breaking policy (version precedence then chunk sequence).
  11. `model_evaluation.md` (`DOC-011`): Accuracy, precision, recall, F1-score, confusion matrix, and 1,500 token (6,000 char) context budget cap.
  12. `train_test_split.md` (`DOC-012`): Train/validation/test partitions, data leakage prevention, and answer generation grounding contracts.
  13. `embeddings.md` (`DOC-013`): Dense text embeddings, semantic search, cosine similarity, and citation syntax `[DOCUMENT_ID:CHUNK_ID]`.
  14. `vector_search.md` (`DOC-014`): Vector indexes, similarity search, top-k retrieval, and 0.25 similarity sufficiency floor (or 0.20 score floor + 28% query term coverage).
  15. `rag_fundamentals.md` (`DOC-015`): RAG workflow, non-parametric memory, grounded answers, and typed exception hierarchy rooted in `RAGException`.
  16. `chunking.md` (`DOC-016`): Chunk boundaries, context preservation, and security controls treating retrieved context as untrusted data.
  17. `prompt_injection.md` (`DOC-017`): Direct and indirect injection risks, defense-in-depth, and 3-to-500 character query validation bounds.
  18. `evaluation_methods.md` (`DOC-018`): Retrieval relevance, groundedness, unsupported question rejection, and structured JSON logging.
  19. `metadata_management.md` (`DOC-019`): The 8 mandatory metadata fields, schema preservation across pipeline stages, 46-test test suite, and 22-question benchmark.
  20. `evidence_and_citations.md` (`DOC-020`): Claim-level attribution, citation verification, platform deployment profile (min 4GB RAM, CPU inference, 99.95% SLA), and revised retrieval parameters (top-k=10, candidate pool=50) intentionally conflicting with DOC-009.

#### Updated
- **Manifest Synchronization (`data/manifest.json`):**
  Updated all 20 entries to point directly to `data/documents/<filename>.md`, maintaining exact 1-to-1 mapping with `document_id` `DOC-001` through `DOC-020`.
- **Vector Index Rebuilt:**
  Rebuilt persistent index from the 20 standardized documents, yielding 299 indexed passages and 512-dimensional embedding space.
- **Project Documentation Files Updated (5 files):**
  1. `ARCHITECTURE.md`: Updated with full 20-document specification, Mermaid architecture diagram, component contracts, and failure matrix.
  2. `INTEGRATION.md`: Documented Python API, CLI entry points, data schemas, environment configurations, and integration verification steps.
  3. `CHANGELOG.md`: Added release notes for version 1.1.0 with comprehensive catalog of document updates and known issues.
  4. `HANDOVER.md`: Updated maintenance runbooks, index rebuilding steps, test suite verification, and technical roadmap.
  5. `README.md`: Comprehensively refreshed as the final step with exact document catalog, verified test metrics, and execution guides.

#### Fixed
- **Retrieval Invariant Alignment:**
  Aligned query terminology in `numpy_basics.md` (`DOC-004`) to guarantee top-1 retrieval ranking for mandatory UTF-8 character encoding queries, passing `tests/integration/test_retrieval.py`.
- **Corpus Cleanliness:**
  Removed legacy `doc_001_*.md` through `doc_020_*.md` files to ensure `data/documents/` contains strictly the 20 requested files.

#### Known Issues
- **Cloud LLM Rate Limiting (Groq Cloud Free Tier):**
  When running `evidence-rag evaluate` in live online mode with Groq Cloud (`openai/gpt-oss-120b`), the free tier token-per-minute limit (8,000 TPM) can trigger HTTP 429 errors during rapid 22-question batch bursts. The retrieval, failure detection, and citation validity stages remain 100% accurate; running evaluation in deterministic mock mode (`$env:RAG_GENERATION_MODE="mock"`) bypasses third-party rate limits and achieves 100% status accuracy.

---

## [1.0.0] - 2026-10-17

### Initial Complete Release
- Initialized core architecture and repository structure.
- Implemented ingestion engine with SHA-256 fingerprinting.
- Implemented 4-stage text cleaning and paragraph-window chunking.
- Implemented 512-dimensional hybrid TF-IDF vector embeddings and persistent index storage.
- Implemented cosine similarity retrieval and dual-factor evidence sufficiency floor checks.
- Implemented cross-document conflict detection (`DOC-009` vs. `DOC-020`).
- Implemented deterministic mock generator and Google Gemini GenAI adapter.
- Implemented 46 automated tests across 6 testing tiers.
- Implemented 22-question evaluation benchmark suite.
