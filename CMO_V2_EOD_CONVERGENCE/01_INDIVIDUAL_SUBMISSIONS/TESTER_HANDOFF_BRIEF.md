# Independent Verification Handoff Brief — For Tester

| Field | Value |
|---|---|
| **Prepared By** | Pratik Bhuwad (CMO Product Owner / Sprint Lead) |
| **Handed Off To** | **Tester** (Independent Verification Lead) |
| **Timestamp** | `2026-11-18T13:30:00+05:30` |
| **Output File Requested** | `CMO_V2_EOD_CONVERGENCE/01_INDIVIDUAL_SUBMISSIONS/TESTER_VERIFICATION.md` |
| **Control Rule** | **No person is sole verifier of their own work.** Please challenge every claim, reproduce commands independently, and issue a conservative score and verdict. |

---

## Independent Verification Checklist (Step-by-Step)

1. **Reproduce Automated Test Baseline (DoD AC-02):**
   - Run from `c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main`:
     ```powershell
     & "c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe" -m pytest tests -q --tb=short
     ```
   - Confirm commit `db032d6`, Python `3.11.9`, and count (`136 passed` expected). Also verify `DEF-REPRO-001` (CWD sensitivity if run from parent dir).
   - Run targeted commercial & approval integrity tests:
     ```powershell
     & "c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe" -m pytest tests/functional/test_v2_linkedin_acceptance.py tests/task3/test_task3_approval_integrity.py -v
     ```
2. **Audit Commercial Traces — Separate Hard-Stop vs. Approval Paths (DoD AC-03):**
   - Inspect `c:\Pratik_Bhuwad\CMO_Agent\evidence_packet\api_samples\`:
     - `req_mkt_2026_li_01_proposal_evaluated.json` (verify `status == "AWAITING_APPROVAL"`, `approval == null`, zero external side effects)
     - `req_mkt_2026_li_01_approval_rejected_default_reviewer.json` & `..._blank_reviewer.json`
     - `req_mkt_2026_li_01_approved_record.json` & `..._duplicate_approval_rejected.json`
     - `defect_semantic_001_linear_tv_blocked.json` (verify `INSUFFICIENT_EVIDENCE` & `null` metrics)
   - Confirm `DEF-DOC-001` (Trace ID `TRC-20261116-1833C82E` in artifacts vs. `TRC-20261116-6C7BDA95` in Nov 17 prose).
3. **Challenge Path B Classification (DoD AC-04):**
   - Verify `evidence-grounded-rag-main/src/evidence_rag/` has NO FastAPI router or `Dockerfile` yet, confirming Path B is honestly classified as `SELECTED` (local kernel `VERIFIED NON-PRODUCTION`, adapter `PROPOSED`, MASTERDB prod `BLOCKED`).
4. **Inspect First-Time-User UX Prototype (DoD AC-05):**
   - Open `05_UX/cmo_first_time_user_prototype.html` in a browser.
   - Verify all 5 screens, one primary CTA per screen, Back/Undo/Cancel, LinkedIn `$30k` cap warning, Linear TV abstention, `Prof_Evaluator` rejection, User Controls drawer (Pause, Mute, Revoke Corpus Access, Inspect Trace, Delete Draft), accessibility (Large Text, High Contrast, Read Aloud), and **zero** manipulative patterns or external trackers.
5. **Audit 30+ Agent Capability Registry (DoD AC-06):**
   - Inspect `06_AGENT_ARCHITECTURE/AGENT_CAPABILITY_REGISTRY.md` & `ORCHESTRATION_AND_GOVERNANCE.md`.
   - Confirm `>= 30` capabilities (36 defined across 6 domains), all **15 mandatory fields** present per capability, zero autonomous publishing/spend capabilities, and clear design-only framing.
6. **Audit BIQOS / CXO Matrix & Non-Goal Compliance (DoD AC-07, AC-08):**
   - Inspect `07_BIQOS_CXO_INTEGRATION/INTEGRATION_MATRIX.md` — verify ONLY the 6 allowed status labels are used and every row includes evidence, owner, blocker, next action, and acceptance test.
   - Confirm zero unauthorized schema, authority, permission, or financial changes, and zero new work falsely attributed to unavailable teammates.
7. **Issue Independent Verdict & Conservative Score:**
   - Record defects found, conservative score, pass/conditional/fail verdict, and hand off directly to **Parikshak** (`03_PARIKSHAK_REVIEW.md`).
