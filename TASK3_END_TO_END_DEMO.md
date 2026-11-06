# TASK3_END_TO_END_DEMO.md
## AegisCore — End-to-End Marketing Workflow Demonstration

**Project:** AegisCore — Evidence-Grounded RAG System  
**Commit Hash:** `3703c514418f76586a08a30cf341c6d14f441fff`  
**Date:** 2026-11-06  
**Demonstration Suite:** 5 Full End-to-End Operational Scenarios  
**Evidence Reference:** `evidence_packet/end_to_end_results.json`, `data/workflow_records/records.json`

---

## 1. Realistic Marketing Campaign Scenario

### Campaign Context
AegisCore serves as an evidence-grounded decision-support system evaluating business proposals against organizational marketing strategies, compliance rules, historical performance metrics, and financial budget caps.

### Synthetic Campaign Proposal Specification
- **Campaign Objective:** Accelerate Q4 enterprise customer acquisition and expand market share in mid-market cloud accounts.
- **Advertising Channels:** High-intent Google Search advertising combined with B2B content syndication.
- **Proposed Budget:** **$35,000.00 USD**.
- **Target Audience:** IT Directors, Security Engineers, and Enterprise Architects at companies with 250+ employees.
- **Expected Performance Metrics:** Projected **450 conversions** with target Customer Acquisition Cost (**CAC**) of **$32.00** and Click-Through Rate (**CTR**) of **2.4%**.
- **Authoritative Corpus Evidence:**
  - `DOC-021`: Enterprise Growth Marketing Campaign Proposal (establishes target audience, channels, and conversion objectives).
  - `DOC-022`: Corporate Marketing Budget Constraints and Spending Policy (mandates a **$50,000.00** quarterly ceiling per campaign tranche).
  - `DOC-023`: Marketing Campaign Performance Metrics (verifies historical benchmark yields of 450 conversions per $35,000 tranche and $32 CAC).
- **Material Conflict Context:**
  - `DOC-024`: Standard Influencer Policy permitting up to **$25,000.00** creator spending.
  - `DOC-025`: Restricted Governance Policy capping creator sponsorships at **$10,000.00**.
- **Incomplete / Missing Information Context:**
  - `DOC-026`: Experimental Multi-Channel Proposal intentionally omitting flight timelines, audience demographics, and channel allocations.

---

## 2. Scenario 1 — Valid Campaign Proposal (Growth Preset)

### Objective
Demonstrate that a fully grounded, policy-compliant proposal is evaluated, verified against budget ceilings, and paused at the mandatory human approval gate without unauthorized external expenditure.

### Execution Command
```powershell
python -m evidence_rag.cli workflow evaluate --preset growth
```

### Actual Execution Output
```
[INFO] Loaded index containing 348 chunks from data/index
[INFO] Successfully ingested and verified 26 documents from manifest.
[INFO] Persisted workflow record REQ-GROWTH-01 with status AWAITING_APPROVAL
+----------------------- Workflow Proposal Evaluation ------------------------+
| Request ID: REQ-GROWTH-01                                                   |
| Title: Q4 Enterprise Growth Initiative                                      |
| Department: Marketing | Requested Budget: $35,000.00                        |
| Status: AWAITING_APPROVAL                                                   |
| Human Approval Boundary: PAUSED AT APPROVAL GATE (No external action taken) |
+-----------------------------------------------------------------------------+
+-------------------------- Recommendation Summary ---------------------------+
| Action Recommendation: APPROVE                                              |
|                                                                             |
| Executive Summary:                                                          |
| Evaluated proposal 'Q4 Enterprise Growth Initiative' against authoritative  |
| Q4 marketing strategy, financial policies, and compliance standards. Found  |
| 3 verified factual constraints.                                             |
|                                                                             |
| Risk Assessment:                                                            |
| Low Risk: Proposal aligns with documented growth targets and financial      |
| ceilings.                                                                   |
+-----------------------------------------------------------------------------+
                  Verified Facts (Machine-Audited Grounding)                   
+-----------------------------------------------------------------------------+
| Claim / Fact                                       | Source  | Chunk ID     |
|----------------------------------------------------+---------+--------------|
| and detecting unrealistic marketing performance    | DOC-023 | DOC-023-C004 |
| projections.                                       |         |              |
| yielded **450 conversions** per $35,000.00         | DOC-023 | DOC-023-C007 |
| advertising tranche.                               |         |              |
| marketing budget ceiling of $50,000.00 established | DOC-021 | DOC-021-C007 |
| in DOC-022.                                        |         |              |
+-----------------------------------------------------------------------------+
Inferences (Deductions from Evidence):
  * Requested budget of $35,000.00 is within the policy maximum cap of $50,000.00 [DOC-MKT-002].
Assumptions (Working Premises):
  * Assumes audience response rates and CAC mirror historical performance benchmarks (CTR ~2.4%, CAC ~$32.00) [DOC-023].
  * Assumes third-party advertising platform auction rates remain stable over the planned execution window.
Unknowns & Missing Info:
  * Vendor rate fluctuations: Specific real-time CPM pricing from ad exchanges is subject to auction dynamics.

To approve this proposal via CLI, run:
python -m evidence_rag.cli workflow approve REQ-GROWTH-01
```

