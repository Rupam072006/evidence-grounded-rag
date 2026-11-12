# Existing Features Classification Matrix

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Date:** 2026-11-11  
**Classification Taxonomy:**
- `IMPLEMENTED`: Fully implemented in code with operational logic and test coverage.
- `PARTIALLY IMPLEMENTED`: Functional components exist, but significant elements are incomplete, rule-based, or lack production parity.
- `MISSING`: Capability is absent from the codebase.
- `MOCKED`: Logic returns hardcoded, synthetic, or rule-based placeholders rather than dynamic computation.
- `UNVERIFIED`: Code is present, but cannot be validated or executed in the current runtime environment due to missing dependencies, external service requirements, or missing credentials.

---

## 1. Feature Classification Matrix

| # | Feature / Capability | Classification | Primary Implementation Files | Operational Mechanism & Logic | Limitations, Gaps & Runtime Notes |
|---|---|---|---|---|---|
| **1** | **Document Ingestion** | `IMPLEMENTED` & `VERIFIED` | `src/evidence_rag/ingestion.py`<br>`data/manifest.json` | Validates manifest completeness, verifies required document count (26 in default, 4 in marketing), checks document schema, and calculates SHA-256 cryptographic hashes for each document. | Fully operational and verified under Python 3.11 `.venv`. Manifest validation and hash checking pass consistently. |
| **2** | **Document Parsing & Cleaning** | `IMPLEMENTED` | `src/evidence_rag/cleaning.py` | 5-stage text sanitization: Unicode NFKC normalization, script/HTML tag stripping, control character removal, email/API key redaction, and whitespace/newline consolidation. | Uses standard regex and Python `unicodedata`. Does not handle complex binary document formats (PDF, DOCX) directly; operates on markdown/text files. |
| **3** | **Chunking** | `IMPLEMENTED` | `src/evidence_rag/chunking.py` | Boundary-aware paragraph window chunker. Targets 400 characters per chunk with 60-character sliding overlap and a 40-character minimum floor. Falls back to sentence splitting for oversized paragraphs. | Generates deterministic chunk IDs (e.g. `DOC-001-C001`). Operates on character counts rather than tokenizer tokens. |
| **4** | **Embedding Generation** | `IMPLEMENTED` *(TF-IDF)* / `PARTIALLY IMPLEMENTED` *(Dense)* | `src/evidence_rag/embeddings.py` | `HybridTfidfEmbeddingEngine` fits vocabulary and generates 512-dimensional L2-normalized vectors using sublinear term frequency and (1, 2) n-grams. `SentenceTransformerEmbeddingEngine` class is defined for dense embeddings. | `HybridTfidfEmbeddingEngine` verified operational via `scikit-learn` in `.venv`. Dense neural embeddings (`all-MiniLM-L6-v2`) remain optional extension. |
| **5** | **Vector Indexing** | `IMPLEMENTED` | `src/evidence_rag/indexing.py`<br>`data/index/` | `VectorIndex` stores chunk objects and a NumPy float32 binary matrix (`vectors.npy`). Computes cosine similarity via dot product. Tracks corpus SHA-256 fingerprint for cache staleness detection. | Flat brute-force dot product. No Approximate Nearest Neighbor (ANN) index (FAISS, HNSW) is used; suitable for small corpora (348 chunks), but not scalable to >100k passages. |
| **6** | **Semantic Retrieval** | `IMPLEMENTED` | `src/evidence_rag/retrieval.py` | `Retriever.retrieve()` encodes incoming query, performs vector search against indexed passages, and applies candidate similarity threshold (`0.12`). | Based on hybrid TF-IDF + n-gram vector representations rather than dense transformer representations. |
| **7** | **Hybrid Retrieval** | `PARTIALLY IMPLEMENTED` | `src/evidence_rag/retrieval.py` | Calculates additive exact keyword boost (up to 0.08) for matching query terms within chunk text, layered on top of vector similarity. Applies domain-aware routing multipliers. | Not a true dual-index dense-neural + sparse BM25 pipeline with Reciprocal Rank Fusion (RRF). It is a hybrid score adjustment on a single vector index. |
| **8** | **Reranking** | `PARTIALLY IMPLEMENTED` / `MOCKED` | `src/evidence_rag/retrieval.py` | Re-orders candidates based on lexical keyword overlap ratio and domain category weights (`domain_multiplier = 0.60` downweighting irrelevant domains). | No cross-encoder neural model (e.g. `bge-reranker`, `Cohere Rerank`) is implemented. Re-ranking is performed via heuristic arithmetic adjustments. |
| **9** | **Citation Generation** | `IMPLEMENTED` | `src/evidence_rag/generation.py` | `DeterministicMockGenerator` extracts top candidate sentences and appends standardized citation tags `[DOC-XXX:CHUNK_ID]`. External LLM system prompt enforces the same syntax. | In mock mode, citations are mechanically appended to top overlapping sentences from retrieved passages. |
| **10** | **Evidence Verification** | `IMPLEMENTED` | `src/evidence_rag/evidence.py` | `CitationValidator` parses citation patterns (`[DOC-XXX:CHUNK_ID]`), verifies that cited documents existed in the retrieved context, and validates that the specific chunk ID was present in the candidate pool. | Validates citation existence against retrieved chunks; does not perform Natural Language Inference (NLI) entailment checking between claim and source text. |
| **11** | **Conflict Detection** | `IMPLEMENTED` | `src/evidence_rag/conflict_detection.py` | Detects cross-document contradictions via registered known contradiction pairings (DOC-009 vs DOC-020; DOC-024 vs DOC-025) and numerical parameter discrepancy regex scanning. | Pairings for marketing spending limits are pre-registered; numerical conflict detection is heuristic and rule-driven. |
| **12** | **Response Generation** | `IMPLEMENTED` *(Mock)* / `UNVERIFIED` *(LLM)* | `src/evidence_rag/generation.py` | `DeterministicMockGenerator` provides 100% offline, deterministic, grounded extraction. `GeminiGenerator`, `GroqGenerator`, and `GrokGenerator` provide external API generation. | External LLM providers are unverified in runtime due to missing `.env` API keys. Mock generator is the active default. |
| **13** | **Proposal Generation** | `PARTIALLY IMPLEMENTED` / `MOCKED` | `src/evidence_rag/workflow.py` | Synthesizes `RecommendationReport` containing verified facts, inferences, assumptions, and unknowns based on hardcoded policy checks (e.g. $50,000 budget cap, 15% reserve, DOC-026 gap checks). | The system evaluates proposals; it does **not** dynamically draft or generate campaign proposals from high-level objectives. Inferences and unknowns are rule-based template strings. |
| **14** | **Approval Workflow** | `IMPLEMENTED` | `src/evidence_rag/workflow.py`<br>`src/evidence_rag/record_store.py` | Mandates human governance gate. Proposal evaluation pauses at `AWAITING_APPROVAL`. `submit_approval()` records human decision (`APPROVED`/`REJECTED`) with reviewer name, timestamp, and notes. Enforces single-decision finality. | Reviewer identity is a recorded text string; there is no role-based access control (RBAC), SSO, or cryptographic signature verification. |
| **15** | **Audit Logging** | `IMPLEMENTED` | `src/evidence_rag/logging_config.py`<br>`data/workflow_records/records.json` | Structured logging with `SecretMaskingFilter` redacting API keys and Bearer tokens. Persistent transaction ledger in `records.json` records every submission, state transition, and decision. | Ledger is a local single-file JSON store; lacks distributed transaction locking, concurrency controls, or append-only cryptographic hashing (e.g., Merkle tree). |

