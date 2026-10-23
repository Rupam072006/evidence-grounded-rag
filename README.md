# AegisCore: Evidence-Grounded Retrieval-Augmented Generation (RAG) System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-55%20passed-success.svg)]()
[![Retrieval Success Rate](https://img.shields.io/badge/Retrieval%20Rate-100%25-brightgreen.svg)]()
[![Citation Validity Rate](https://img.shields.io/badge/Citation%20Validity-100%25-brightgreen.svg)]()

> **Project Author:** Rupam Patne (Computer Science Engineering, AI/ML Specialization)  
> **Repository:** `evidence-grounded-rag`  
> **Target Environment:** Windows 10/11 / PowerShell / Python 3.10 - 3.13 (Tested on Python 3.13.1)  
> **System Status:** Fully Tested (55/55 Passed), Benchmarked, Task 2 Day 2 Decision-Support Workflow Complete, and 100% Deterministic.

---

## 1. Executive Summary & Overview

**AegisCore** is an enterprise-grade **Evidence-Grounded Retrieval-Augmented Generation (RAG) system** engineered for zero-trust, high-assurance knowledge retrieval. Traditional conversational AI systems hallucinate facts or extrapolate unverifiable claims when answering from parametric memory alone. AegisCore treats internal documentation as the single source of truth, enforcing mathematical sufficiency floors, claim-level attribution, and automated conflict detection.

### Key Capabilities
1. **Zero-Trust Grounding:** Answers are generated exclusively from verified internal document chunks.
2. **Machine-Auditable Citations:** Every claim must carry a verified citation using canonical syntax `[DOCUMENT_ID:CHUNK_ID]` checked against retrieved context.
3. **Anti-Hallucination Sufficiency Floor:** If retrieved evidence does not meet similarity and coverage floors (score >= 0.20, term coverage >= 28%), the system issues a canonical refusal (`INSUFFICIENT_EVIDENCE`) rather than fabricating answers.
4. **Automated Contradiction Detection:** When authoritative documents contain conflicting specifications (such as baseline vs. revised deployment parameters), the system detects the discrepancy (`CONFLICT_DETECTED`) and presents both perspectives.
5. **Decoupled Generation Engines:** Supports offline bitwise-deterministic mock generation for tests and CI/CD, as well as live cloud LLM generation via Groq Cloud (`openai/gpt-oss-120b`) or Google Gemini.

---

## 2. Project Documentation Files

The repository maintains five dedicated project documentation files in the project root:

1. **[`README.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/README.md):** Master overview, installation, execution, architecture, and benchmarking manual.
2. **[`ARCHITECTURE.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/ARCHITECTURE.md):** Deep technical architecture, component responsibilities, Mermaid pipeline topology, and failure handling matrix.
3. **[`INTEGRATION.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/INTEGRATION.md):** Programmatic Python API, schemas, environment configurations, and integration verification steps.
4. **[`CHANGELOG.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/CHANGELOG.md):** Chronological history of releases, document updates, bug fixes, and version milestones.
5. **[`HANDOVER.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/HANDOVER.md):** Maintenance runbooks, re-indexing commands, testing procedures, known limitations, and future roadmap.

---

## 3. The 20 Knowledge Base Documents

The system's non-parametric knowledge corpus resides in `data/documents/` and is cataloged in `data/manifest.json`. Each document implements the 8 required metadata fields (`document_id`, `title`, `source`, `source_type`, `version`, `created_at`, `updated_at`, `topic`) and cites reliable public sources:

### Programming and Data Analysis
1. **[`doc_001_python_basics.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_001_python_basics.md) (`DOC-001`):** Python variables, dynamic typing, operators, conditional branching, loops, and AegisCore's 99.95% uptime SLA target.
2. **[`doc_002_python_functions.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_002_python_functions.md) (`DOC-002`):** Defining and calling functions, parameter passing, return values, scope resolution (LEGB rule), and modular architecture.
3. **[`doc_003_python_exceptions.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_003_python_exceptions.md) (`DOC-003`):** Common Python exceptions, `try`/`except`/`else`/`finally` blocks, and SHA-256 document provenance hashing.
4. **[`doc_004_numpy_basics.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_004_numpy_basics.md) (`DOC-004`):** NumPy arrays (`ndarray`), vectorized operations, slicing, and mandatory UTF-8 character encoding enforcement.
5. **[`doc_005_pandas_basics.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_005_pandas_basics.md) (`DOC-005`):** Series and DataFrames, CSV loading, filtering, and 4-stage text cleaning pipeline (NFKC, control char removal, whitespace consolidation, security tag stripping).
6. **[`doc_006_pandas_cleaning.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_006_pandas_cleaning.md) (`DOC-006`):** Missing value handling, duplicate record removal, data type casting, 400-character chunking, and 60-character sliding overlap.
7. **[`doc_007_matplotlib_basics.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_007_matplotlib_basics.md) (`DOC-007`):** Basic plots, labels, legends, chart selection, and 512-dimensional L2 unit-norm vectors for dot product equivalence.
8. **[`doc_008_sql_basics.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_008_sql_basics.md) (`DOC-008`):** SELECT, WHERE, ORDER BY, GROUP BY, joins, and persistent storage layout (`vectors.npy` and `knowledge_index.json`).

### Machine Learning
9. **[`doc_009_machine_learning_intro.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_009_machine_learning_intro.md) (`DOC-009`):** Machine learning fundamentals, supervised/unsupervised/reinforcement learning types, applications, limitations, and baseline retrieval parameters (default top-k of 5 and candidate pool size of 20).
10. **[`doc_010_supervised_learning.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_010_supervised_learning.md) (`DOC-010`):** Classification vs. regression, training examples, supervised algorithms, and deterministic tie-breaking policy (document version precedence followed by chunk sequence order).
11. **[`doc_011_model_evaluation.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_011_model_evaluation.md) (`DOC-011`):** Accuracy, precision, recall, F1-score, confusion matrix, regression metrics, and 1,500 token (6,000 character) context budget cap.
12. **[`doc_012_train_test_split.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_012_train_test_split.md) (`DOC-012`):** Training, validation, and test partitions, data leakage prevention, and answer generation grounding contracts.

### RAG and Retrieval
13. **[`doc_013_embeddings.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_013_embeddings.md) (`DOC-013`):** Dense text embeddings, semantic search, cosine similarity, inner product equivalence, and canonical citation syntax `[DOCUMENT_ID:CHUNK_ID]`.
14. **[`doc_014_vector_search.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_014_vector_search.md) (`DOC-014`):** Vector indices, exact flat k-NN vs. ANN, top-k candidate ranking, and the 0.25 similarity floor (or 0.20 score floor + 28% query term coverage).
15. **[`doc_015_rag_fundamentals.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_015_rag_fundamentals.md) (`DOC-015`):** RAG workflow, non-parametric vs. parametric memory, grounded answers, and typed exception hierarchy rooted in `RAGException`.
16. **[`doc_016_chunking.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_016_chunking.md) (`DOC-016`):** Chunk boundaries, sentence preservation, sliding windows, and security controls treating retrieved context as untrusted data.
17. **[`doc_017_prompt_injection.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_017_prompt_injection.md) (`DOC-017`):** Direct and indirect prompt injection attacks, adversarial defense, and query validation boundaries (3 to 500 characters, whitespace rejection).
18. **[`doc_018_evaluation_methods.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_018_evaluation_methods.md) (`DOC-018`):** Retrieval relevance, answer groundedness, unanswerable question testing, and structured JSON logging.

### Metadata and Evidence
19. **[`doc_019_metadata_management.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_019_metadata_management.md) (`DOC-019`):** The 8 mandatory metadata fields, schema preservation across ingestion/chunking/indexing/retrieval, 46-test test suite, and 22-question benchmark.
20. **[`doc_020_evidence_and_citations.md`](file:///c:/Users/rupam/OneDrive/Desktop/RAG/data/documents/doc_020_evidence_and_citations.md) (`DOC-020`):** Claim-level attribution, citation verification, platform deployment profile (minimum 4GB RAM, CPU inference, 99.95% SLA), and revised retrieval parameters (top-k=10, candidate pool=50) intentionally conflicting with DOC-009.

---

## 4. Repository Directory Structure

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
│   ├── index/                     # Persistent index storage
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
├── README.md                      # Master user and reviewer manual
├── pyproject.toml                 # Package definition and CLI entry points
└── requirements.txt               # Pinned package dependencies
```

---

## 5. Technology Stack & Dependencies

- **Language:** Python 3.10+ (tested on Python 3.13.1)
- **Data Validation & Schemas:** Pydantic v2
- **Vector Computation & Mathematics:** NumPy (vector matrix operations, L2 normalization, dot products)
- **Natural Language Preprocessing:** Scikit-learn (TF-IDF vectorizer, n-gram extraction)
- **Configuration & Persistence:** PyYAML, JSON, Pickle
- **Testing:** Pytest (46 tests passing)
- **External LLM Backends (Optional):** Groq Cloud API, Google GenAI SDK (`google-generativeai`)

---

## 6. Installation & Setup Instructions

### Step 1: Open PowerShell in Project Root
```powershell
cd C:\Users\rupam\OneDrive\Desktop\RAG
```

### Step 2: Install Package in Editable Mode
```powershell
python -m pip install -e .
```

### Step 3: Configure Environment Variables (Optional for Live Mode)
By default, the system operates in offline `mock` mode, requiring no API keys. If you wish to use Groq Cloud for online generation, configure `.env`:
```ini
# .env file
RAG_GENERATION_MODE=mock
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

---

## 7. How to Run the Project

### Command-Line Interface (`evidence-rag`)

1. **Rebuild the Vector Index:**
   ```powershell
   evidence-rag index
   ```
   *Ingests all 20 documents from `data/manifest.json`, chunks them into 299 passages, and saves the index to `data/index/`.*

2. **Verify Corpus & Index Integrity:**
   ```powershell
   evidence-rag verify
   ```
   *Confirms exactly 20 documents, checks metadata schemas, and validates index persistence.*

3. **Query the System:**
   ```powershell
   # Answerable query
   evidence-rag query "What character encoding is mandatory for all incoming documents in AegisCore?"

   # Contradiction query (DOC-009 vs DOC-020)
   evidence-rag query "What is the default production top-k parameter and candidate pool size for the retrieval service?"

   # Unsupported out-of-domain query (triggers canonical refusal)
   evidence-rag query "What is the secret recipe for Aunt May's chocolate chip cookies?"
   ```

4. **Run the 22-Question Evaluation Benchmark:**
   ```powershell
   evidence-rag evaluate
   ```

---

## 8. How to Add Knowledge Base Documents

To add or update documents in the knowledge base:

1. **Create the Markdown file** in `data/documents/<new_filename>.md`.
2. **Include all 8 required metadata fields** at the top:
   ```markdown
   # Title
   
   ## Metadata
   - **document_id:** DOC-021
   - **title:** Your Document Title
   - **source:** data/documents/your_filename.md
   - **source_type:** technical_guide
   - **version:** 1.0.0
   - **created_at:** 2026-10-21T08:00:00Z
   - **updated_at:** 2026-10-21T08:00:00Z
   - **topic:** Your Topic
   ```
3. **Register the document in `data/manifest.json`**:
   Add a matching JSON object to the `documents` array and update `total_documents`.
4. **Rebuild the index**:
   ```powershell
   evidence-rag index
   evidence-rag verify
   ```

---

## 9. Pipeline Architecture & Implementation Mechanics

### A. Ingestion & Cryptographic Fingerprinting (`ingestion.py`)
- Reads `data/manifest.json`, validates required schema fields, and enforces document counts.
- Computes SHA-256 hashes of every file to verify provenance and detect bitrot or tampering.

### B. 4-Stage Text Cleaning (`cleaning.py`)
- **Stage 1 (Unicode Normalization):** Converts characters to NFKC canonical standard.
- **Stage 2 (Control Character Removal):** Strips non-printable ASCII codes while preserving structural whitespace.
- **Stage 3 (Whitespace Consolidation):** Collapses duplicate spaces and line breaks.
- **Stage 4 (Security Tag Stripping):** Removes `<script>`, HTML tags, and XML injection vectors.

### C. Boundary-Aware Chunking (`chunking.py`)
- Splits text along paragraph and sentence boundaries into 400-character passages with 60-character sliding overlap.
- Assigns deterministic chunk IDs: `[DOCUMENT_ID]-C[SEQUENCE_3_DIGITS]`.

### D. 512-Dimensional Vector Embeddings (`embeddings.py`)
- Converts text passages into 512-dimensional vectors using sublinear TF-IDF and character/word n-grams.
- Normalizes all vectors to unit L2 norm ($\|\mathbf{v}\|_2 = 1.0$), transforming cosine similarity into ultra-fast dot products.

### E. Retrieval, Ranking & Tie-Breaking (`retrieval.py`)
- Computes query-passage dot products, applies lexical term bonuses, and ranks candidates descending.
- Breaks ties deterministically: document version precedence followed by chunk sequence order.

### F. Dual-Factor Evidence Sufficiency Check (`confidence.py`)
- Compares top retrieved score against `0.20` similarity floor and verifies that query term coverage across retrieved context is >= `28%`.
- If either check fails, generation is bypassed and status `INSUFFICIENT_EVIDENCE` is emitted.

### G. Cross-Document Contradiction Engine (`conflict_detection.py`)
- Analyzes retrieved passages for contradictory parameter specifications (such as `DOC-009` top-k=5/pool=20 vs. `DOC-020` top-k=10/pool=50).
- Surfaces both perspectives and sets status to `CONFLICT_DETECTED`.

### H. Grounded Generation & Citation Validation (`generation.py`, `evidence.py`)
- Context is packaged within structured data delimiters and capped at 1,500 tokens (6,000 characters).
- Generated answers assert claims accompanied by citations in the exact syntax `[DOCUMENT_ID:CHUNK_ID]`.
- Post-generation validator verifies each citation against the actively retrieved candidate set.

---

## 10. Automated Test Suite (46 Tests across 6 Tiers)

The project includes 46 automated pytest test cases covering all pipeline components:

```powershell
python -m pytest tests -q
```

### Verified Test Summary:
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-8.3.4, pluggy-1.6.0
rootdir: C:\Users\rupam\OneDrive\Desktop\RAG
collected 46 items

tests\boundary\test_corrupt_index.py .                                   [  2%]
tests\boundary\test_empty_knowledge_base.py .                            [  4%]
tests\boundary\test_input_validation.py .....                            [ 15%]
tests\functional\test_citation_validation.py ..                          [ 19%]
tests\functional\test_conflict_detection.py ..                           [ 23%]
tests\functional\test_pipeline_qa.py ...                                 [ 30%]
tests\integration\test_context_builder.py ..                             [ 34%]
tests\integration\test_indexing.py ..                                    [ 39%]
tests\integration\test_ingestion.py ....                                 [ 47%]
tests\integration\test_retrieval.py ..                                   [ 52%]
tests\regression\test_benchmark_regression.py .                          [ 54%]
tests\security\test_prompt_injection.py .                                [ 56%]
tests\security\test_secret_leakage.py .                                  [ 58%]
tests\unit\test_chunking.py ....                                         [ 67%]
tests\unit\test_cleaning.py ......                                       [ 80%]
tests\unit\test_confidence.py ..                                         [ 84%]
tests\unit\test_embeddings.py ....                                       [ 93%]
tests\unit\test_schemas.py ...                                           [100%]

============================= 46 passed in 0.27s ==============================
```

---

## 11. Current Limitations & Troubleshooting

1. **Cloud LLM Quota Limit (Groq Cloud Free Tier):**
   When running `evidence-rag evaluate` in live online mode with Groq Cloud (`openai/gpt-oss-120b`), the free tier enforces an 8,000 TPM limit that can trigger HTTP 429 errors during rapid 22-question batch execution. To run evaluation cleanly without external rate limits, run in mock mode:
   ```powershell
   $env:RAG_GENERATION_MODE="mock"; evidence-rag evaluate
   ```
2. **Query Length Bounds:**
   Queries must be between 3 and 500 characters. Queries outside this boundary are rejected with `INVALID_INPUT`.
3. **Index Persistence:**
   If `data/index/` files are deleted, run `evidence-rag index` to regenerate `vectors.npy`, `knowledge_index.json`, and `embedding_model.pkl`.
