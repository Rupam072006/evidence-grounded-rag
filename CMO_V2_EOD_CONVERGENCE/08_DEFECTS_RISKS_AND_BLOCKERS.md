# Defects, Risks, Gaps & Blockers Register

| Field | Value |
|---|---|
| **Author** | Pratik Bhuwad (CMO Product Owner / Sprint Lead) |
| **Timestamp** | `2026-11-18T13:25:00+05:30` |
| **Canonical Repo / Commit** | `evidence-grounded-rag-main` (`main` @ `db032d6`) & `masterdb-ingestion-certification-service` (`main` @ `284ef75`) |
| **Verification Status** | `VERIFIED NON-PRODUCTION` (Pending Independent Audit & Conservative Scoring by **Tester**) |

---

## 1. Historical & Active Code / Runtime Defects

| Defect ID | Title & Description | Severity | Repo / Component | Status | Evidence / Resolution Notes |
|---|---|---|---|---|---|
| **DEF-001 to DEF-006** | Historical Task 2 Day 1 defects (`httpx` packaging, corpus fingerprint hashing, `INDEX_UNAVAILABLE` status, unicode lenticular citation regex, HTTP 429 retry, dynamic conflict pair registry) | High–Low | `evidence-grounded-rag-main` | **CLOSED (Local Verified)** | Documented in `evidence-grounded-rag-main/evidence_packet/defect_register.md`; covered by passing `136/136` suite. |
| **DEFECT-SEMANTIC-001** | Hallucinated Linear TV metrics instead of semantic abstention | High | `src/evidence_rag/workflow.py` / `confidence.py` | **CLOSED (Local Verified — Pending Hariom Push & Tester Re-Verify)** | Discovered by Hariom Upadhyay; verified returning `INSUFFICIENT_EVIDENCE` & `null` metrics in `evidence_packet/api_samples/defect_semantic_001_linear_tv_blocked.json` and `test_workflow.py::test_workflow_linear_tv_abstains_insufficient_evidence`. |
| **DEF-MASTERDB-001** | Unhandled `NameError: name 'Path' is not defined` in CMO HTTP retrieval branch | High | `masterdb-ingestion-certification-service/services/capability_registry_service.py:1639` | **CLOSED (Audited by Kavy)** | Fixed (`from pathlib import Path`) + regression test `test_cmo_capability_http_retrieval_endpoint_regression` added (`Kavy/masterdb_test_report.md`, `100/100` passing). |
| **DEF-REPRO-001** *(New — Caught 18 Nov)* | Relative path CWD dependency in test suite (`IndexNotFoundError` when `pytest` runs from parent folder `c:\Pratik_Bhuwad\CMO_Agent`) | Medium | `evidence-grounded-rag-main/src/evidence_rag/pipeline.py` & `tests/` | **OPEN** | Running `pytest evidence-grounded-rag-main/tests` from parent dir yields 9 failed / 27 errors (`C:\Pratik_Bhuwad\CMO_Agent\data\index` missing). Running inside `evidence-grounded-rag-main/` passes `136/136`. Needs repo-relative path resolution in Post-EOD Task 1. |
| **DEF-DOC-001** *(New — Caught 18 Nov)* | Trace ID mismatch between Nov 17 prose docs (`TRC-20261116-6C7BDA95`) and persisted JSON/log artifacts (`TRC-20261116-1833C82E`) | Low | `PRATIK_BHUWAD_PO_DELIVERABLE_V2.md`, `CMO_V2_EVIDENCE_BASED_CLOSURE_SUBMISSION.md` | **OPEN (Documented for Tester)** | Preserved historical files untouched; reconciled transparently in `04_TEST_AND_RUNTIME_EVIDENCE/TEST_RECONCILIATION_AND_REPRODUCTION.md`. |
| **DEF-DOC-002** *(New — Caught 18 Nov)* | Duplicate/divergent `evidence_packet/` directories (`evidence-grounded-rag-main/evidence_packet/` has Oct 2026 20-doc metadata vs. root `evidence_packet/` has Nov 16 26-doc packet) + missing `rhugved_runtime_validation_report.md` referenced in Nov 17 prose | Medium | Workspace & `evidence_packet/` | **OPEN (Governance / PMC Gap)** | Preserved prior history; flagged for PMC (Nupur) archival cleanup and Tester audit. |
| **DEF-GOV-001** *(Executive Escalation)* | Ownership-document naming conflict (`Pratik Bhuwad` vs. `Prateek` in `rupam_handover/05_integration_assessment.md` vs. `Pratik Bhuvad` in `Kavy/handover.md`) | Medium | Cross-repo governance documents | **OPEN (Executive Decision Required)** | Escalated in `00_EXECUTIVE_SUMMARY.md` & `01_INDIVIDUAL_SUBMISSIONS/PRATIK_BHUWAD.md`. |

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
| **GAP-001** | **Tester** | Active — Handoff Required Today | Independent test reproduction, assigned-vs-delivered audit, UX/agent review, conservative score & verdict | **Tester** — depends on receiving this EOD package (`01_INDIVIDUAL_SUBMISSIONS/TESTER_HANDOFF_BRIEF.md`). |
| **GAP-002** | **Parikshak** | Active — Handoff Required Today | Evidence analysis, gap report, canonical state update, validation of 3 next tasks (`03_PARIKSHAK_REVIEW.md`) | **Parikshak** — depends on Tester verdict + consolidated submissions. |
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
