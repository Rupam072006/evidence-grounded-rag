# Defects, Risks, Gaps & Blockers Register

| Field | Value |
|---|---|
| **Author** | Pratik Bhuwad (CMO Product Owner / Sprint Lead) |
| **Timestamp** | `2026-11-18T13:25:00+05:30` (Updated `2026-11-19T16:30:00+05:30` with Tester QA Findings) |
| **Canonical Repo / Commit** | `evidence-grounded-rag-main` (`main` @ `b91789d`) & `masterdb-ingestion-certification-service` (`main` @ `284ef75`) |
| **Verification Status** | `CONDITIONAL PASS (63/100) — VERIFIED NON-PRODUCTION` (Independently Audited by **Samsoorya Rajakumar, Tester**) |

---

## 1. Historical, Active & Tester-Identified Defects

| Defect ID | Title & Description | Severity | Repo / Component | Status | Evidence / Resolution Notes |
|---|---|---|---|---|---|
| **DEF-001 to DEF-006** | Historical Task 2 Day 1 defects (`httpx` packaging, corpus fingerprint hashing, `INDEX_UNAVAILABLE` status, unicode lenticular citation regex, HTTP 429 retry, dynamic conflict pair registry) | High–Low | `evidence-grounded-rag-main` | **CLOSED (Local Verified)** | Documented in `evidence-grounded-rag-main/evidence_packet/defect_register.md`; covered by passing `136/136` suite. |
| **DEFECT-SEMANTIC-001** | Hallucinated Linear TV metrics instead of semantic abstention | High | `src/evidence_rag/workflow.py` / `confidence.py` | **CLOSED (Local Verified & Retested by Tester)** | Retested by Tester in `p4_linear_tv_test.txt`: returns `INSUFFICIENT_EVIDENCE` & `null` metrics. Related gate gap `QA-002` logged below. |
| **DEF-MASTERDB-001** | Unhandled `NameError: name 'Path' is not defined` in CMO HTTP retrieval branch | High | `masterdb-ingestion-certification-service/services/capability_registry_service.py:1639` | **CLOSED (Audited by Kavy)** | Fixed (`from pathlib import Path`) + regression test `test_cmo_capability_http_retrieval_endpoint_regression` added (`Kavy/masterdb_test_report.md`, `100/100` passing). |
| **DEF-REPRO-001** | Relative path CWD dependency in test suite (`IndexNotFoundError` when `pytest` runs from parent folder) | Medium | `evidence-grounded-rag-main/src/evidence_rag/pipeline.py` & `config.py` | **CONFIRMED / OPEN (P1 for Rhugved)** | Confirmed by Tester (9 failed, 27 errors when run outside repo root). Solution documented in `PATH_B_DEVELOPER_HANDOFF.md` for Post-EOD Task 1. |
| **DEF-DOC-001** | Trace ID mismatch between Nov 17 prose docs (`TRC-20261116-6C7BDA95`) and persisted JSON/log artifacts (`TRC-20261116-1833C82E`) | Low | Historical prose docs | **CONFIRMED / OPEN** | Confirmed by Tester. Reconciled in `04_TEST_AND_RUNTIME_EVIDENCE/TEST_RECONCILIATION_AND_REPRODUCTION.md`. |
| **DEF-DOC-002** | Divergent `evidence_packet/` directories + missing `rhugved_runtime_validation_report.md` | Medium | Workspace & `evidence_packet/` | **UNVERIFIABLE IN TESTER WORKSPACE** | Logged for PMC (Nupur) archival cleanup upon return from leave. |
| **DEF-GOV-001** | Ownership-document naming conflict (`Pratik Bhuwad` vs `Prateek` vs `Pratik Bhuvad`) | Medium | Cross-repo governance documents | **RESOLVED VIA MEMO (ED-1)** | Formally resolved in `GOVERNANCE_NAME_CORRECTION_MEMO.md` (`MEMO-GOV-20261119-ED1`) confirming `Pratik Bhuwad` as canonical without overwriting history. |
| **QA-001** *(Tester Finding)* | Reviewer placeholder gate is exact-match only (`workflow.py:443`, `cli.py:571,630`). Case variants (`prof_evaluator`, `PROF_EVALUATOR`, `Anonymous`, `.`) were accepted and recorded | High | `src/evidence_rag/workflow.py`, `cli.py` | **OPEN (P1 for Rhugved)** | Assigned to Rhugved in `PATH_B_DEVELOPER_HANDOFF.md`: normalize NFKC, strip zero-width, casefold, and share validator between CLI and workflow. |
| **QA-002** *(Tester Finding)* | `record_store.record_decision` accepts decision on non-approvable statuses (only logs warning on `INSUFFICIENT_EVIDENCE -> APPROVED`) | High | `src/evidence_rag/record_store.py` | **OPEN (P1 for Rhugved)** | Assigned to Rhugved in `PATH_B_DEVELOPER_HANDOFF.md`: raise error unless status $\in$ `{AWAITING_APPROVAL, RECOMMENDATION_READY}`. |
| **QA-003** *(Tester Finding)* | `HUMAN_APPROVED` / `HUMAN_REJECTED` history events have no `trace_id` | Medium | `src/evidence_rag/record_store.py` | **OPEN (P2 for Rhugved)** | Assigned to Rhugved: copy `record.trace_id` into every history event. |
| **QA-004** *(Tester Finding)* | `_read_store` returns `{}` on parse error, silently discarding prior records on next save | Medium | `src/evidence_rag/record_store.py` | **OPEN (P2 for Rhugved)** | Assigned to Rhugved: fail closed on parse error and transition to MASTERDB transactional persistence. |
| **QA-005** *(Tester Finding)* | UX self-XSS: reviewer and notes interpolated unescaped into `innerHTML` (lines 984–985) | Medium / High | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Implemented `escapeHtml()`, escaped reviewer & notes output, and added CSP meta tag. |
| **QA-006** *(Tester Finding)* | UX/backend validation mismatch (placeholders, blank notes) | Medium | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Normalized reviewer string check, disallowed `anonymous`, `default`, `.`, and enforced non-blank notes (min 5 chars). |
| **QA-007** *(Tester Finding)* | UX accepts budget 0 and negative (-500) and displays "APPROVE" | Low | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Added strict validation requiring `budget > 0` and finite number before evaluating. |
| **QA-008** *(Tester Finding)* | Budget >$50k max gets "REJECT/ESCALATE" recommendation but approval form remained enabled | Medium | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Blocked standard approval on budgets over $50k unless authorized executive exception is recorded. |
| **QA-009** *(Tester Finding)* | Modal lacks Escape key handling and focus management | Medium | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Added `Escape` key event listener, focus movement into modal on open, and return focus to toggle button on close. |
| **QA-010** *(Tester Finding)* | "Pause AI" in UX was cosmetic only | Low | `05_UX/cmo_first_time_user_prototype.html` | **CLOSED (Fixed 19 Nov)** | Updated logic to suppress automated recommendations when paused and show raw policy facts only. |
| **QA-011** *(Tester Finding)* | Environment differs from brief (Python 3.13.7 vs 3.11.9 global interpreter) | Medium | Test Environment | **OPEN (Tester Environment Note)** | Brief specifies `.venv` with Python 3.11.9 and pinned `numpy==1.26.4`. Tester ran on global Python 3.13.7. CI pipeline will enforce pinned Python 3.11.9 container. |
| **QA-012** *(Tester Finding)* | Test suite modifies tracked files (`records.json`, `latest_evaluation_run.json`, `rag_system.log`) | Medium | `tests/conftest.py` | **OPEN (P2 for Rhugved)** | Tests should output to temporary directories (`tmp_path`) instead of mutating tracked files. |
| **QA-013** *(Tester Finding)* | Stale samples beside V2 samples in `evidence_packet/` | Low | `evidence_packet/` | **OPEN** | Flagged for PMC archival cleanup in `evidence_packet/archive/`. |
| **QA-014** *(Tester Finding)* | Citations have `quote: null` and truncated chunk statements | Medium | `src/evidence_rag/evidence.py` | **OPEN (P2)** | Store exact quote span and complete sentence boundaries during citation extraction. |
| **QA-015** *(Tester Finding)* | Docs vs code: "authenticated" reviewer vs unauthenticated free text; 48h rule proposed | Medium | Documentation | **OPEN / ALIGNED** | Aligned terminology to "recorded reviewer" until TANTRA RS256 token is wired; 48h rule marked `PROPOSED`. |
| **QA-016** *(Tester Finding)* | `generation.py` has direct Gemini/Groq/xAI client calls (opt-in) | Medium | `src/evidence_rag/generation.py` | **OPEN** | Direct cloud model calls must remain gated behind the authorized platform model gateway. |

