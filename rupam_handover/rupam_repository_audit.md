# WP1: Repository Audit Deliverable — Evidence-Grounded RAG (AegisCore)

**Document:** `rupam_repository_audit.md` / `01_repository_audit.md`  
**Author / Auditor:** Senior Python Engineer, RAG Architect and Technical Auditor  
**Assignment Reference:** *BHIV / BHQ CMO Agent — Technical Execution Assignment v2 (10 November 2026)*  
**Accountable CMO Product Owner:** Prateek  
**Handover Subject:** Rupam Patne (Marketing Intelligence RAG)  
**Date of Audit:** 2026-11-13  
**Audit Standard:** READ-ONLY, Non-destructive, Evidence-Grounded Verification  

---

## 1. Executive Summary & Governance Context

Under the *CMO Agent Technical Execution Assignment v2*, the accountable CMO Product Owner is **Prateek** (superseding earlier references). As part of the takeover of Rupam Patne's responsibilities for the Marketing Intelligence RAG workstream, this report delivers **Work Package 1 (WP1): Repository Audit**.

### Key Audit Findings
1. **Repository Identity & Staging Layout:**  
   The outer folder `C:\Pratik_Bhuwad\CMO_Agent` is not a Git repository. The canonical Git repository is located at `C:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main`, tracking `origin https://github.com/Rupam072006/evidence-grounded-rag.git` on branch `main` at commit `9e551e2`.
2. **System Characterization:**  
   AegisCore is a modular, standalone Python package (`evidence_rag`) and Click CLI application (`evidence-rag`). It is **not** an HTTP web microservice (zero REST routes, zero ASGI/WSGI servers, zero port bindings) and **not** an autonomous multi-agent execution loop. It is a specialized, zero-trust knowledge retrieval and compliance-checking policy kernel.
3. **Core Algorithmic Foundations:**  
   The system implements a 4-stage text cleaning pipeline with PII/secret scrubbing, boundary-aware paragraph chunking (400-char window, 60-char overlap), 512-dimensional unit-norm TF-IDF vector indexing, domain-routed retrieval across 7 logical categories with a dual sufficiency floor ($\text{score} \ge 0.20$ and $\ge 28\%$ query term coverage), automated cross-document contradiction interception, claim-level citation validation (`[DOC-ID:CHUNK-ID]`), and an immutable human governance gate (`AWAITING_APPROVAL`) halting automated spend execution.
4. **Resolution of Test Count Discrepancies:**  
   Rupam's documentation (`README.md`, `HANDOVER.md`, `TASK3_FINAL_REPORT.md`) claims **116 passed tests** across **24 test suites**. The actual codebase contains **25 test files** and **126 test cases**. In commit `2178225`, Rupam added `test_workflow_cli_separation.py` (10 tests) and recorded 126 passed tests in `clean_test_output.txt` and `test_execution_summary.json`, but left outdated documentation badges.
5. **Runtime Environment Blocker:**  
   In the local environment (Python 3.11.9 on Windows), unpinned dependency specification (`numpy>=1.24.0` in `pyproject.toml`) resolves to NumPy 2.4.6, causing an ABI mismatch with compiled SciPy 1.11.4 C-extensions, crashing `pytest` during `conftest.py` loading. Isolation in a dedicated virtual environment with `numpy<2.0.0` is required for WP2.
6. **Ecosystem Seam Reality:**  
   There is **zero code, zero imports, zero configuration, and zero client hooks** for the BHIV enterprise ecosystem (**BIQOS, TANTRA, VAJRA, or MASTERDB**). All storage is local flat-file storage (`vectors.npy`, `knowledge_index.json`, `records.json`), and approval reviewer identities are plain unverified text strings.

---

## 2. Repository Identity and Working Tree Topology

