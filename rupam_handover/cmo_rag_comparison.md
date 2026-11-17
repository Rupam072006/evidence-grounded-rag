# Rupam Patne Handover — WP4 Three-Way RAG Systems Comparison Summary

**Canonical Reference:** See the full detailed report at [04_cmo_rag_comparison.md](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/04_cmo_rag_comparison.md)  
**Governing Authority / CMO Product Owner:** Prateek  
**Author:** Rupam Patne (CMO Agent Engineering Lead)  
**Status:** WP4 Complete — Three-Way Architectural Comparison & Reuse Strategy Defined  
**Date:** November 14, 2026  

---

## 1. Summary of Compared Systems

1. **System 1: Evidence-Grounded RAG (Rupam's Implemented Codebase):**  
   Standalone Python library & Click CLI (`evidence-rag`). 21 modules, 26 docs, 348 passages, 132 automated tests (100% pass rate). 512-dim TF-IDF embeddings, strict citation enforcement, contradiction detection, and deterministic approval gate state machine.
2. **System 2: AegisCore Reference Architecture (Task 1 Blueprint):**  
   Zero-trust evidence-first specification (`DOC-001`–`DOC-020`). 99.95% SLA, 400-char chunks, 60-char sliding overlap, L2 unit-norm vectors, and canonical refusal on insufficient evidence.
3. **System 3: Current CMO Kernel (Target Enterprise Ecosystem):**  
   Enterprise multi-agent cluster: **MASTERDB** (PostgreSQL on dedicated VM), **TANTRA** (JWT authentication), **VAJRA** (cryptographic identity), and **BIQOS** (business campaign execution). Requires a REST API wrapper.

---

## 2. Core Comparison Insights

| Capability Area | System 1 (Implemented) | System 2 (AegisCore Spec) | System 3 (CMO Enterprise Target) | Recommended Canonical Path |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion & Cleaning** | 4-stage pipeline with PII/key redaction | Strict 4-stage untrusted data sanitization | Upstream service ingestion | **REUSE System 1 directly** |
| **Chunking Engine** | Boundary-aware (400 chars, 60 overlap) | Paragraph & sentence-aware chunking | Variable/coarse record chunking | **REUSE System 1 directly** |
| **Citation Tracking** | Candidate pool validation `[DOC:CHUNK]` | Mandatory claim-level citation syntax | Free-form LLM citations | **REUSE System 1 directly** |
| **Contradiction Engine**| Pairwise conflict detection (DOC-009/020, DOC-024/025) | Dual-perspective reporting rule | Absent (unmanaged conflict) | **REUSE System 1 directly** |
| **Storage & Persistence**| Local flat files (`records.json`, `vectors.npy`) | Local flat-file layout | MASTERDB (PostgreSQL VM) | **ADAPT: Connect to MASTERDB** |
| **API Exposure** | Click CLI / Python import only | In-process specification | FastAPI REST microservice | **ADAPT: Wrap with FastAPI** |
| **Managerial Approval** | State machine halting at `AWAITING_APPROVAL` | Human-in-the-loop governance | Authenticated sign-off via TANTRA/VAJRA | **ADAPT: Validate JWT Bearer** |

---

## 3. Recommended Architectural Strategy

- **DO NOT REBUILD:** The algorithms for text cleaning, passage chunking, vector indexing, citation validation, conflict detection, and human approval state transitions are already written, tested across 26 test suites, and verified against 25 benchmark scenarios.
- **ADAPT VIA MICROSERVICE:** Wrap `RAGPipeline` and `DecisionWorkflow` with a lightweight FastAPI microservice exposing `/api/v1/query`, `/api/v1/proposals/evaluate`, and `/api/v1/proposals/{id}/approve`.
- **PRESERVE MASTERDB AS SOURCE OF TRUTH:** Replace local flat-file `records.json` with an adapter writing proposal records to MASTERDB, satisfying the assignment mandate forbidding parallel vector stores.

WP4 is complete and ready for handoff to **WP5 (Integration Assessment)**.

