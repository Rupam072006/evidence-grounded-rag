# Next Three Post-EOD Tasks (Proposed for Parikshak Review & Niyantran Routing)

| Field | Value |
|---|---|
| **Proposed By** | Pratik Bhuwad (CMO Product Owner / Sprint Lead) |
| **Timestamp** | `2026-11-18T13:25:00+05:30` |
| **Task Count** | **Exactly 3 tasks** (strictly complying with DoD AC-09) |
| **Routing Control** | **Parikshak** reviews and recommends priority/adjustments; **Executive Leadership** authorizes next phase; **Niyantran** routes authorized tasks. |

---

## Task 1 — Rhugved — Build & Containerize Path B FastAPI Adapter and Local MASTERDB Client (CMO Agent V2 – Path B Runtime Implementation)

- **Objective:** Transition the locally verified `src/evidence_rag/` kernel (`136/136` tests) into a containerized Path B FastAPI microservice wired to the local MASTERDB testbed (`cap-cmo-marketing-intelligence`) and eliminate relative-CWD test fragility (`DEF-REPRO-001`), while preserving zero shadow databases and the `AWAITING_APPROVAL` hard stop.
- **Scope:**
  - Implement FastAPI service wrapping `src/evidence_rag/` (`/api/v1/query`, `/api/v1/proposals/evaluate`, `/api/v1/proposals/{id}/approve`, `/api/v1/proposals/{id}/reject`, `/api/v1/proposals/{id}/replay`, `/api/v1/health`).
  - Implement `MasterDBPersistenceAdapter` calling local MASTERDB capability endpoints (`/capabilities/cap-cmo-marketing-intelligence`, `/access/request`) instead of flat-file `records.json`.
  - Add reproducible `Dockerfile`, `.dockerignore`, and `docker-compose.yml` for local CMO + MASTERDB integration.
  - Fix `DEF-REPRO-001` so `pytest` resolves `data/index` and `data/manifest.json` relative to repo root regardless of CWD.
  - Attach structured `trace_id` logging ready for Bucket/InsightFlow export.
- **Non-goals:**
  - No parallel RAG store, vector DB, model gateway, or shadow database.
  - No real-world ad publishing, campaign activation, Workflow Executor writes, or ARTHA ledger mutations.
  - No production Render deployment until Task 2 RS256 credentials & persistent DB URL are provisioned.
- **Owner / Reviewer:**
  - **Owner:** Rhugved (Runtime / Backend Integration Lead)
  - **Reviewer:** Pratik Bhuwad (CMO PO — contract acceptance) + Kavy (MASTERDB seam review) + Tester (Independent Verification)
- **READ THIS FIRST:**
  1. `CMO_V2_EOD_CONVERGENCE/01_INDIVIDUAL_SUBMISSIONS/PRATIK_BHUWAD.md`
  2. `rupam_handover/05_integration_assessment.md` (FastAPI endpoint & 16-field mapping spec)
  3. `Kavy/handover.md` & `Kavy/masterdb_handshake.md` (MASTERDB local startup & access grant flow)
  4. `CMO_V2_EOD_CONVERGENCE/08_DEFECTS_RISKS_AND_BLOCKERS.md` (`DEF-REPRO-001`, `BLK-003`)
- **Dependencies:**
  - Executive authorization of the next runtime integration phase.
  - Rhugved's return from university exams (Target start: `2026-11-21`; Target completion: `2026-11-24`).
  - Local `masterdb-ingestion-certification-service` running (`commit 284ef75`).
- **Integration Points:**
  - Upstream: `src/evidence_rag/` kernel (`main` @ `db032d6`).
  - Downstream: Local MASTERDB FastAPI (`http://127.0.0.1:8000`, `cap-cmo-marketing-intelligence`).
  - Auth seam: Fail-closed TANTRA JWT middleware stub accepting test RSA keypair locally.
- **Execution Phases (`Learn → Build → Integrate → Test → Document → Handover`):**
  1. **Learn:** Review `05_integration_assessment.md`, `Kavy/handover.md`, and `DEF-REPRO-001`.
  2. **Build:** Implement FastAPI routes, Pydantic schemas, `MasterDBPersistenceAdapter`, CWD path fix, and `Dockerfile`.
  3. **Integrate:** Wire FastAPI container to local MASTERDB testbed over RS256 test JWT (`CMO_AGENT`).
  4. **Test:** Run full `136+` pytest suite (from both repo root and parent dir), FastAPI integration tests, and Docker container smoke probes.
  5. **Document:** Update OpenAPI spec, `README.md`, and runbook with exact build/run commands.
  6. **Handover:** Open clean PR on `main`, generate `REVIEW_PACKET.md` & evidence packet, and hand off to Tester.
