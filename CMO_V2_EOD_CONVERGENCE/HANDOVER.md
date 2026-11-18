# Handover Guide — CMO Agent V2 EOD Convergence Package

| Field | Value |
|---|---|
| **Author** | Pratik Bhuwad (CMO Product Owner / EOD Convergence Sprint Lead) |
| **Timestamp** | `2026-11-18T13:30:00+05:30` |
| **Package Root** | `c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main\CMO_V2_EOD_CONVERGENCE\` |
| **Canonical Repo / Branch / Commit** | `c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main` (`main` @ `db032d6`) |
| **MASTERDB Reference Repo / Commit** | `masterdb-ingestion-certification-service` (`main` @ `284ef75`, audited in `c:\Pratik_Bhuwad\CMO_Agent\Kavy\`) |
| **History Preservation** | Confirmed — zero prior evidence files in `evidence_packet/`, `rupam_handover/`, `Kavy/`, `audit_reports/`, or `evidence-grounded-rag-main/` were modified or overwritten. |

---

## 1. Complete Package Inventory (Matches Prescribed Page 6 Layout)

```text
CMO_V2_EOD_CONVERGENCE/
├── 00_EXECUTIVE_SUMMARY.md                                 # Executive state summary + 4 Executive Decisions Required
├── 01_INDIVIDUAL_SUBMISSIONS/
│   ├── PRATIK_BHUWAD.md                                    # Pratik PO submission, Path B classification, non-goals, escalation
│   ├── UNAVAILABLE_AND_EXISTING_ARTIFACT_AUDIT.md          # Honest audit of Kavy/Rhugved/Rupam/Nupur/Hariom existing artifacts & gaps
│   └── TESTER_HANDOFF_BRIEF.md                             # Ready-to-run independent verification checklist for Tester (PENDING)
├── 02_COLLECTIVE_CONVERGENCE_REPORT.md                     # Assigned-vs-delivered matrix across all 8 roles + 10-point DoD status
├── 03_PARIKSHAK_REVIEW.md                                  # Structured review slot & input index for Parikshak (PENDING)
├── 04_TEST_AND_RUNTIME_EVIDENCE/
│   └── TEST_RECONCILIATION_AND_REPRODUCTION.md             # Test reconciliation (126→130→132→136 + 100 MASTERDB), live run & trace index
├── 05_UX/
│   ├── cmo_first_time_user_prototype.html                  # Clickable 5-screen accessible HTML prototype (SIMULATED, zero trackers)
│   └── UX_FLOWS_AND_WALKTHROUGH.md                         # Annotated flows, accessibility & anti-manipulation checklist
├── 06_AGENT_ARCHITECTURE/
│   ├── AGENT_CAPABILITY_REGISTRY.md                        # 36 governed capabilities across 6 domains × all 15 mandatory fields
│   └── ORCHESTRATION_AND_GOVERNANCE.md                     # Orchestration flow, handoff invariants, consent & escalation rules
├── 07_BIQOS_CXO_INTEGRATION/
│   └── INTEGRATION_MATRIX.md                               # 8-system evidence-backed integration matrix (strict 6-term vocabulary)
├── 08_DEFECTS_RISKS_AND_BLOCKERS.md                        # Active/closed defects (incl. DEF-REPRO-001), BLK-001..008, GAP-001..007
├── 09_NEXT_THREE_TASKS.md                                  # Exactly 3 post-EOD tasks in exact Page 6 Candidate format
└── HANDOVER.md                                             # This operational handover & reproduction guide
```

---

## 2. Quick Reproduction Commands (For Tester & Next-Phase Engineers)

### A. Reproduce CMO Kernel Baseline (`136/136` Tests)
> **Important (`DEF-REPRO-001`):** Run from inside `evidence-grounded-rag-main/` so relative `data/index` resolves cleanly.

```powershell
Push-Location "c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main"
& "c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe" -m pytest tests -q --tb=short
Pop-Location
```

### B. Reproduce LinkedIn Commercial & Approval Integrity Suites (`16/16` Tests)
```powershell
Push-Location "c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main"
& "c:\Pratik_Bhuwad\CMO_Agent\.venv\Scripts\python.exe" -m pytest tests/functional/test_v2_linkedin_acceptance.py tests/task3/test_task3_approval_integrity.py -v
Pop-Location
```

### C. Open & Validate First-Time-User UX Prototype (Offline, Zero Dependencies)
Open directly in Chrome or Edge:
`c:\Pratik_Bhuwad\CMO_Agent\evidence-grounded-rag-main\CMO_V2_EOD_CONVERGENCE\05_UX\cmo_first_time_user_prototype.html`
- Test **Goal 1 (LinkedIn $30k)** → verifies `$15,000` cap variance warning, cited facts, explicit unknowns, `Prof_Evaluator`/blank rejection, explicit named approval, and duplicate rejection.
- Test **Goal 2 (Linear TV)** → verifies `INSUFFICIENT_EVIDENCE` abstention (`DEFECT-SEMANTIC-001`).
- Test **Your Controls & Privacy** → verifies Pause AI, Mute Tips, Revoke Corpus Access (blocks Screen 4 reads), Inspect Trace, and Delete Draft.

---

## 3. Immediate Role-by-Role Handover Actions (Before EOD Today)

1. **Tester (IMMEDIATE — Independent Verification):**
   - Follow `01_INDIVIDUAL_SUBMISSIONS/TESTER_HANDOFF_BRIEF.md`.
   - Independently run the pytest commands, verify commercial traces (`evidence_packet/`), inspect `05_UX/` and `06_AGENT_ARCHITECTURE/`, audit `02_COLLECTIVE_CONVERGENCE_REPORT.md` & `08_DEFECTS_RISKS_AND_BLOCKERS.md`, and submit `01_INDIVIDUAL_SUBMISSIONS/TESTER_VERIFICATION.md` with conservative score & verdict.
2. **Parikshak AI Agent (AFTER TESTER — Automated AI Review & Task Intelligence):**
   - Submit the assembled `CMO_V2_EOD_CONVERGENCE/` package (with Tester's verdict) into the **Parikshak AI agent** workflow.
   - Parikshak automatically populates `03_PARIKSHAK_REVIEW.md` with evidence analysis, gap report, canonical state update, convergence verdict, and recommended priority/adjustments for the 3 tasks in `09_NEXT_THREE_TASKS.md`. *(Per PDF Page 3 control rule: Parikshak is an AI agent that recommends only — authorised task routing is performed by Niyantran following Executive decision.)*
3. **Kavy (IF AVAILABLE BEFORE EOD):**
   - Optionally append a brief 18 Nov confirmation (`01_INDIVIDUAL_SUBMISSIONS/KAVY.md`) confirming `BLK-001` (TANTRA RS256 token) and `BLK-002` (Render `MASTERDB_DATABASE_URL`) remain the exact production blockers.
4. **Unavailable Teammates (Post-Leave / Post-Exam Handover):**
   - **Rhugved:** Pick up **Post-EOD Task 1** (Path B FastAPI adapter + Docker + local MASTERDB + `DEF-REPRO-001` fix) after exams.
   - **Hariom Upadhyay:** Push 7 local evaluation files and co-execute **Post-EOD Task 2** after exams.
   - **Rupam Patne & Nupur:** Review logged pending clarifications (`GAP-006`, `GAP-007`) upon return from extended leave.
5. **Executive Leadership / Niyantran:**
   - Decide the **4 Executive Decisions Required** in `00_EXECUTIVE_SUMMARY.md` (`ED-1` through `ED-4`) and route authorized tasks via **Niyantran**.
