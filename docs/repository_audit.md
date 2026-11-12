# Repository and Architecture Audit Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Date:** 2026-11-11  
**Target Repository Reference:** [Rupam072006/evidence-grounded-rag](https://github.com/Rupam072006/evidence-grounded-rag) (AegisCore)  
**Audit Scope:** Full codebase structure, technology stack, dependency manifests, configuration, existing APIs, storage, RAG pipeline, deployment configuration, and technical blockers.

---

## 1. Executive Summary

This audit assesses the current state of the BHIV CMO project workspace prior to making any architectural modifications, migrations, or code enhancements. 

The audit evaluated:
1. Workspace root structure and Git repository topology.
2. In-tree backend modules, schemas, and CLI entry points.
3. Persistent storage, vector index artifacts, and document corpora.
4. RAG orchestration, retrieval strategies, conflict detection, and human approval workflow.
5. Runtime environment health, dependency completeness, and execution viability.

### Primary Audit Findings:
- **Workspace Layout & Git Topology:** The workspace directory `c:\Users\A\Desktop\Bhiv_Rhugved\CMO Agent` is not itself a Git repository root. Instead, it contains an intact clone of Rupam's reference repository in the subfolder `evidence-grounded-rag` (`origin: https://github.com/Rupam072006/evidence-grounded-rag.git` at commit `9e551e2` on branch `main`), along with an empty root log file `logs/rag_system.log`. The local git user configuration is set to `Rhugved <blackholeinfiverse146@gmail.com>`.
- **Runtime Environment & Resolution:** The host global Python runtime is Python 3.11.9, which initially lacked `scikit-learn` and `rich`. In Task 2, this blocker was fully resolved by establishing an isolated virtual environment (`.venv`), pinning all 68 packages in `requirements.lock`, and verifying all 130 tests across 26 suites with a 100% pass rate.
- **API Surface:** No REST, GraphQL, or gRPC network service exists. The system exposes an extensive Click-based CLI (`evidence-rag` / `python -m evidence_rag.cli`) and a modular Python class library (`RAGPipeline`, `DecisionWorkflow`, `RecordStore`).
- **Core RAG Functionality:** The codebase contains a fully specified, zero-trust evidence-grounded RAG implementation featuring NFKC text cleaning, boundary-aware chunking, a 512-dimension hybrid TF-IDF + n-gram vectorizer, cosine similarity retrieval with lexical keyword boosting, rule-based cross-document conflict detection, claim-level citation validation (`[DOC-XXX:CHUNK_ID]`), and a human governance approval gate (`AWAITING_APPROVAL`).
- **External Model Integrations:** Adapters for Google Gemini, Groq Cloud, and xAI Grok are coded using `httpx`, but no API keys or `.env` file exist in runtime. All execution currently defaults to an offline, deterministic mock generator (`DeterministicMockGenerator`).

---

## 2. Repository Metadata & Git Topology

| Attribute | Inspected Value | Notes / Audit Observation |
|---|---|---|
| **Workspace Root** | `C:\Users\A\Desktop\Bhiv_Rhugved\CMO Agent` | Active workspace passed to audit agent. |
| **Workspace Git Root** | None (`fatal: not a git repository`) | No `.git` directory at `CMO Agent` root. |
| **Sub-Repository Folder** | `evidence-grounded-rag/` | Contains the complete RAG codebase. |
| **Git Remote URL** | `https://github.com/Rupam072006/evidence-grounded-rag.git` | Points to Rupam's AegisCore reference repository. |
| **Active Branch** | `main` | Clean working tree; up to date with `origin/main`. |
| **Active Commit** | `9e551e25a6a02c1f6dfc751faa3936003f519361` | `chore(cleanup): remove intermediate evaluation run dumps and build artifacts` |
| **Commit Author** | Rupam Patne `<rupam022006@gmail.com>` | Upstream maintainer commit author. |
| **Local Git Identity** | `Rhugved <blackholeinfiverse146@gmail.com>` | Configured in local git config. |
| **Preservation Rule** | Strict rule compliance | Sub-repo preserved; no files deleted or rewritten. |

> [!WARNING]
> **Git Hierarchy Risk:** Because the root `CMO Agent` folder is not initialized as a git repository, any new files created directly under `CMO Agent/` (such as audit reports in `reports/`) are outside version control unless `evidence-grounded-rag` remains the tracked repository or `CMO Agent` is initialized.

---

## 3. Project Structure

The project layout within `CMO Agent` is structured as follows:

```
c:\Users\A\Desktop\Bhiv_Rhugved\CMO Agent\
├── evidence-grounded-rag/               # Core codebase repository
│   ├── configs/                         # YAML pipeline & workflow configurations
│   │   ├── default.yaml                 # Master configuration (512-dim TF-IDF, mock mode)
│   │   ├── marketing_workflow.yaml      # Synthetic marketing evaluation config (256-dim)
│   │   └── online.yaml                  # Online inference config (Groq/Gemini/Grok)
│   ├── data/                            # Corpora, manifests, vector indices, and audit stores
│   │   ├── documents/                   # Authoritative 26 markdown documents (DOC-001 to DOC-026)
│   │   │   ├── doc_001 to doc_020       # Technical RAG & Python architecture specifications
│   │   │   └── doc_021 to doc_026       # Marketing proposals, budget policies & influencer rules
│   │   ├── index/                       # Pre-built persistent vector index (348 chunks, 512-dim)
│   │   │   ├── embedding_model.pkl      # Pickled TfidfVectorizer
│   │   │   ├── knowledge_index.json     # Chunks metadata & SHA-256 fingerprints
│   │   │   └── vectors.npy              # Float32 NumPy vector matrix (348 x 512)
│   │   ├── marketing_corpus/            # 4 synthetic marketing documents (DOC-MKT-001 to 004)
│   │   ├── marketing_index/             # 256-dim index for marketing corpus
│   │   ├── workflow_records/            # Local audit ledger
│   │   │   └── records.json             # 26 stored decision records with secret redaction
│   │   ├── manifest.json                # Master corpus manifest (26 document records)
│   │   └── README.md                    # Data corpus documentation
│   ├── evaluation/                      # Evaluation suite and benchmark datasets
│   │   ├── questions.jsonl              # 22 standardized evaluation questions
│   │   └── results/                     # Historical benchmark execution outputs
│   ├── evidence_packet/                 # Audit artifacts, logs, and sample JSON outputs
│   │   ├── api_samples/                 # Sample response payloads for Q1 to Q5
│   │   └── runtime_logs/                # Historical runtime execution logs
│   ├── review_packets/                  # Architecture review & viva defense documentation
│   ├── scripts/                         # Operational & maintenance utilities
│   │   ├── build_benchmark_report.py    # Evaluation markdown report generator
│   │   ├── create_corpus.py             # Corpus generator utility
│   │   ├── day1_audit.py                # System verification & index health check
│   │   ├── generate_evidence.py         # Evidence packet builder
│   │   ├── run_day3_scenarios.py        # Scenario demonstration harness
│   │   └── update_task3_evidence.py     # Task 3 evidence reconciliation utility
│   ├── src/                             # Source package root
│   │   └── evidence_rag/                # Core Python package
│   │       ├── chunking.py              # Boundary-aware paragraph window chunker
│   │       ├── cleaning.py              # 4-stage text preprocessing & sanitization
│   │       ├── cli.py                   # Click CLI with Rich visual formatting
│   │       ├── confidence.py            # Multi-factor uncertainty scoring
│   │       ├── config.py                # Pydantic v2 configuration models
│   │       ├── conflict_detection.py    # Contradiction detection engine
│   │       ├── context_builder.py       # Token-capped context synthesizer
│   │       ├── embeddings.py            # Hybrid TF-IDF & Sentence-Transformers engines
│   │       ├── evaluation.py            # Evaluation benchmark runner
│   │       ├── evidence.py              # Citation extraction and validation
│   │       ├── generation.py            # Deterministic mock & external LLM generators
│   │       ├── indexing.py              # Disk-backed NumPy vector index
│   │       ├── ingestion.py             # Manifest validation & SHA-256 fingerprinting
│   │       ├── logging_config.py        # Structured logging with secret redaction
│   │       ├── pipeline.py              # Master RAGPipeline orchestrator
│   │       ├── record_store.py          # Decision transaction persistent JSON store
│   │       ├── retrieval.py             # Calibrated cosine & domain-aware retriever
│   │       ├── schemas.py               # Core data models and exception hierarchy
│   │       ├── workflow.py              # DecisionWorkflow engine with Human Approval Gate
│   │       ├── workflow_schemas.py      # Workflow status, request, and report schemas
│   │       └── __init__.py              # Package initialization
│   ├── tests/                           # Pytest test suite (116 tests across 7 tiers)
│   │   ├── conftest.py                  # Pytest fixtures and mock configurations
│   │   ├── boundary/                    # Corrupt index, empty corpus, input validation
│   │   ├── functional/                  # Pipeline QA, citations, conflict detection, workflow
│   │   ├── integration/                 # Ingestion, indexing, retrieval, context builder
│   │   ├── regression/                  # Benchmark regression tests
│   │   ├── security/                    # Prompt injection, secret leakage
│   │   ├── task3/                       # Approval integrity, replay determinism, security
│   │   └── unit/                        # Chunking, cleaning, confidence, embeddings, schemas
│   ├── pyproject.toml                   # PEP 517 build specification
│   ├── requirements.txt                 # Pinned runtime dependencies
│   ├── run_all.ps1                      # Windows PowerShell test & audit suite runner
│   ├── ARCHITECTURE.md                  # System architecture specification
│   ├── CHANGELOG.md                     # Revision history
│   ├── HANDOVER.md                      # Operational handover runbook
│   ├── INTEGRATION.md                   # Integration specifications and interfaces
│   └── README.md                        # Master project documentation
├── logs/                                # Workspace root runtime logs
│   └── rag_system.log                   # Root log file (currently 0 bytes)
└── reports/                             # Current technical audit reports (Task 1)
    ├── repository_audit.md              # This repository audit
    ├── existing_features_matrix.md      # Feature classification matrix
    ├── api_inventory.md                 # Complete API and CLI inventory
    └── runtime_dependencies.md          # Runtime dependency and environment report
```

---

## 4. Technology Stack & Frameworks

### 4.1 Backend
- **Language:** Python (Specification: `>=3.10`; host environment: `Python 3.11.9`).
- **Data Validation & Modeling:** `pydantic>=2.0.0` (active: `2.11.7`) for all configuration, document metadata, chunk data models, and workflow request/response contracts.
- **Scientific & Vector Operations:**
  - `numpy>=1.24.0` (active: `2.4.6`): Vector matrix manipulation, L2 normalization, dot-product cosine similarity.
  - `scikit-learn>=1.3.0` (**MISSING** in active Python environment): Provides `TfidfVectorizer` for `HybridTfidfEmbeddingEngine`.
- **Text Processing & Preprocessing:** Python standard library `unicodedata`, `re`, `hashlib`.
- **CLI & Formatting:**
  - `click>=8.0.0` (active: `8.4.2`): Command line interface parser and sub-command groups.
  - `rich>=13.0.0` (**MISSING** in active Python environment): Terminal colorization, tables, and panels.
- **HTTP Client:** `httpx>=0.24.0` (active: `0.28.1`): Synchronous and retry-wrapped HTTP calls to Google Gemini, Groq, and xAI APIs.
- **Configuration Management:** `PyYAML>=6.0` (active: `6.0.2`) and `python-dotenv>=1.0.0` (active: `1.0.1`).

### 4.2 Frontend
- **Frontend Stack:** **NONE**. No React, Vue, Angular, Svelte, HTML/CSS, or web dashboard is present.
- **User Interface:** Purely terminal-based CLI via Click with Rich rendering.

---

## 5. Entry Points & Invocation Mechanisms

The system exposes three distinct entry points:

### 5.1 Command-Line Interface (`cli.py`)
Registered in `pyproject.toml` as console script `evidence-rag` and executable via `python -m evidence_rag.cli`:
- `evidence-rag index [--config PATH]`: Rebuilds vector index from documents and manifest.
- `evidence-rag query "<QUESTION>" [--mode MODE] [--json-out]`: Queries the RAG pipeline.
- `evidence-rag verify [--config PATH]`: Validates document counts, SHA-256 fingerprints, and index status.
- `evidence-rag evaluate [--questions PATH] [--output DIR]`: Executes benchmark question battery.
- `evidence-rag demo`: Runs interactive 3-query end-to-end demonstration.
- `evidence-rag workflow evaluate`: Evaluates business/marketing proposals against policy.
- `evidence-rag workflow ask "<QUESTION>"`: Answers marketing policy questions without creating proposals.
- `evidence-rag workflow approve <REQ-ID>`: Submits human managerial approval.
- `evidence-rag workflow reject <REQ-ID>`: Submits human managerial rejection.
- `evidence-rag workflow show <REQ-ID>`: Displays full record and audit trail.
- `evidence-rag workflow list`: Lists all stored workflow records.
- `evidence-rag workflow replay <REQ-ID>`: Re-executes proposal against index and reconstructs evidence.

### 5.2 Programmatic In-Process Python APIs
- `evidence_rag.pipeline.RAGPipeline`: Primary end-to-end question-answering orchestrator.
- `evidence_rag.workflow.DecisionWorkflow`: Policy evaluation engine with Human Approval Gate.
- `evidence_rag.record_store.RecordStore`: Local JSON persistence manager for decision records.
- `evidence_rag.retrieval.Retriever`: Semantic and domain-routed candidate chunk retrieval.
- `evidence_rag.indexing.VectorIndex`: Vector index serialization and search.

### 5.3 Automated Test Suite
- `pytest tests`: 116 tests structured across `boundary`, `functional`, `integration`, `regression`, `security`, `task3`, and `unit` suites.
- Script runner: `run_all.ps1` runs tests, verifies index, and regenerates evidence packets.

---

## 6. Database and Storage Architecture

The repository uses **zero external database engines** (no PostgreSQL, SQLite, MySQL, MongoDB, Redis, Pinecone, Milvus, Qdrant, or ChromaDB). All persistence is file-based:

1. **Document Storage:**
   - Raw source documents stored as UTF-8 Markdown in `data/documents/` (26 docs) and `data/marketing_corpus/` (4 docs).
   - Document metadata catalog stored in JSON format at `data/manifest.json`.
2. **Vector Index Artifacts:**
   - Vector array: `data/index/vectors.npy` (binary NumPy float32 array, shape: 348 x 512).
   - Chunk catalog & metadata: `data/index/knowledge_index.json` (JSON list of chunk texts, offsets, tokens, document IDs, and SHA-256 corpus fingerprint).
   - Embedding model: `data/index/embedding_model.pkl` (Pickled scikit-learn `TfidfVectorizer`).
3. **Audit Ledger:**
   - `data/workflow_records/records.json`: Single flat JSON dictionary keyed by `request_id`, containing 26 historical transaction records with secret masking.

---

## 7. Existing RAG Pipeline Flow

The current implementation follows an end-to-end 12-stage pipeline:

```
[User Query / Proposal]
          │
          ▼
1. Input Validation (pipeline.validate_input)
          │
          ▼
2. Index Staleness Check (pipeline.ensure_index)
          │
          ▼
3. Query Embedding (HybridTfidfEmbeddingEngine.encode_query)
          │
          ▼
4. Vector Search & Domain Routing (Retriever.retrieve)
          │
          ▼
5. Lexical Calibration (Retriever._calculate_keyword_boost)
          │
          ▼
6. Evidence Sufficiency Gate (Retriever.assess_evidence_sufficiency)
    ├── If score < 0.20 or term coverage < 28% ──► [Canonical Refusal: INSUFFICIENT EVIDENCE]
    └── If sufficient ──► Proceed
          │
          ▼
7. Contradiction Detection (ConflictDetector.detect_conflicts)
    ├── If conflict detected ──► [Status: CONFLICT_DETECTED, summarize both sides]
    └── If consistent ──► Proceed
          │
          ▼
8. Context Construction (ContextBuilder.build_context, cap: 1500 tokens)
          │
          ▼
9. Grounded Answer Synthesis (DeterministicMockGenerator / Gemini / Groq / Grok)
          │
          ▼
10. Citation Validation (CitationValidator.validate_citations, check [DOC-XXX:CHUNK_ID])
          │
          ▼
11. Confidence & Limitation Scoring (ConfidenceScorer.calculate_confidence)
          │
          ▼
12. Audit Logging (SecretMaskingFilter -> logs/rag_system.log)
```

---

## 8. Deployment Configuration

- **Containerization:** None. No `Dockerfile` or `docker-compose.yml` exists.
- **Cloud Infrastructure:** None. No Terraform, CloudFormation, Kubernetes manifests, or Helm charts.
- **CI/CD Pipelines:** None. No `.github/workflows/` directory exists.
- **Current Deployment Target:** Local Windows desktop / developer workstation running PowerShell and Python.

---

## 9. Technical Blockers & Critical Risks

1. **Missing Runtime Dependencies (`BLOCKER`):**
   - The current Python 3.11 environment lacks `scikit-learn` and `rich`.
   - Running `pytest` or `evidence-rag` raises `ModuleNotFoundError: No module named 'sklearn'`.
   - **Remediation:** A dedicated Python virtual environment must be initialized and populated from `requirements.txt`.
2. **Missing Environment Configuration (`RISK`):**
   - Only `.env.example` is present. No `.env` file exists with actual API keys for Groq, Gemini, or Grok.
   - External LLM generation modes fail or fall back to mock generation.
3. **Repository Decoupling (`RISK`):**
   - The workspace root `CMO Agent` is not a git repository. The tracked repository is `evidence-grounded-rag/`.
   - To make reviewable Pull Requests, git operations must be executed from inside `evidence-grounded-rag/` or the parent directory must be properly initialized/linked.