### 2.1 Git Verification Matrix
| Dimension | Verified State | Audit Evidence |
|---|---|---|
| **Outer Workspace** | `C:\Pratik_Bhuwad\CMO_Agent` | `git rev-parse --is-inside-work-tree` returned `fatal: not a git repository`. Outer folder serves as handover/audit staging workspace. |
| **Canonical Git Repository Root** | `C:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main` | Contains `.git` directory (`13-11-2026 12:03 <DIR> .git`). |
| **Upstream Git Remote** | `origin https://github.com/Rupam072006/evidence-grounded-rag.git` (fetch & push) | `git remote -v` executed in inner repository. |
| **Active Branch** | `main` | `git status` reports: `On branch main. Your branch is up to date with 'origin/main'.` |
| **Current Commit Hash** | `9e551e2` | `git log -n 1 --oneline` -> `9e551e2 chore(cleanup): remove intermediate evaluation run dumps and build artifacts`. |
| **Commit Predecessors** | `82e50d8`, `213ef20`, `2178225`, `e816600` | Historical progression from Task 3 verification through demo documentation and cleanup. |
| **Working Tree Status** | Clean (1 untracked file: `file_tree.txt`) | Zero modified, zero staged, zero deleted files. |

### 2.2 Workspace Directory Layout
```
C:\Pratik_Bhuwad\CMO_Agent\
│
├── audit_reports/                               # 9 prior audit reports from 2026-11-07
│   ├── API_AND_INTEGRATION_AUDIT.md
│   ├── CMO_AGENT_REUSE_RECOMMENDATIONS.md
│   ├── DATABASE_AND_RAG_AUDIT.md
│   ├── EXECUTIVE_SUMMARY.md
│   ├── MASTER_AUDIT_REPORT.md
│   ├── REPOSITORY_STRUCTURE.md
│   ├── SECURITY_AND_RISK_AUDIT.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   └── TEST_AND_RUNTIME_AUDIT.md
│
├── CMO_AGENT_BASELINE_AND_DELIVERY_PLAN.md      # Team roster, baseline, and convergence roadmap
├── file_tree.txt                                # Workspace file tree dump
├── logs/                                        # Workspace log directory
│
├── evidence-grounded-rag-main/                  # CANONICAL APPLICATION REPOSITORY (Git root)
│   ├── .env.example                             # Template environment variables
│   ├── .gitignore                               # Ignores .env, .venv, __pycache__, test dumps
│   ├── ARCHITECTURE.md                          # Technical architecture specification
│   ├── CHANGELOG.md                             # Release notes and chronological changes
│   ├── configs/                                 # Pipeline YAML configurations
│   │   ├── default.yaml                         # Master 26-doc pipeline configuration
│   │   ├── marketing_workflow.yaml              # Synthetic marketing workflow configuration
│   │   └── online.yaml                          # Online cloud provider configuration
│   ├── data/                                    # Datasets, indices, and audit records
│   │   ├── documents/                           # Exactly 26 knowledge and policy documents
│   │   ├── index/                               # Primary 348-chunk vector index (512-dim)
│   │   ├── manifest.json                        # Authoritative 26-document corpus manifest
│   │   ├── marketing_corpus/                    # 4 specialized marketing documents + manifest
│   │   ├── marketing_index/                     # 22-chunk marketing index (256-dim)
│   │   └── workflow_records/                    # Persistent proposal ledger (records.json)
│   ├── evaluation/                              # Benchmark questions and run reports
│   │   ├── questions.jsonl                      # 25 standardized benchmark questions
│   │   └── results/                             # Evaluation execution JSON reports
│   ├── evidence_packet/                         # 19 Task 3 audit and verification artifacts
│   ├── pyproject.toml                           # Package definition and build configuration
│   ├── requirements.txt                         # Pinned pip dependency list
│   ├── run_all.ps1                              # PowerShell automation script
│   ├── scripts/                                 # Helper benchmark and evidence scripts
│   ├── src/evidence_rag/                        # Core application source package (21 modules)
│   └── tests/                                   # Pytest test suite (25 test files, 126 cases)
│
└── rupam_handover/                              # Handover documentation and test artifacts
    ├── 01_repository_audit.md                   # This audit report (WP1 deliverable)
    └── evidence/                                # Destination for test logs and evaluations
```

