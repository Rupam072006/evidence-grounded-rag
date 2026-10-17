# Changelog

All notable changes and engineering milestones for the Evidence-Grounded RAG System are documented in this file.

## [1.0.0] - 2026-10-17

### Initial Complete Release (Accelerated Delivery)

#### Added
- **Core Architecture & Repository Structure:**
  - Initialized Git repository and configured `.gitignore` to prevent secrets and cache leaks.
  - Authored `.env.example` with placeholder credentials.
  - Packaged project with `pyproject.toml` and `requirements.txt`.
- **Knowledge Base Corpus:**
  - Authored exactly 20 comprehensive technical Markdown documents in `data/documents/` covering the fictional AegisCore platform.
  - Implemented `data/manifest.json` containing required metadata (`document_id`, `title`, `source`, `source_type`, `version`, `created_at`, `updated_at`, `topic`).
  - Implemented intentional technical contradiction between `DOC-009` (top-k=5, pool=20) and `DOC-020` (top-k=10, pool=50).
- **Core Pipeline Implementation (`src/evidence_rag/`):**
  - `ingestion.py`: Manifest validation, count enforcement (20 docs), and SHA-256 fingerprinting.
  - `cleaning.py`: NFKC Unicode normalization, control character removal, HTML tag stripping, and PII redaction.
  - `chunking.py`: Paragraph-window chunker (400 chars, 60 overlap), orphan fragment merging, and stable `[DOC_ID]-C[SEQ]` IDs.
  - `embeddings.py`: Dual-mode embedding architecture with unit-normalized Hybrid TF-IDF and SentenceTransformers.
  - `indexing.py`: Persistent storage layout (`vectors.npy`, `knowledge_index.json`, `embedding_model.pkl`).
  - `retrieval.py`: Cosine similarity retrieval, keyword calibration, and evidence sufficiency floor checks.
  - `context_builder.py`: 1,500 token budget enforcement and delimiter formatting.
  - `generation.py`: Deterministic mock generation and Google Gemini GenAI integration.
  - `evidence.py`: Claim-level citation extraction and context-validity auditing.
  - `conflict_detection.py`: Contradiction analysis and dual-perspective synthesis.
  - `confidence.py`: Multi-factor confidence scoring with uncertainty disclosures.
  - `pipeline.py`: Unified pipeline orchestrator.
  - `cli.py`: CLI supporting `index`, `query`, `verify`, and `evaluate`.
- **Evaluation Benchmark Suite (`evaluation/`):**
  - Authored `evaluation/questions.jsonl` with 22 distinct evaluation questions covering all 6 mandatory categories.
  - Implemented `evaluation.py` measuring retrieval success, status accuracy, citation validity, and latency.
- **Automated Test Suite (`tests/`):**
  - Created 46 automated tests across unit, integration, functional, boundary, security, and regression tiers.
  - All 46 tests pass in under 0.3 seconds.
- **Evidence & Review Packets (`review_packets/`, `evidence_packet/`):**
  - Generated genuine API samples for real queries.
  - Recorded runtime logs with secret-free filtering.
