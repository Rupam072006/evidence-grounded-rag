# Known Issues, Weak Spots & Technical Blockers

**Project:** BHIV CMO Technical Execution Assignment v2 — Known Issues Audit  
**Date:** 2026-11-11  

---

## 1. Executive Identification of Issues

This document records all confirmed technical blockers, architectural constraints, potential code defects, and runtime limitations identified during the initial audit. In accordance with strict auditing standards, no issue is categorized as resolved or nonexistent until empirical verification is established.

---

## 2. Technical Blockers & Remediation Status

### Blocker 1: Environment Import Failure (`sklearn` Missing in Python 3.11) — **RESOLVED (Task 2)**
- **Classification:** Runtime Dependency Blocker (Severity: **CRITICAL**)
- **Remediation Status:** **RESOLVED** via isolated virtual environment (`.venv`) and pinned `requirements.lock` (`scikit-learn==1.9.1`).
- **Verification:** Verified via `test_environment_reproducibility.py` (`4/4 passed`) and all 130 tests passing in 2.43s.
- **Reference:** [`defect_report.md`](file:///C:/Users/A/Desktop/Bhiv_Rhugved/CMO%20Agent/evidence-grounded-rag/docs/defect_report.md) (`DEFECT-ENV-001`).

### Blocker 2: CLI Console Renderer Missing (`rich` Missing in All Runtimes) — **RESOLVED (Task 2)**
- **Classification:** Runtime Dependency Blocker (Severity: **HIGH**)
- **Remediation Status:** **RESOLVED** via `.venv` installation (`rich==15.0.0`).
- **Verification:** CLI commands (`evidence-rag verify`, `evidence-rag workflow evaluate`) execute cleanly with Rich panel and table rendering.
- **Reference:** [`defect_report.md`](file:///C:/Users/A/Desktop/Bhiv_Rhugved/CMO%20Agent/evidence-grounded-rag/docs/defect_report.md) (`DEFECT-ENV-001`).

### Blocker 3: Dual Workspace Root Topography Ambiguity — **RESOLVED (Task 2)**
- **Classification:** Configuration / Structure Ambiguity (Severity: **MEDIUM**)
- **Remediation Status:** **RESOLVED** via standardized execution guidelines. All commands run with working directory set to `evidence-grounded-rag` (`Set-Location evidence-grounded-rag`).
- **Verification:** 100% of relative path operations (`configs/`, `data/`) resolve deterministically without path errors.
- **Reference:** [`defect_report.md`](file:///C:/Users/A/Desktop/Bhiv_Rhugved/CMO%20Agent/evidence-grounded-rag/docs/defect_report.md) (`DEFECT-ENV-004`).

---

## 3. Architectural Limitations & Known Weak Spots

### Weak Spot 1: Unauthenticated Manager Approval Gate
- **Classification:** Security & Governance Vulnerability (Severity: **HIGH**)
- **Location:** `src/evidence_rag/workflow.py:submit_approval()` and `src/evidence_rag/cli.py:workflow_approve()`
- **Detail:** In `workflow.py`, `submit_approval` takes `reviewer: str` as an unvalidated parameter. Any terminal operator can pass `--reviewer "cmo_executive"` and approve a proposal with zero authentication, cryptographic signature, or role-based access control (RBAC) verification.
- **Auditor Note:** While the system successfully halts automated execution and preserves an audit trail, the identity of the human approver is self-attested text rather than authenticated authorization.

### Weak Spot 2: Rule-Based / Pairwise Conflict Detection
- **Classification:** Scalability & Generalization Constraint (Severity: **MEDIUM**)
- **Location:** `src/evidence_rag/conflict_detection.py:ConflictDetector`
- **Detail:** Contradiction interception relies primarily on pre-registered document pairings (`DEFAULT_KNOWN_CONFLICT_PAIRS` such as `DOC-MKT-002` vs `DOC-MKT-004`) combined with regex number/topic matching.
- **Impact:** Unregistered or newly introduced policy contradictions outside the known paired catalog will not be intercepted reliably.

### Weak Spot 3: Heuristic Keyword Additive Reranking
- **Classification:** Retrieval Quality Limitation (Severity: **LOW - MEDIUM**)
- **Location:** `src/evidence_rag/retrieval.py:Retriever._calculate_keyword_boost`
- **Detail:** The system combines sparse-dense TF-IDF cosine similarity with an additive boost (`+0.05` for matching keywords). It does not implement a dedicated neural cross-encoder (e.g., BGE Reranker or Cohere Rerank) or Reciprocal Rank Fusion (RRF).

### Weak Spot 4: Single-File JSON Audit Ledger Concurrency
- **Classification:** Concurrency & Persistence Bottleneck (Severity: **MEDIUM**)
- **Location:** `src/evidence_rag/record_store.py:RecordStore`
- **Detail:** All proposal records are serialized into a single flat file (`data/workflow_records/records.json`). Although write operations use atomic file swapping (`temp_file.replace(store_file)`), concurrent multi-process writes could result in race conditions and lost updates without file locking (`fcntl` / `filelock`).

### Weak Spot 5: Absence of HTTP / REST Service Layer
- **Classification:** Integration Blocker (Severity: **HIGH for Web Portal Integration**)
- **Location:** Project-wide
- **Detail:** The system is exclusively operable via CLI or Python import. It cannot be consumed by web dashboards, frontend portals, or third-party webhooks without adding an ASGI server layer (e.g. FastAPI).

---

## 4. Code Defects & Edge Cases Recorded

1. **Character Budget Truncation in Long Chunks:** In `chunking.py`, when splitting very long paragraphs using sentence boundaries, if a single sentence exceeds `target_size`, it is emitted without further sub-chunking, causing occasional chunk size variance.
2. **Case Sensitivity in Preset Identifiers:** In `cli.py`, preset aliases (`REQ-GROWTH-01`, `REQ-OVERSPEND-01`) require specific case normalization to prevent key misses during replay commands.
3. **Encoding Hazards on Windows Consoles:** Legacy Windows PowerShell consoles using CP1252 or OEM code pages may encounter Unicode display glitches with special quote marks or arrows. `cli.py:safe_text()` attempts sanitization, but running in standard UTF-8 (`chcp 65001`) is advised.
