# AegisCore Evidence-Grounded RAG System — Handover Document

## 1. Project Purpose & Current State

- **Project Name:** AegisCore Evidence-Grounded RAG System
- **Repository Corpus:** `Rupam072006/evidence-grounded-rag`
- **Architecture Philosophy:** Zero-trust evidence grounding, claim-level attribution, anti-hallucination sufficiency floors, and automated conflict detection.
- **Current State:** Fully operational, tested, and verified.
  - **Knowledge Base:** Exactly 20 standardized knowledge documents in `data/documents/` indexed in `data/manifest.json`.
  - **Vector Index:** 299 chunk passages embedded into 512-dimensional vector space persisted in `data/index/`.
  - **Test Suite:** 46 automated tests passing across 6 tiers in <0.3s.
  - **Evaluation Suite:** 22 benchmark questions covering answerable, multi-document, ambiguous, unanswerable, conflicting, adversarial, and boundary categories.
- **Runtime Environment:** Windows 10/11 (PowerShell), Python 3.10 to 3.13 (verified on Python 3.13.1).

---

## 2. Main Folders and Key Files

```
RAG/
├── configs/
│   └── default.yaml               # Pipeline hyperparameters (top-k, chunk size, floors)
├── data/
│   ├── documents/                 # Exactly 20 knowledge base Markdown documents
│   │   ├── doc_001_python_basics.md to doc_008_sql_basics.md (DOC-001 to DOC-008)
│   │   ├── doc_009_machine_learning_intro.md to doc_012_train_test_split.md (DOC-009 to DOC-012)
│   │   ├── doc_013_embeddings.md to doc_018_evaluation_methods.md (DOC-013 to DOC-018)
│   │   └── doc_019_metadata_management.md, doc_020_evidence_and_citations.md (DOC-019 to DOC-020)
│   ├── index/                     # Persistent index artifacts
│   │   ├── vectors.npy            # Binary matrix of 299 unit-normalized vectors
│   │   ├── knowledge_index.json   # Chunk catalog, metadata, and SHA-256 fingerprints
│   │   └── embedding_model.pkl    # Serialized vectorizer state
│   └── manifest.json              # Authoritative corpus manifest (20 document records)
├── evaluation/
│   ├── questions.jsonl            # 22 standardized evaluation questions
│   └── results/                   # Evaluation execution reports (JSON)
├── src/evidence_rag/              # Core application package
│   ├── ingestion.py               # Manifest validation & SHA-256 fingerprinting
│   ├── cleaning.py                # 4-stage text preprocessing & sanitization
│   ├── chunking.py                # Boundary-aware paragraph chunker (400 chars, 60 overlap)
│   ├── embeddings.py              # Hybrid TF-IDF and neural embedding engines
│   ├── indexing.py                # Persistent vector index management
│   ├── retrieval.py               # Cosine similarity retrieval & sufficiency check
│   ├── context_builder.py         # Context formatting & 1,500 token budget cap
│   ├── conflict_detection.py      # Cross-document contradiction detection (DOC-009 vs DOC-020)
│   ├── generation.py              # Mock, Groq Cloud, and Gemini generators
│   ├── evidence.py                # Regex extraction & runtime citation validator
│   ├── confidence.py              # Multi-factor uncertainty scoring
│   ├── pipeline.py                # Unified RAGPipeline orchestrator
│   └── cli.py                     # Command-line entry points
├── tests/                         # Pytest test suite (46 tests across 6 directories)
├── ARCHITECTURE.md                # System topology and component specification
├── INTEGRATION.md                 # Module interfaces, schemas, and configurations
├── CHANGELOG.md                   # Chronological development and release records
├── HANDOVER.md                    # Operational handover, maintenance, and runbooks
├── README.md                      # Comprehensive user and reviewer manual
├── pyproject.toml                 # Package definition and CLI entry points
└── requirements.txt               # Pinned package dependencies
```

---

## 3. Installation and Execution Runbook

### Step 1: Environment Activation & Package Installation
```powershell
# Open Windows PowerShell in project root
cd C:\Users\rupam\OneDrive\Desktop\RAG

# Install editable package with all runtime dependencies
python -m pip install -e .
```

### Step 2: Rebuilding the Knowledge Base Vector Index
Whenever documents in `data/documents/` are modified or added:
```powershell
evidence-rag index
```
This parses `data/manifest.json`, ingests the 20 documents, chunks them into passages, fits the vectorizer, and serializes the index to `data/index/`.

### Step 3: Verifying System Integrity
```powershell
evidence-rag verify
```
This confirms that exactly 20 documents are present, all 8 metadata fields are valid, file hashes match, and the index contains all chunks.

### Step 4: Running Interactive Queries
```powershell
# Answerable factual query
evidence-rag query "What character encoding is mandatory for all incoming documents in AegisCore?"

# Cross-document conflict query (DOC-009 vs DOC-020)
evidence-rag query "What is the default production top-k parameter and candidate pool size for the retrieval service?"

# Unsupported out-of-domain query (triggers canonical refusal)
evidence-rag query "What is the secret recipe for Aunt May's chocolate chip cookies?"
```

### Step 5: Executing the Automated Test Suite (46 Tests)
```powershell
python -m pytest tests -q
```
All 46 tests should pass in under 1 second.

### Step 6: Executing the Evaluation Benchmark
```powershell
# Run benchmark in deterministic mock mode (offline, reproducible, zero API cost)
$env:RAG_GENERATION_MODE="mock"
evidence-rag evaluate
```

---

## 4. Configuration Requirements

The system reads settings from `configs/default.yaml` and environment variables:
- `RAG_GENERATION_MODE`: Set to `mock` (default for tests/benchmarks) or `groq` / `gemini` for live online LLM mode.
- `GROQ_API_KEY`: Required only when running with Groq Cloud. Store in `.env` (never commit secrets to version control).
- `GROQ_MODEL`: Model identifier on Groq Cloud (e.g., `openai/gpt-oss-120b`).
- `GEMINI_API_KEY`: Required only when running with Google Gemini.

---

## 5. Known Limitations & Unresolved Issues

1. **Groq Cloud Rate Limiting on Batch Bursts:**
   The Groq on-demand free tier enforces an 8,000 Tokens-Per-Minute (TPM) quota. Running all 22 evaluation benchmark questions in rapid succession without throttling causes HTTP 429 rate limit errors for several questions. Use `mock` mode for instant, quota-free evaluations.
2. **Context Window Ceiling:**
   Total prompt context is constrained to 1,500 tokens (approx. 6,000 characters). Queries requiring evidence spanning more than 10 documents will omit lower-scoring passages.
3. **Lexical Reliance in Hybrid TF-IDF:**
   The hybrid embedding engine uses sublinear TF-IDF with character and word n-grams (512 dimensions). While fast and deterministic, highly abstract queries using zero overlapping terms may fail to meet the 28% query term coverage floor.

---

## 6. Recommended Next Steps

1. **Add Request Throttling / Exponential Backoff for Online Cloud Mode:**
   Implement an automated 2-second pacing delay between queries when running batch evaluations against public rate-limited cloud APIs (Groq / Gemini).
2. **Approximate Nearest Neighbor (ANN) Indexing for Scale:**
   For knowledge bases expanding beyond 10,000 chunks, integrate FAISS or HNSWlib into `src/evidence_rag/indexing.py` to maintain sub-millisecond retrieval.
3. **Cross-Encoder Re-Ranking:**
   Add a secondary re-ranking stage using a compact cross-encoder (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) to jointly score query and passage attention before context formatting.