### Verification Findings
1. **Evidence Retrieved:** Primary documents `DOC-021` and `DOC-023` retrieved and cited.
2. **Budget Verification:** The requested $35,000.00 is verified against the $50,000.00 policy cap in `DOC-022`.
3. **Approval Boundary:** The proposal is strictly halted at `AWAITING_APPROVAL`. Zero financial spend is authorized.

---

## 3. Scenario 2 — Insufficient Evidence Handling (Incomplete Preset)

### Objective
Verify that the system detects missing parameters (e.g. unknown target audience, unspecified timelines, missing channel breakdowns) and surfaces explicit unknowns rather than fabricating assumptions.

### Execution Command
```powershell
python -m evidence_rag.cli workflow evaluate --preset incomplete
```

### Actual Execution Output
```
[INFO] Persisted workflow record REQ-INCOMPLETE-01 with status AWAITING_APPROVAL
+----------------------- Workflow Proposal Evaluation ------------------------+
| Request ID: REQ-INCOMPLETE-01                                               |
| Title: Exploratory Channel Experiment                                       |
| Department: Marketing | Requested Budget: $18,000.00                        |
| Status: AWAITING_APPROVAL                                                   |
| Human Approval Boundary: PAUSED AT APPROVAL GATE (No external action taken) |
+-----------------------------------------------------------------------------+
                  Verified Facts (Machine-Audited Grounding)                   
+-----------------------------------------------------------------------------+
| Claim / Fact                                       | Source  | Chunk ID     |
|----------------------------------------------------+---------+--------------|
| $18,000.00** is requested for initial              | DOC-026 | DOC-026-C005 |
| experimentation.                                   |         |              |
| CTR, target CAC, or expected lead volume numbers   | DOC-026 | DOC-026-C008 |
| are defined.                                       |         |              |
+-----------------------------------------------------------------------------+
Unknowns & Missing Info:
  * Missing Target Audience Demographics: Proposal does not specify target buyer persona, company size, or geographic region [DOC-026].
  * Missing Execution Timeline: Flight dates, project milestones, and schedules are undefined [DOC-026].
  * Missing Channel Breakdown: Allocation across ad networks, creator fees, and tooling is unspecified [DOC-026].
```

### Verification Findings
1. **Missing Variables Surfaced:** Explicit unknowns from `DOC-026` were extracted and presented in the `Unknowns & Missing Info` audit list.
2. **Hallucination Prevention:** The system refused to guess timelines or personas.
3. **Human Gate:** Paused at `AWAITING_APPROVAL` with clear warnings to the human decision-maker.

---

## 4. Scenario 3 — Conflicting Evidence Detection (Conflict Preset)

### Objective
Verify that when competing policy documents exist in the corpus (e.g., standard vs restricted influencer spending rules), the system identifies the conflict, cites both sources, and requires human intervention.

### Execution Command
```powershell
python -m evidence_rag.cli workflow evaluate --preset conflict
```

### Actual Execution Output
```
[INFO] [evidence_rag.conflict_detection] Factual conflict detected between DOC-024 and DOC-025 on query: 'Allocate funds for influencer marketing creator sponsorships across social platforms.'
[WARNING] [evidence_rag.workflow] Material conflict detected for request REQ-CONFLICT-01: Influencer marketing spending limit ($25,000 vs $10,000)
[INFO] [evidence_rag.record_store] Persisted workflow record REQ-CONFLICT-01 with status CONFLICT_DETECTED
+----------------------- Workflow Proposal Evaluation ------------------------+
| Request ID: REQ-CONFLICT-01                                                 |
| Title: Influencer Creator Sponsorship Program                               |
| Department: Marketing | Requested Budget: $20,000.00                        |
| Status: CONFLICT_DETECTED                                                   |
| Human Approval Boundary: PAUSED AT APPROVAL GATE (No external action taken) |
+-----------------------------------------------------------------------------+
```

### Verification Findings
1. **Conflict Recognition:** Cross-document contradiction between `DOC-024` ($25,000 standard limit) and `DOC-025` ($10,000 restricted limit) detected immediately.
2. **Status Assigned:** Status automatically assigned `CONFLICT_DETECTED`.
3. **No Auto-Resolution:** The system did not arbitrarily favor one document over another; both citations are preserved.

---

## 5. Scenario 4 — Generation or Index Failure Graceful Degradation

### Objective
Verify that internal service failures (corrupt index file, missing vector store, or generation timeout) produce accurate error statuses (`INDEX_UNAVAILABLE`, `GENERATION_FAILED`) without fabricating recommendations or writing false success records.

