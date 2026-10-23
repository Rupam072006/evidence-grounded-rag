# AegisCore Evidence-Grounded RAG System — Handover Document

## 1. Project Purpose & Current State

- **Project Name:** AegisCore Evidence-Grounded RAG System
- **Repository Corpus:** `Rupam072006/evidence-grounded-rag`
- **Architecture Philosophy:** Zero-trust evidence grounding, claim-level attribution, anti-hallucination sufficiency floors, and automated conflict detection.
- **Current State:** Fully operational, tested, and verified.
  - **Knowledge Base:** Exactly 20 standardized knowledge documents in `data/documents/` + 4 marketing workflow policy documents in `data/marketing_corpus/`.
  - **Vector Indices:** Technical index (301 chunks) + Marketing workflow index (22 chunks) persisted in `data/index/` and `data/marketing_index/`.
  - **Test Suite:** 65 automated tests passing across unit, functional, integration, boundary, security, and regression tiers in <0.8s.
  - **Evaluation Suite:** 25 benchmark questions covering answerable, multi-document, ambiguous, unanswerable, conflicting, adversarial, and boundary categories.
  - **Workflow Engine:** `DecisionWorkflow` with human governance approval gate and secret-scrubbed JSON ledger.
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

## 5. Operational Runbooks & Common Tasks

### 5.1 Running the Decision Workflow via CLI
```powershell
# Evaluate a proposal
python -m evidence_rag.cli workflow evaluate --title "..." --proposal "..." --budget 20000

# View pending or approved proposal
python -m evidence_rag.cli workflow show <request_id>

# Submit human approval or rejection
python -m evidence_rag.cli workflow approve <request_id> --decision APPROVED --reviewer "Name" --notes "Audited"

# List all stored records
python -m evidence_rag.cli workflow list
```

### 5.2 Re-Indexing After Corpus Changes
Whenever documents in `data/documents/` or `data/marketing_corpus/` are modified, added, or deleted, AegisCore automatically detects the change via SHA-256 corpus fingerprinting on the next query. To force an immediate manual re-index:
```powershell
python -m evidence_rag.cli index
```

---

## 6. Known Limitations & Production Roadmap

1. **Multi-Hop Synthesis Under Single-Pass Retrieval:**
   Queries spanning multiple disparate documents (e.g. Q11 connecting chunking with token budgets) retrieve both source documents, but individual chunk term overlap can fall below the strict single-passage sufficiency floor (28%). The system chooses canonical refusal over hallucination. Recommendation: Implement sub-query decomposition.
2. **Local Record Store Concurrency:**
   Workflow proposal records are stored in `data/workflow_records/records.json` using atomic disk write-replace. Suitable for single-instance or small team operations. For large-scale distributed deployments, migrate `RecordStore` to an ACID relational database (e.g., PostgreSQL).
3. **Automated Rate Limit Handling (Resolved in Task 2):**
   Groq Cloud HTTP 429 rate limits are now automatically mitigated via a 3-attempt exponential backoff retry mechanism in `OpenAICompatibleGenerator`.

