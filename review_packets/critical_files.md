# AegisCore System Critical Files Specification

In accordance with review standards, this document highlights the **three most critical code files** in the repository for reviewer evaluation, explaining their architecture, design decisions, and core invariants.

---

## 1. `src/evidence_rag/pipeline.py` (Master Orchestrator)
- **Role:** Central coordination pipeline unifying all subsystems from input reception to response emission.
- **Why It Matters:**
  - Enforces the strict end-to-end execution lifecycle.
  - Implements early boundary validation, preventing invalid inputs from wasting vector retrieval computation.
  - Houses the evidence sufficiency decision gate that emits canonical refusals when retrieval confidence is inadequate.
  - Guarantees that every query emits a typed `RAGResponse` containing status, citations, evidence passages, confidence, limitations, and latency.
- **Key Code Sections:**
  - `validate_input(query)`: Enforces 3-500 character boundaries and strips control characters.
  - `build_index()`: Sequences ingestion, chunking, embedding, and serialization.
  - `query(user_query)`: Executes the complete multi-stage RAG workflow.

---

## 2. `src/evidence_rag/retrieval.py` (Semantic Retrieval & Evidence Assessment)
- **Role:** High-performance vector candidate search, lexical score calibration, and evidence sufficiency assessment.
- **Why It Matters:**
  - Implements the mathematical bridge between high-dimensional vector representations and textual relevance.
  - Eliminates external database dependencies by performing fast NumPy dot products on unit-normalized vectors.
  - Incorporates lexical re-ranking (+0.08 max boost) to prioritize exact key-term matches over vague semantic proximity.
  - Implements the defensible dual-factor evidence sufficiency mechanism: checking both score floor (0.20) and query term coverage across retrieved context (>=28%) to prevent false-positive answers on out-of-domain queries.
- **Key Code Sections:**
  - `retrieve(query, top_k)`: Candidate dot-product scoring and ranking.
  - `_calculate_keyword_boost()`: Exact keyword calibration.
  - `assess_evidence_sufficiency()`: Sufficiency floor and term coverage evaluation.

---

## 3. `src/evidence_rag/generation.py` (Grounded Generation & Provider Resilience)
- **Role:** Grounded factual answer generation supporting both offline deterministic synthesis and Google Gemini GenAI.
- **Why It Matters:**
  - Implements the zero-trust grounding mandate: generative output must originate solely from retrieved context passages.
  - Provides complete insulation against external API outages, rate limits, or project permission denials (`403 PERMISSION_DENIED`) via `DeterministicMockGenerator`.
  - Implements automated conflict formatting when contradictions are discovered between sources.
  - Appends verifiable claim-level citations in the required `[DOCUMENT_ID:CHUNK_ID]` format.
- **Key Code Sections:**
  - `DeterministicMockGenerator.generate_answer()`: Factual extraction from retrieved chunks with claim citations.
  - `GeminiGenerator.check_availability()`: Non-crashing preflight check for API key access.
  - `GeminiGenerator.generate_answer()`: Strict system prompting with temperature=0.0.