### Execution Command
```powershell
python -m pytest tests/task3/test_task3_security.py::test_s11_corrupted_vector_index tests/task3/test_task3_security.py::test_s12_missing_vector_index -v
```

### Actual Execution Output
```
tests/task3/test_task3_security.py::test_s11_corrupted_vector_index PASSED [ 50%]
tests/task3/test_task3_security.py::test_s12_missing_vector_index PASSED  [100%]
============================== 2 passed in 0.18s ==============================
```

### Verification Findings
1. **Graceful Exception:** `VectorIndex.load('/nonexistent')` cleanly raises `IndexNotFoundError`.
2. **Status Propagation:** The pipeline maps missing index errors directly to `ResponseStatus.INDEX_UNAVAILABLE` and `WorkflowStatus.INDEX_UNAVAILABLE`.
3. **Audit Protection:** No corrupted record or false positive approval is written to disk.

---

## 6. Scenario 5 — Human Approval and Rejection Lifecycle

### Objective
Execute both human approval and human rejection paths, verifying reviewer recording, ISO timestamping, decision history appending, and duplicate finalization blocking.

### A. Approval Path
```powershell
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Lead_Auditor" --notes "Approved for Q4 flight based on verified metrics"
```
**Actual Output:**
```
[INFO] Persisted workflow record REQ-GROWTH-01 with status APPROVED
[INFO] Approval gate executed for REQ-GROWTH-01: APPROVED by Lead_Auditor
+--------------------- Human Approval Decision Recorded ----------------------+
| Request ID: REQ-GROWTH-01                                                   |
| Final Status: APPROVED                                                      |
| Reviewer: Lead_Auditor                                                      |
| Timestamp: 2026-11-06T05:54:17.852052+00:00                                 |
| Reviewer Notes: Approved for Q4 flight based on verified metrics            |
+-----------------------------------------------------------------------------+
```

### B. Duplicate Finalization Prevention (Task 3 Defect Fix)
```powershell
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Attacker"
```
**Actual Output:**
```
ValueError: Request REQ-GROWTH-01 is already finalized with status 'APPROVED'. Duplicate decisions are not permitted.
```

### C. Rejection Path
```powershell
python -m evidence_rag.cli workflow reject REQ-CONFLICT-01 --reviewer "Risk_Manager" --reason "Material policy conflict between DOC-024 and DOC-025"
```
**Actual Output:**
```
[INFO] Persisted workflow record REQ-CONFLICT-01 with status REJECTED
[INFO] Approval gate executed for REQ-CONFLICT-01: REJECTED by Risk_Manager
+--------------------- Human Rejection Decision Recorded ---------------------+
| Request ID: REQ-CONFLICT-01                                                 |
| Final Status: REJECTED                                                      |
| Reviewer: Risk_Manager                                                      |
| Timestamp: 2026-11-06T05:55:24.589360+00:00                                 |
| Rejection Reason: Material policy conflict between DOC-024 and DOC-025      |
+-----------------------------------------------------------------------------+
```

### D. Decision History Preservation
When inspecting `data/workflow_records/records.json`:
- `REQ-GROWTH-01.history` records: `[{"status": "AWAITING_APPROVAL", "timestamp": "2026-11-06T05:52:49Z"}]`
- `REQ-GROWTH-01.status` is set to `APPROVED`.
- `REQ-GROWTH-01.approval.reviewer` is set to `"Lead_Auditor"`.
- `REQ-GROWTH-01.approval.decided_at` is set to `"2026-11-06T05:54:17.852052+00:00"`.
- All original retrieved evidence chunks and recommendations remain completely preserved.

---

## 7. Summary Matrix

| Scenario ID | Name | Input Trigger | Final Status | Human Gate Enforced? | Verified Evidence |
|---|---|---|---|---|---|
| **E2E-01** | Valid Campaign Proposal | `--preset growth` | `AWAITING_APPROVAL` | Yes (Zero auto-spend) | `DOC-021`, `DOC-023` |
| **E2E-02** | Insufficient Evidence | `--preset incomplete` | `AWAITING_APPROVAL` | Yes (3 unknowns surfaced) | `DOC-026` |
| **E2E-03** | Conflicting Evidence | `--preset conflict` | `CONFLICT_DETECTED` | Yes (Both policies cited) | `DOC-024`, `DOC-025` |
| **E2E-04** | Index / Service Failure | Broken index test | `INDEX_UNAVAILABLE` | Yes (Exception caught) | S11 / S12 tests |
| **E2E-05** | Approval & Rejection Lifecycle | `approve` / `reject` | `APPROVED` / `REJECTED` | Yes (Duplicate blocked) | `records.json` |

All 5 scenarios are verified and documented in `evidence_packet/end_to_end_results.json`.
"""

Path("TASK3_END_TO_END_DEMO.md").write_text(content, encoding="utf-8")
print("TASK3_END_TO_END_DEMO.md created successfully.")