---

## 2. Platform & Integration Blockers

| Blocker ID | Blocker Description | Impacted System / Workstream | Status | Owner | Exact Dependency / Unblock Condition |
|---|---|---|---|---|---|
| **BLK-001** | **TANTRA Sarathi RS256 production Bearer token not issued for `CMO_AGENT`** | MASTERDB Production (`https://bhiv-masterdb-ingestion-certification.onrender.com`) & Path B Staging | `BLOCKED` | Platform Security (TANTRA) + Kavy | Issue production RS256 token (`iss: tantra-sarathi`, `aud: masterdb`, `sub: cmo-agent`, role `cmo-agent`) so protected `/capabilities` passes `401 DENY:MISSING_IDENTITY`. |
| **BLK-002** | **`MASTERDB_DATABASE_URL` unconfigured on Render production** (service runs ephemeral SQLite fallback across container restarts) | MASTERDB Production Persistence (`Kavy/masterdb_deployment_status.md`) | `BLOCKED` | Kavy + Render Infrastructure Admin | Provision persistent PostgreSQL connection string in Render production env vars and verify persistence across restart. |
| **BLK-003** | **Path B FastAPI Microservice & `Dockerfile` not yet implemented in `evidence-grounded-rag-main`** | Path B Runtime Integration (`CMO Kernel → FastAPI → MASTERDB`) | `PROPOSED` / `BLOCKED` (Exam Leave) | Rhugved | Rhugved returns from university exams (target post-20 Nov) and merges FastAPI wrapper + Docker + MASTERDB adapter PR (Post-EOD Task 1). |
| **BLK-004** | **MDU formal schema registration & lineage IDs not issued** | MDU Schema Provenance | `BLOCKED` | MDU Schema Authority + Hariom + Pratik | Register 5 CMO v2 contracts + `cmo_marketing_intelligence.schema.json` with MDU Parakosha (`https://parakosha.blackholeinfiverse.com`). |
| **BLK-005** | **ARTHA finance review not completed** | ARTHA Read-Only Economics (`cmo.artha_economics.v2`) | `PROPOSED` | ARTHA Finance Team + Pratik | Complete joint review of read-only (`GET`-only) economics schema; zero ledger write authority granted. |
| **BLK-006** | **Workflow Executor real-world campaign activation strictly unauthorized** | Real-world ad publishing / POs | `BLOCKED` (Intentional Governance Gate) | GC SHAKTI / Executive Leadership | Requires separate formal executive permission in a future phase; **this sprint grants zero real-world execution permissions**. |
| **BLK-007** | **BIQOS / CXO Suite workspace route & role-scoped shell slot not assigned** | BIQOS / CXO Suite Integration (`05_UX/`) | `PROPOSED` | BIQOS / CXO Suite Lead + Pratik | Assign canonical workspace route, identity scoping, and navigation entry for Post-EOD Task 3. |
| **BLK-008** | **Bucket / InsightFlow live ingestion endpoints not wired** | Telemetry / Replay Observability | `PROPOSED` | Bucket / InsightFlow Owner + Rhugved | Provide live trace ingestion URL/auth so Path B FastAPI exports `trace_id` and audit events automatically. |