---

## 3. Project Specifications and Dependencies

### 3.1 `pyproject.toml` Specification
Inspected `evidence-grounded-rag-main/pyproject.toml` (Lines 1-50):
- **Build System:** `setuptools>=61.0`, `setuptools.build_meta`.
- **Package Identity:** Name `evidence-grounded-rag`, version `1.0.0`, author `Rupam Patne`.
- **Python Version Requirement:** `requires-python = ">=3.10"`.
- **Core Runtime Dependencies:**
  - `pydantic>=2.0.0` (Schemas and data validation)
  - `PyYAML>=6.0` (Configuration loading)
  - `numpy>=1.24.0` (Vector operations; **unpinned upper bound**)
  - `scikit-learn>=1.3.0` (TF-IDF vectorizer and SVD)
  - `python-dotenv>=1.0.0` (Environment variable management)
  - `click>=8.0.0` (CLI framework)
  - `rich>=13.0.0` (Console formatting and tables)
  - `httpx>=0.24.0` (HTTP client for cloud LLM APIs)
- **Optional Dependency Groups:**
  - `ml`: `sentence-transformers>=2.2.0`, `torch>=2.0.0`
  - `gemini`: `google-genai>=0.1.0`
  - `test`: `pytest>=7.4.0`, `pytest-cov>=4.1.0`
- **CLI Entry Point:** `evidence-rag = "evidence_rag.cli:main"`.
- **Pytest Configuration:**
  - `pythonpath = ["src"]`
  - `testpaths = ["tests"]`
  - `python_files = ["test_*.py"]`
  - `addopts = "-v --tb=short"`

### 3.2 `requirements.txt` Specification
Inspected `evidence-grounded-rag-main/requirements.txt` (Lines 1-17):
- Explicitly declares runtime dependencies matching `pyproject.toml` plus `sentence-transformers>=2.2.0`, `google-genai>=0.1.0`, `pytest>=7.4.0`, and `pytest-cov>=4.1.0`.

### 3.3 Identified Environment / Dependency Blocker
- **NumPy 2.x ABI Conflict:** In modern Python environments (e.g. host Python 3.11.9), running unpinned `pip install` resolves to `NumPy 2.4.6`. However, installed binary wheels for `scipy 1.11.4` and `scikit-learn 1.3.2` were compiled against the NumPy 1.x C-API.
- **Symptom:** Importing `evidence_rag` (which loads `sklearn.feature_extraction.text.TfidfVectorizer` -> `scipy.sparse`) immediately raises:
  `ImportError: numpy.core.multiarray failed to import` / `AttributeError: _ARRAY_API not found`.
- **Mitigation for WP2:** Must isolate a virtual environment pinned to `numpy>=1.24.0,<2.0.0`.

---

## 4. Architecture and Entry Points

### 4.1 Architectural Topology
AegisCore is structured around a **zero-trust evidence grounding paradigm**:
- Generative answering is permitted only when retrieved context exceeds mathematically defined sufficiency thresholds.
- External documents and user queries are treated as untrusted data inputs, precluding prompt injection escapes.
- Every factual assertion carries verifiable citations (`[DOCUMENT_ID:CHUNK_ID]`) validated against runtime retrieval context.
- When authoritative documents present conflicting parameters, the architecture surfaces both claims rather than arbitrarily favoring the higher-ranked passage.
- For business proposals, the system halts execution at a **Mandatory Human Approval Gate (`AWAITING_APPROVAL`)**, prohibiting automated external financial spend.