- **Deliverables:**
  - FastAPI router & adapter code in `src/evidence_rag/api/`
  - `Dockerfile` + `docker-compose.yml` + OpenAPI JSON
  - Clean PR merged/reviewed on `main`
- **Acceptance Criteria:**
  - `docker build` & `docker run` start cleanly; `GET /api/v1/health` returns `200 OK`.
  - `POST /api/v1/proposals/evaluate` for `REQ-MKT-2026-LI-01` retrieves certified data from local MASTERDB, flags $15k LinkedIn cap variance, and halts at `AWAITING_APPROVAL` with zero side effects.
  - Linear TV proposal returns `INSUFFICIENT_EVIDENCE` with `null` metrics.
  - `pytest` passes `100%` regardless of working directory (`DEF-REPRO-001` closed).
- **Tests:** All existing 136 unit/functional/security/replay tests + new FastAPI endpoint tests + local MASTERDB adapter contract tests + negative auth (`401/403`) tests.
- **`REVIEW_PACKET.md`:** Required inside PR folder summarizing architecture diff, API samples, test counts, and defect closures.
- **Evidence Packet:** Saved Docker build logs, OpenAPI JSON, curl/HTTP request-response traces (`AWAITING_APPROVAL`, `Prof_Evaluator` rejection, explicit approval, duplicate rejection, Linear TV abstention), and pytest output.
- **Rollback:** Revert PR commit on `main`; kernel CLI (`src/evidence_rag/cli.py`) remains completely unaffected and reproducible at `db032d6`.
- **Handover:** Operational runbook + env var table handed to Kavy (for Task 2 staging wiring) and Tester (for independent sign-off).

---

## Task 2 — Kavy & Platform Security — TANTRA Sarathi RS256 Production Handshake, Render DB Persistence & Hariom Data-Quality Push (CMO Agent V2 – Staging Auth & Data Integrity Convergence)

- **Objective:** Unblock `BLK-001` and `BLK-002` by provisioning authoritative TANTRA Sarathi RS256 credentials for `CMO_AGENT`, configuring persistent `MASTERDB_DATABASE_URL` (PostgreSQL) on Render staging/production, registering CMO schemas with MDU, and pushing + verifying Hariom's 7 pending data-quality benchmark artifacts.
- **Scope:**
  - Provision TANTRA Sarathi RS256 token / JWKS config for `sub: cmo-agent`, `application_id: CMO_AGENT`, `aud: masterdb`.
  - Configure persistent PostgreSQL `MASTERDB_DATABASE_URL` on Render (`https://bhiv-masterdb-ingestion-certification.onrender.com`) eliminating ephemeral SQLite fallback.
  - Execute authenticated staging handshake against `GET /capabilities/cap-cmo-marketing-intelligence` and `POST /access/request` with zero secret leakage.
  - Submit the 5 CMO v2 contracts + `cmo_marketing_intelligence.schema.json` for formal MDU registration (`BLK-004`).
  - Push Hariom Upadhyay's 7 local benchmark/evaluation files to remote repo and verify `DEFECT-SEMANTIC-001` + corpus freshness/provenance regression.
- **Non-goals:**
  - No enabling of `POST /auth/token` on production MASTERDB (must stay disabled / fail closed).
  - No bypassing RS256 verification or hardcoding secrets in git.
  - No real-world campaign execution or ARTHA ledger writes.
- **Owner / Reviewer:**
  - **Owner:** Kavy (MASTERDB Platform Lead) + Platform Security (TANTRA/VAJRA) + Hariom Upadhyay (Data Quality push)
  - **Reviewer:** Pratik Bhuwad (CMO PO) + Tester (Independent Verification)
- **READ THIS FIRST:**
  1. `Kavy/masterdb_deployment_status.md` (`BLK-001`, `BLK-002`)
  2. `Kavy/masterdb_auth_audit.md` & `Kavy/masterdb_handshake.md`
  3. `CMO_V2_EOD_CONVERGENCE/07_BIQOS_CXO_INTEGRATION/INTEGRATION_MATRIX.md`
  4. `CMO_V2_EOD_CONVERGENCE/08_DEFECTS_RISKS_AND_BLOCKERS.md` (`GAP-005`)
- **Dependencies:**
  - Platform Security authorization for TANTRA Sarathi RS256 key/token issuance.
  - Render admin access for PostgreSQL `MASTERDB_DATABASE_URL`.
  - Hariom's return from exams for git push (Target window: `2026-11-20` to `2026-11-24`).