---

## 2. In-Depth Technical Analysis of Specific Capabilities

### 2.1 Document Ingestion & Verification
- **Strengths:** Manifest-driven approach ensures deterministic reproducibility. Every document has a verified SHA-256 content hash in `data/manifest.json`. Any missing file or count discrepancy triggers a fail-fast `CorpusError`.
- **Weaknesses:** Ingestion is file-system based and synchronous. Re-indexing requires a full pass over all 26 documents.

### 2.2 Vector Indexing & Hybrid Retrieval
- **Strengths:** Hybrid TF-IDF vectorizer (512 dimensions) provides 100% reproducible, bitwise deterministic embeddings across machines without GPU or internet dependencies. Dot product search is fast for small collections.
- **Weaknesses:** Lacks dense semantic representations from transformer encoders in the active default path. Domain-specific routing and keyword boosting prevent cross-domain contamination but rely on hardcoded keyword dictionaries (`DOMAIN_KEYWORDS`).

### 2.3 Conflict Detection
- **Strengths:** Directly addresses multi-document contradictions—a common failure mode in enterprise RAG. When contradictory documents (e.g. DOC-024 permitting $25,000 influencer spend vs DOC-025 restricting it to $10,000) are retrieved, the system catches the contradiction and transitions to `CONFLICT_DETECTED` rather than hallucinating an answer.
- **Weaknesses:** Relies on registered known conflict pairings and regex numerical discrepancy patterns rather than an automated zero-shot NLI contradiction model.

### 2.4 Decision-Support Workflow & Human Approval Gate
- **Strengths:** Strictly enforces a human approval boundary. The agent cannot self-authorize expenditures, dispatch external API webhooks, or finalize decisions without an explicit human sign-off (`APPROVED`/`REJECTED`). Audit trail is preserved in `records.json`.
- **Weaknesses:** Proposals are evaluated against hardcoded policy constants ($50,000 cap, 15% reserve buffer) directly in Python code rather than reading dynamic rules from a knowledge graph or policy engine.