### 4.2 Application Entry Points
1. **Command-Line Interface (`src/evidence_rag/cli.py`):**
   - Implemented using Click and Rich.
   - Core subcommands:
     - `evidence-rag index [--config <path>]`: Ingests corpus and rebuilds vector index.
     - `evidence-rag query "<question>" [--mode mock|groq|grok|gemini] [--json-out]`: Interactive RAG question answering.
     - `evidence-rag verify [--config <path>]`: Validates document counts, metadata completeness, SHA-256 hashes, and index chunk counts.
     - `evidence-rag evaluate [--questions <path>] [--output <dir>]`: Runs the 25-question evaluation benchmark.
     - `evidence-rag demo`: Runs an offline 3-query showcase.
     - `evidence-rag workflow evaluate [--preset <name>] [--proposal <text>] [--budget <float>]`: Evaluates a proposal against policy and pauses at `AWAITING_APPROVAL`.
     - `evidence-rag workflow ask "<question>"`: Answers policy questions without prompting for budget or creating ledger records.
     - `evidence-rag workflow approve <request_id> --reviewer <name> --notes <text>`: Records human approval.
     - `evidence-rag workflow reject <request_id> --reviewer <name> --notes <text>`: Records human rejection.
     - `evidence-rag workflow show <request_id>`: Displays audit trail and recommendation for a proposal.
     - `evidence-rag workflow list`: Lists all proposals in the audit ledger.
     - `evidence-rag workflow replay <request_id>`: Reconstructs a historical proposal against the current corpus.
2. **Programmatic Python API:**
   - `RAGPipeline.query(user_query: str) -> RAGResponse` (`src/evidence_rag/pipeline.py#L140-L234`)
   - `DecisionWorkflow.evaluate_proposal(request: WorkflowRequest) -> WorkflowRecord` (`src/evidence_rag/workflow.py#L94-L216`)
   - `DecisionWorkflow.submit_approval(request_id, decision, reviewer, notes) -> WorkflowRecord` (`src/evidence_rag/workflow.py#L336-L363`)
   - `DecisionWorkflow.ask_policy_question(question: str) -> RAGResponse` (`src/evidence_rag/workflow.py#L74-L77`)
3. **HTTP REST API:**
   - **NOT IMPLEMENTED.** An exhaustive search confirmed zero web framework imports, zero routes, and zero server sockets.

---

## 5. In-Depth Module Inspection (`src/evidence_rag/`)