- **Integration Points:**
  - TANTRA Sarathi (RS256 JWT issuer) → MASTERDB Render (`v1.3.0`) → MDU Parakosha (`https://parakosha.blackholeinfiverse.com`) → Path B CMO FastAPI adapter (Task 1).
- **Execution Phases (`Learn → Build → Integrate → Test → Document → Handover`):**
  1. **Learn:** Audit Render env vars, TANTRA JWKS config, MDU schema submission requirements, and Hariom's local branch diff.
  2. **Build:** Configure `MASTERDB_DATABASE_URL`, provision scoped `CMO_AGENT` RS256 credentials, and prepare MDU schema registration payload.
  3. **Integrate:** Execute staging authenticated handshake (`CMO_AGENT → MASTERDB`) and push Hariom's 7 evaluation files into canonical repo.
  4. **Test:** Verify `200 OK` authenticated retrieval, `401` on invalid/missing token, DB persistence across Render restart, and full reproducibility of Hariom's 14-query benchmark.
  5. **Document:** Update `INTEGRATION_MATRIX.md` (promoting staging items only where proven), `masterdb_deployment_status.md`, and data-quality report.
  6. **Handover:** Deliver sanitized logs, `REVIEW_PACKET.md`, and evidence packet to Tester.
- **Deliverables:**
  - Redacted staging RS256 handshake transcript (`200 OK` + SHA-256 digest + `401` negative proof)
  - Render persistence verification log (pre/post restart read proof)
  - MDU schema registration receipt / tracking ID
  - Pushed remote commit containing Hariom's 7 evaluation deliverables
- **Acceptance Criteria:**
  - Authenticated staging `GET /capabilities/cap-cmo-marketing-intelligence` returns `200 OK` with valid Draft 2020-12 payload; unauthenticated request returns `401 DENY:MISSING_IDENTITY`.
  - Certified record survives Render container restart (confirming PostgreSQL persistence).
  - Hariom's benchmark scripts run cleanly in `.venv` reproducing Recall@4, citation validity, and `DEFECT-SEMANTIC-001` Linear TV abstention.
  - Zero tokens/secrets committed to git or logs.
- **Tests:** MASTERDB `100/100` security/validation suite + staging restart durability test + Hariom benchmark regression script + secret-leakage scan.
- **`REVIEW_PACKET.md`:** Security & data-integrity review packet documenting token scope, DB persistence proof, MDU registration state, and Hariom benchmark parity.
- **Evidence Packet:** Redacted HTTP probe logs, SHA-256 verification outputs, Render restart check log, and committed benchmark JSON results.
- **Rollback:** Revoke `CMO_AGENT` staging token via TANTRA immediately on anomaly; revert Render env change; revert git branch if benchmark scripts break CI.
- **Handover:** Staging connection & auth contract handed to Rhugved (Task 1) and BIQOS/CXO UI team (Task 3).

---

## Task 3 — Pratik Bhuwad & BIQOS/CXO UI Lead — Wire First-Time-User UX into Shared BIQOS / CXO Suite Workspace & Connect Telemetry (CMO Agent V2 – Founder Workspace & UX Convergence)

- **Objective:** Integrate the validated 5-screen first-time-user UX flow (`05_UX/`) into the shared founder-controlled **BIQOS / CXO Suite** workspace route (no shadow dashboard shell), wire it to the staging Path B FastAPI service (Task 1) + Bucket/InsightFlow trace correlation, and validate usability and anti-manipulation compliance with real first-time test users.
- **Scope:**
  - Register the CMO workspace route, navigation entry, and TANTRA/VAJRA role-scoped access inside the shared BIQOS / CXO Suite frontend.
  - Connect the 5-screen guided UI (*Welcome → Next Best Action → Guided Plan → Facts/Unknowns/Recommendation → Human Approval*) + User Control Drawer (*Pause, Mute, Inspect, Revoke, Delete*) to staging Path B FastAPI endpoints.
  - Wire structured `trace_id` correlation from UI → FastAPI → Bucket / InsightFlow replay viewer.
  - Complete read-only `cmo.artha_economics.v2` contract review with ARTHA finance team.
  - Run structured usability testing with 3–5 non-technical first-time users measuring **task completion rate, comprehension, user control usage, and time-to-completion** (never time-on-app).
- **Non-goals:**
  - No standalone/shadow dashboard shell outside BIQOS / CXO Suite.
  - No autonomous ad publishing, campaign activation, or Workflow Executor triggers (execution remains strictly gated pending separate executive permission).
  - No addictive loops, streaks, infinite feeds, covert tracking, or deceptive urgency.
