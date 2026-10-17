# AegisCore Knowledge Base Corpus

This directory contains the knowledge base documents and machine-readable metadata manifest for the Evidence-Grounded RAG System.

## Corpus Summary
- **Total Documents:** Exactly 20 synthetic technical documents
- **Format:** Markdown (`.md`) with UTF-8 encoding
- **Manifest:** `data/manifest.json`
- **Domain:** Fictional AegisCore Distributed Intelligence Platform

## Required Metadata Fields
Every document in `data/manifest.json` contains:
1. `document_id`: Unique stable identifier (`DOC-001` through `DOC-020`)
2. `title`: Human-readable document title
3. `source`: Relative filesystem path to the document file
4. `source_type`: Category of documentation (e.g. `technical_specification`, `architecture_design`, `security_standard`, `operational_guideline`, `engineering_guide`, `qa_standards`)
5. `version`: Semantic version string (e.g. `1.0.0`)
6. `created_at`: ISO 8601 creation timestamp
7. `updated_at`: ISO 8601 last modified timestamp
8. `topic`: High-level subject domain

## Document Inventory
| Document ID | Topic | Title | Source Type |
|---|---|---|---|
| `DOC-001` | System Overview | AegisCore System Overview and Operational Mission | technical_specification |
| `DOC-002` | Architecture | AegisCore Modular Architecture and Component Topology | architecture_design |
| `DOC-003` | Data Ingestion | Data Ingestion Protocols and Manifest Validation | engineering_guide |
| `DOC-004` | Document Processing | Document Parsing and Structural Extraction | technical_specification |
| `DOC-005` | Text Cleaning | Text Cleaning, Sanitization, and PII Redaction | security_standard |
| `DOC-006` | Chunking | Chunking Strategies and Chunk Identity Specification | engineering_guide |
| `DOC-007` | Embeddings | Embedding Generation and Vector Representations | technical_specification |
| `DOC-008` | Vector Indexing | Vector Indexing, Storage Layout, and Index Persistence | technical_specification |
| `DOC-009` | Retrieval Configuration | Retrieval Configuration, Filter Policies, and Candidate Limits | operational_guideline |
| `DOC-010` | Similarity Scoring | Similarity Scoring Metrics and Candidate Ranking Heuristics | mathematical_specification |
| `DOC-011` | Context Construction | Context Construction and Passage Formatting Guidelines | engineering_guide |
| `DOC-012` | Answer Generation | Grounded Answer Generation Protocols and Prompt Templates | system_prompt_specification |
| `DOC-013` | Citation Rules | Citation Syntax, Claim Attribution, and Citation Validation | compliance_specification |
| `DOC-014` | Confidence & Uncertainty | Confidence Scoring and Uncertainty Handling Framework | algorithmic_specification |
| `DOC-015` | Error Handling | Error Handling Protocols, Fault Resilience, and Fallbacks | reliability_guide |
| `DOC-016` | Security Controls | Security Controls, Prompt Injection Defense, and Secret Protection | security_standard |
| `DOC-017` | Input Validation | Input Validation, Query Sanitization, and Boundary Enforcement | technical_specification |
| `DOC-018` | Logging & Observability | Logging, Telemetry, and Observability Framework | operational_guideline |
| `DOC-019` | Testing & Evaluation | Testing Pyramid, Quality Assurance, and Evaluation Standards | qa_standards |
| `DOC-020` | Deployment & Limitations | Deployment Profiles, Operational Limitations, and Resource Sizing | operational_guideline |

## Intentionally Conflicting Pair
- **Document 1:** `DOC-009` (Retrieval Configuration) states that production retrieval operates with a **default top-k of 5** and **candidate pool size of 20**.
- **Document 2:** `DOC-020` (Deployment Profiles) states that under revised guidelines, production retrieval operates with a **default top-k of 10** and **candidate pool size of 50**.
- **Conflict Behavior:** When queried on default production top-k or candidate pool size, the RAG system retrieves both documents, flags status `CONFLICT_DETECTED`, and presents both documented viewpoints without arbitrary bias.