---

## 3. Team Availability & Handover Gaps (Honest Attribution)

| Gap ID | Member | Availability State | Missing / Pending Item | Owner & Dependency |
|---|---|---|---|---|
| **GAP-001** | **Tester** | Completed (19 Nov 2026) | Independent verification complete: `CONDITIONAL PASS (63/100) — VERIFIED NON-PRODUCTION` | **Tester** — Report committed in `01_INDIVIDUAL_SUBMISSIONS/TESTER_VERIFICATION.md`. |
| **GAP-002** | **Parikshak** | Active (Awaiting Submission Handoff) | Evidence synthesis, canonical state update, priority recommendations on 3 next tasks | **Parikshak** — Awaiting submission package + Tester verdict (`03_PARIKSHAK_REVIEW.md` is strictly PENDING). |
| **GAP-003** | **Kavy** | Active (Nov 17 handover on disk) | Direct 18 Nov individual confirmation (`01_INDIVIDUAL_SUBMISSIONS/KAVY.md`) if available before EOD | **Kavy** — existing 9 reports in `Kavy/` already audited. |
| **GAP-004** | **Rhugved** | University Exam Leave | FastAPI adapter, `Dockerfile`, staging PR, missing `rhugved_runtime_validation_report.md` | **Rhugved** — pending return from exams. |
| **GAP-005** | **Hariom Upadhyay** | University Exam Leave | Git push of 7 local data-quality evaluation deliverables (`CMO_V2_DATA_CORPUS_EVALUATION_HARIOM.md`, 3 scripts, 3 JSONs) | **Hariom Upadhyay** — pending return from exams. |
| **GAP-006** | **Rupam Patne** | Extended Leave | Clarification on Path B adapter error/retry mapping & live-corpus threshold tuning | **Rupam Patne** — existing WP1–WP6 artifacts audited; clarifications marked `PENDING`. |
| **GAP-007** | **Nupur** | Extended Leave | Formal PMC archival reconciliation of duplicate `evidence_packet/` folders & live checkpoint sign-off | **Nupur** — existing records audited; gaps marked `PENDING`. |

---

## 4. Key Risks & Mitigations

1. **Risk — Conflating Local Kernel Success with Production Readiness:** *Mitigation:* Strictly enforced 6-term allowed vocabulary across all EOD documents; Path B explicitly split into `SELECTED` (PO decision), `VERIFIED NON-PRODUCTION` (local kernel + local MASTERDB handshake), `PROPOSED` (FastAPI adapter), and `BLOCKED` (production MASTERDB RS256 & persistence).
2. **Risk — Self-Verification Governance Breach:** *Mitigation:* Pratik explicitly disclaims independent verification authority and hands off all reproducible commands, traces, UX prototype, and 36-capability registry to **Tester** and **Parikshak**.
3. **Risk — Ephemeral Render Storage Causing Data Loss in Staging/Prod:** *Mitigation:* Escalated `BLK-002` (`MASTERDB_DATABASE_URL`) directly into Post-EOD Task 2 acceptance criteria so staging/production cannot be certified on ephemeral SQLite.