- **Owner / Reviewer:**
  - **Owner:** Pratik Bhuwad (CMO PO) + BIQOS / CXO Suite Frontend Lead
  - **Reviewer:** Tester (Independent UX, accessibility, anti-manipulation & E2E verification) + Parikshak (Convergence review)
- **READ THIS FIRST:**
  1. `CMO_V2_EOD_CONVERGENCE/05_UX/cmo_first_time_user_prototype.html` & `UX_FLOWS_AND_WALKTHROUGH.md`
  2. `CMO_V2_EOD_CONVERGENCE/06_AGENT_ARCHITECTURE/AGENT_CAPABILITY_REGISTRY.md` & `ORCHESTRATION_AND_GOVERNANCE.md`
  3. `CMO_V2_EOD_CONVERGENCE/07_BIQOS_CXO_INTEGRATION/INTEGRATION_MATRIX.md`
  4. Outputs of Post-EOD Task 1 (FastAPI staging URL) & Task 2 (RS256 staging auth)
- **Dependencies:**
  - Completion of Task 1 (Path B FastAPI staging endpoints) & Task 2 (TANTRA staging auth).
  - BIQOS / CXO Suite route allocation & Bucket/InsightFlow trace endpoint availability (Target window: `2026-11-25` to `2026-11-28`).
- **Integration Points:**
  - Shared BIQOS / CXO Suite shell (auth, nav, role scoping) ↔ Path B FastAPI (`POST /api/v1/proposals/evaluate`, `/approve`, `/replay`) ↔ Bucket / InsightFlow (`trace_id`) ↔ ARTHA (read-only contract review).
- **Execution Phases (`Learn → Build → Integrate → Test → Document → Handover`):**
  1. **Learn:** Review BIQOS shell conventions, role-scoping rules, and Tester's EOD feedback on `05_UX/`.
  2. **Build:** Implement the 5 guided screens + accessibility controls + User Control Drawer inside the shared BIQOS workspace route.
  3. **Integrate:** Connect UI to staging Path B FastAPI endpoints and Bucket/InsightFlow trace inspector; complete ARTHA read-only contract sign-off.
  4. **Test:** Execute E2E Playwright/Cypress + WCAG AA accessibility + anti-manipulation + user-control revocation tests + 3–5 first-time-user comprehension sessions.
  5. **Document:** Publish UX usability metrics, BIQOS route docs, and updated `INTEGRATION_MATRIX.md`.
  6. **Handover:** Deliver live staging walkthrough demo, `REVIEW_PACKET.md`, and evidence packet to Tester and Founders.
- **Deliverables:**
  - Live staging CMO workspace route inside shared BIQOS / CXO Suite
  - E2E + accessibility + anti-manipulation test suite results
  - First-time-user usability & comprehension evaluation report
  - Signed ARTHA read-only contract review memo
- **Acceptance Criteria:**
  - Founder/PO authenticates into shared BIQOS / CXO Suite, runs `REQ-MKT-2026-LI-01` ($30k LinkedIn) and `TEST-TV-DEFECT-CHECK` (Linear TV) live against staging FastAPI, inspects cited facts + unknowns + `AWAITING_APPROVAL` hard stop, and replays the matching `trace_id` in Bucket/InsightFlow.
  - All 5 user controls (*Pause, Dismiss/Mute, Inspect, Revoke, Delete Draft*) work end-to-end; revoking corpus access blocks backend reads cleanly.
  - Zero manipulative patterns, zero covert tracking, WCAG 2.1 AA contrast & 48px tap targets verified.
  - Zero real-world campaign activation or ARTHA ledger mutations occur.
- **Tests:** Automated UI E2E tests (happy path, cap variance, Linear TV abstention, `Prof_Evaluator` rejection, duplicate rejection, permission revocation) + WCAG AA audit + Bucket/InsightFlow trace parity test.
- **`REVIEW_PACKET.md`:** Consolidated UX & workspace integration review packet with screenshots, route config, usability scores, and anti-manipulation audit.
- **Evidence Packet:** Recorded staging walkthrough, E2E test logs, Bucket/InsightFlow trace screenshots, accessibility report, and usability test logs.
- **Rollback:** Feature-flag disable the CMO route in BIQOS navigation manifest without affecting other CXO Suite workspaces; zero backend state lost.
- **Handover:** Complete founder-ready staging demo & operational guide handed to BIQOS Operations, Tester, and Executive Leadership for next-phase authorization.
