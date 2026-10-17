# AegisCore System Entry Points

This document provides an inventory of all operational and programmatic entry points into the system.

## 1. Command-Line Interface (`evidence_rag.cli`)
The CLI is installed globally in the Python environment as `evidence-rag` or invocable via `python -m evidence_rag.cli`.

| Command | Syntax | Purpose |
|---|---|---|
| **Index** | `evidence-rag index [--config PATH]` | Ingests documents, creates chunk embeddings, and serializes index to disk. |
| **Query** | `evidence-rag query "<QUESTION>" [--json-out]` | Queries the RAG pipeline; formats output in terminal panels or JSON. |
| **Verify** | `evidence-rag verify` | Runs automated integrity checks on manifest, documents, and index. |
| **Evaluate** | `evidence-rag evaluate [--questions PATH]` | Executes benchmark battery and prints evaluation metrics table. |

## 2. Programmatic Python API
- **High-level Orchestrator:** `from evidence_rag.pipeline import RAGPipeline`
  - `pipeline.build_index()`: Rebuilds persistent index.
  - `pipeline.ensure_index()`: Loads or builds index.
  - `pipeline.query(user_query: str) -> RAGResponse`: Executes end-to-end question answering.
- **Config Loader:** `from evidence_rag.config import load_config`
- **Schemas:** `from evidence_rag.schemas import RAGResponse, ResponseStatus, Citation`
- **Evaluator:** `from evidence_rag.evaluation import EvaluationRunner`

## 3. Test Runner
- **Command:** `python -m pytest tests -v`
- **Coverage:** Runs 46 automated tests across unit, integration, functional, boundary, security, and regression tiers.