| Module | Lines | Class / Function | Responsibility & Mechanism |
|---|---|---|---|
| [`schemas.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/schemas.py) | 130 | `ResponseStatus`, `DocumentMetadata`, `Document`, `Chunk`, `RetrievedChunk`, `Citation`, `ConflictEvidence`, `RAGResponse`, `RAGException` | Master Pydantic models, status enums (`ANSWERED`, `INSUFFICIENT_EVIDENCE`, `CONFLICT_DETECTED`, `INVALID_INPUT`, `GENERATION_UNAVAILABLE`, `INDEX_UNAVAILABLE`), and typed exception hierarchy. |
| [`workflow_schemas.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/workflow_schemas.py) | 96 | `WorkflowStatus`, `WorkflowRequest`, `VerifiedFact`, `RecommendationReport`, `ApprovalDecision`, `WorkflowRecord` | Data contracts for decision-support: request modeling, 4-way separation of recommendation components (facts, inferences, assumptions, unknowns), approval records, and full audit logs. |
| [`config.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/config.py) | 140 | `load_config()`, `RAGConfig` | Parses YAML configuration files (`configs/default.yaml`, `configs/marketing_workflow.yaml`). Integrates `.env` variables via `python-dotenv` with `override=False` to preserve active environment settings. |
| [`ingestion.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/ingestion.py) | 110 | `IngestionEngine` | Discovers documents in `data/manifest.json`. Validates all 8 mandatory metadata fields (`document_id`, `title`, `source`, `source_type`, `version`, `created_at`, `updated_at`, `topic`). Computes cryptographic SHA-256 hash per file. Enforces exact document count (26). |
| [`cleaning.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/cleaning.py) | 61 | `TextCleaner`, `clean_text()` | 4-stage pipeline: (1) Unicode NFKC normalization; (2) Script/HTML tag regex stripping; (3) Control character removal (preserving `\n`, `\t`, `\r`); (4) Regex PII/secret redaction (`[REDACTED_EMAIL]`, `[REDACTED_KEY]`); (5) Whitespace consolidation. |
| [`chunking.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/chunking.py) | 119 | `Chunker` | Boundary-aware sliding window chunker. Target: 400 characters, overlap: 60 characters. Prioritizes paragraph double-newlines and sentence terminal punctuation. Merges orphan fragments $<40$ chars. Generates stable IDs `[DOC-ID]-C[001]`. |
| [`embeddings.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/embeddings.py) | 167 | `HybridTfidfEmbeddingEngine`, `SentenceTransformerEmbeddingEngine`, `create_embedding_engine()` | Fits scikit-learn `TfidfVectorizer` (512 dimensions, sublinear TF, character/word n-grams 1-2). Enforces strict L2 unit-norm normalization ($\|\mathbf{v}\|_2 = 1.0$), ensuring cosine similarity simplifies to matrix-vector dot product. |
| [`indexing.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/indexing.py) | 172 | `VectorIndex` | Persists vectors to `data/index/vectors.npy` (NumPy binary array), chunk catalog to `data/index/knowledge_index.json`, and vectorizer model to `data/index/embedding_model.pkl`. Implements candidate dot-product search and metadata category filtering. |
| [`retrieval.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/retrieval.py) | 203 | `Retriever` | Vector dot product search. Scans query for domain signals across 7 categories (`python`, `sql`, `machine_learning`, `business_proposal`, `budget_policy`, `marketing_performance`, `business_approval_policy`). Adds keyword boost up to $+0.08$. Applies $0.60\times$ cross-domain pollution guard. Enforces candidate threshold $\ge 0.12$. |
| [`retrieval.py` (Sufficiency)](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/retrieval.py#L181-L203) | - | `assess_evidence_sufficiency()` | Dual sufficiency floor: top candidate score must be $\ge 0.20$ AND query keyword coverage across retrieved context must be $\ge 28\%$. Triggers canonical refusal if either condition fails. |
| [`context_builder.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/context_builder.py) | 48 | `ContextBuilder` | Encloses passages in delimiter envelopes (`=== PASSAGE [ID] === ... === END PASSAGE ===`). Quarantines passages as untrusted text. Implements hard 1,500 token (~6,000 character) context budget cap. |
| [`conflict_detection.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/conflict_detection.py) | 161 | `ConflictDetector` | Intercepts contradictory evidence before generation. Checks registered contradiction pairs: `DOC-009` vs `DOC-020`, `DOC-024` vs `DOC-025`, and `DOC-MKT-002` vs `DOC-MKT-004`. Includes heuristic numeric parameter discrepancy analyzer. Emits `CONFLICT_DETECTED`. |
| [`confidence.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/confidence.py) | 67 | `ConfidenceScorer` | Multi-factor composite score: $\text{Confidence} = 0.50 \cdot \text{TopScore} + 0.30 \cdot \text{MeanTop3} + 0.20 \cdot \text{QueryCoverage}$. Outputs calibrated score and explicit limitations. |
| [`generation.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/generation.py) | 489 | `DeterministicMockGenerator`, `GeminiGenerator`, `GroqGenerator`, `GrokGenerator`, `create_generator()` | Offline: `DeterministicMockGenerator` extracts verbatim sentences from retrieved passages with citations; zero API calls. Live cloud: `GroqGenerator` (`llama-3.3-70b-versatile` with 3-attempt exponential backoff on HTTP 429), `GeminiGenerator` (`gemini-1.5-flash`), `GrokGenerator` (`grok-beta`). |
| [`evidence.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/evidence.py) | 87 | `CitationValidator` | Regex extraction `[\[\u3010](DOC-(?:[A-Za-z0-9]+-)?\d{3})(?:[:-]([A-Za-z0-9\-_]+))?[\]\u3011]`. Confirms every cited document and chunk exists in the candidate retrieval pool. Marks hallucinated citations `is_valid: False`. |
| [`logging_config.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/logging_config.py) | 60 | `SecretMaskingFilter`, `setup_logger()` | Custom logging filter attaching to console and file handlers (`logs/rag_system.log`). Redacts Gemini, Groq, and generic Bearer tokens. |
| [`pipeline.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/pipeline.py) | 234 | `RAGPipeline` | Master orchestrator. Exposes `query()`, `build_index()`, `load_index()`, `ensure_index()`, `compute_corpus_fingerprint()`, `is_index_stale()`, and `validate_input()` (rejects empty, $<3$ chars, $>500$ chars, and control characters). |
| [`record_store.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/record_store.py) | 130 | `RecordStore` | Persistent audit store in `data/workflow_records/records.json`. Implements atomic `.tmp` file replace, automated regex secret scrubbing, `FINAL_STATUSES` duplicate finalization guard (blocks re-decisions on `APPROVED`/`REJECTED` records), and non-empty reviewer validation. |
| [`workflow.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/workflow.py) | 370 | `DecisionWorkflow` | End-to-end proposal evaluation pipeline: (1) Validation, (2) Index check, (3) Retrieval, (4) Sufficiency, (5) Conflict check, (6) Recommendation synthesis, (7) **Mandatory Human Approval Gate** (`AWAITING_APPROVAL`). Evaluates against corporate $50,000 spend cap and 15% reserve buffer. |
| [`evaluation.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/evaluation.py) | 200 | `EvaluationRunner`, `run_evaluation()` | Benchmark harness executing questions in `evaluation/questions.jsonl`. Computes retrieval success rate, status accuracy, failure detection rate, citation validity rate, and latency. Dumps timestamped JSON reports to `evaluation/results/`. |
| [`cli.py`](file:///c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main/src/evidence_rag/cli.py) | 869 | `main()` Click command group | Implements all CLI commands. Contains `safe_text()` mapping table sanitizing Unicode arrows (`->`), dashes (`--`), and glyphs for Windows `cp1252` console compatibility. |

---

## 6. Data and Indices Inventory

### 6.1 Datasets and Manifests
- **Primary Knowledge Corpus (`data/documents/`):** Exactly 26 Markdown files (`doc_001_python_basics.md` through `doc_026_incomplete_proposal.md`).
  - Technical group: `DOC-001` to `DOC-020` (Python, SQL, Machine Learning, Systems, RAG specifications).
  - Business/Marketing group: `DOC-021` to `DOC-026` (Enterprise Growth Proposal, Budget Constraints Policy, Performance Metrics, Influencer Policies Standard & Restricted, Incomplete Expansion Proposal).
- **Corpus Manifest (`data/manifest.json`):** Tracks all 26 documents. Specifies `document_id`, `title`, `source`, `source_type`, `version`, `created_at`, `updated_at`, `topic`, and `category`. Aggregate SHA-256 fingerprint: `6f9ff58432410528`.
- **Marketing Sub-Corpus (`data/marketing_corpus/`):** 4 documents (`DOC-MKT-001_campaign_objectives.md`, `DOC-MKT-002_budget_guidelines.md`, `DOC-MKT-003_past_performance_benchmarks.md`, `DOC-MKT-004_compliance_and_channel_rules.md`) + `manifest.json`.

### 6.2 Vector Indices
- **Primary Vector Index (`data/index/`):**
  - `vectors.npy`: NumPy binary array of shape `(348, 512)` float32. Unit L2 normalized.
  - `knowledge_index.json`: Catalog of all 348 indexed passages with document references, character offsets, and token counts.
  - `embedding_model.pkl`: Serialized scikit-learn `TfidfVectorizer` state.
  - Alignment: Exactly 348 vectors mapping 1:1 to 348 chunk IDs (zero missing, zero orphans).
- **Marketing Vector Index (`data/marketing_index/`):**
  - Shape: `(22, 256)` float32. Contains 22 chunks across the 4 marketing documents.

### 6.3 Audit Records Ledger (`data/workflow_records/records.json`)
- Exactly 26 recorded proposal transactions (4,585 lines of formatted JSON).
- Contains historical proposal evaluations (`REQ-001`, `REQ-GROWTH-01`, `REQ-OVERSPEND-01`, `REQ-INCOMPLETE-01`, `REQ-CONFLICT-01`, etc.) with full evidence sets, recommendations, risk assessments, and reviewer approval histories.

### 6.4 Benchmark Dataset and Results
- **Benchmark Suite (`evaluation/questions.jsonl`):** Exactly 25 benchmark questions across 6 categories:
  - Answerable Factual: 10 questions (Q01-Q10)
  - Multi-Document Synthesis: 3 questions (Q11-Q13)
  - Ambiguous / Polysemous: 2 questions (Q14-Q15)
  - Insufficient Evidence: 3 questions (Q16, Q17, Q24)
  - Conflicting Evidence: 2 questions (Q18, Q19)
  - Adversarial / Boundary: 5 questions (Q20-Q22, Q23, Q25)
- **Evaluation Results (`evaluation/results/latest_evaluation_run.json`):**
  - Total Questions: 25
  - Retrieval Success Rate: **94.74%** (18/19 applicable)
  - Status Accuracy: **100.0%** (25/25)
  - Failure Detection Rate: **100.0%** (8/8 negative cases)
  - Citation Validity Rate: **100.0%** (45/45 citations verified)
  - Average Latency: **11.52 ms** (offline mock mode)

---

## 7. Test Inventory and Suite Verification

### 7.1 Complete Test Inventory (25 Test Files, 126 Cases)

```
tests/
├── boundary/                           (3 files,   7 tests)
│   ├── test_corrupt_index.py           (1 test)
│   ├── test_empty_knowledge_base.py    (1 test)
│   └── test_input_validation.py        (5 tests)
├── functional/                         (7 files,  48 tests)
│   ├── test_citation_validation.py     (3 tests)
│   ├── test_conflict_detection.py      (2 tests)
│   ├── test_day3_scenarios.py          (10 tests)
│   ├── test_pipeline_qa.py             (3 tests)
│   ├── test_task2_multi_domain.py      (12 tests)
│   ├── test_workflow.py                (8 tests)
│   └── test_workflow_cli_separation.py (10 tests)
├── integration/                        (4 files,  10 tests)
│   ├── test_context_builder.py         (2 tests)
│   ├── test_indexing.py                (2 tests)
│   ├── test_ingestion.py               (4 tests)
│   └── test_retrieval.py               (2 tests)
├── regression/                         (1 file,    1 test)
│   └── test_benchmark_regression.py    (1 test)
├── security/                           (2 files,   2 tests)
│   ├── test_prompt_injection.py        (1 test)
│   └── test_secret_leakage.py          (1 test)
├── task3/                              (3 files,  39 tests)
│   ├── test_task3_approval_integrity.py(12 tests)
│   ├── test_task3_replay.py            (7 tests)
│   └── test_task3_security.py          (20 tests)
└── unit/                               (5 files,  19 tests)
    ├── test_chunking.py                (4 tests)
    ├── test_cleaning.py                (6 tests)
    ├── test_confidence.py              (2 tests)
    ├── test_embeddings.py              (4 tests)
    └── test_schemas.py                 (3 tests)
TOTAL: 25 test files, 126 automated test cases
```

### 7.2 Resolution of Historical Test Claims
1. **The 116 Tests Claim:**  
   Documented in `README.md`, `HANDOVER.md`, and `TASK3_FINAL_REPORT.md` (commit `3703c51`). At that point, the test suite comprised 24 test files totaling 116 tests.
2. **The 24 Test Suites Reference:**  
   The assignment and prior audits referenced the 24 test files listed in Section 9 of `TASK3_FINAL_REPORT.md`.
3. **The 126 Tests Current Reality:**  
   In commit `2178225`, Rupam added `test_workflow_cli_separation.py` containing **10 test cases** to verify strict separation between `workflow ask` and `workflow evaluate`.
   - $116 + 10 = \mathbf{126\text{ tests}}$ across $\mathbf{25\text{ test files}}$.
   - This count is confirmed by `evidence_packet/clean_test_output.txt` ("126 passed in 2.35s"), `evidence_packet/test_execution_summary.json` ("collected_tests: 126, passed: 126"), `evidence_packet/test_inventory.csv` (126 rows), and `PROJECT_REVIEW_GUIDE.md` ("126/126 Tests Passing").
   - **Conclusion:** Documentation claims of 116 tests are outdated snapshots. The canonical test inventory is **126 test cases across 25 test files**.

---

## 8. Integration Seams and Ecosystem Reality Check

In accordance with the assignment stop conditions (*"Do not claim an integration is working simply because a package imports or an API configuration exists; mark BLOCKED / NOT VERIFIED with contract and runtime evidence"*):

| System | Role in CMO Agent | Integration Code | Status | Verification Detail |
|---|---|---|---|---|
| **MASTERDB Platform** | Shared enterprise data platform | None | **BLOCKED / NOT VERIFIED** | AegisCore writes to local `data/workflow_records/records.json`. Zero PostgreSQL / SQLAlchemy connection to the VM deployment. |
| **TANTRA** | Service discovery, auth & orchestration | None | **BLOCKED / NOT VERIFIED** | Zero service registration. Reviewer identity in `submit_approval` is unauthenticated plain text. Zero JWT middleware. |
| **VAJRA** | Trust, identity & provenance | None | **BLOCKED / NOT VERIFIED** | While internal SHA-256 document hashing exists, there is zero integration with VAJRA's cryptographic trust ledger. |
| **BIQOS** | Product positioning & dependencies | None | **BLOCKED / NOT VERIFIED** | Zero positioning contract or shared dependency mapping. |
| **Marketing Intelligence RAG** | CMO marketing intelligence retrieval | Candidate kernel | **READY FOR ADAPTATION** | AegisCore provides the foundational retrieval and policy evaluation algorithms, ready to be wrapped as a microservice. |

---

## 9. WP1 Deliverable Summary & Transition to WP2

### WP1 Deliverable Sign-Off
- **All folders and files inspected:** Outer workspace (`C:\Pratik_Bhuwad\CMO_Agent`) and inner application directory (`evidence-grounded-rag-main`).
- **Dependencies and build files verified:** `pyproject.toml`, `requirements.txt`, `configs/`.
- **Architecture and entry points mapped:** Click CLI, programmatic Python APIs, absence of HTTP REST layer.
- **Ingestion, chunking, embedding, retrieval, conflict, and workflow engines audited:** Complete line-by-line inspection.
- **Test inventory reconciled:** 126 test cases across 25 test files accounted for. Outdated 116-test claims resolved.

### Readiness for WP2 (Reproduce the Environment)
WP1 is complete. The next package is **WP2 — Reproduce the environment**:
1. Isolate a clean Python virtual environment (`.venv`).
2. Pin `numpy>=1.24.0,<2.0.0` to resolve the SciPy C-API ABI blocker.
3. Install declared dependencies from `requirements.txt`.
4. Run `pytest tests -v` and record clean test run evidence into `rupam_environment_test_report.md`.
5. Run baseline CLI commands (`verify`, `evaluate`, `workflow replay`).

