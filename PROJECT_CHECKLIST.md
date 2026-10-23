# Task 2 Placement Assessment — Project Checklist

**Candidate:** Rupam Patne (BE Computer Engineering - AI & ML)  
**Project:** Evidence-Grounded Decision-Support Workflow (`evidence-grounded-rag`)  
**Repository:** `https://github.com/Rupam072006/evidence-grounded-rag`  

---

## 4-Day Execution Milestones

### [x] DAY 1 — AUDIT TASK 1 AND CORRECT VERIFIED DEFECTS
- [x] Documented setup verified in a clean virtual environment (`.venv_audit`).
- [x] Full test suite executed with real output recorded (47 passed).
- [x] Citations verified for genuine content support (not just chunk ID existence).
- [x] Boundary scenarios tested: unknown question, conflict detection, invalid input, prompt injection, invalid API key.
- [x] Conflict detection verified to return explicit `CONFLICT_DETECTED` status (not ordinary answer).
- [x] Corpus fingerprinting verified across full corpus; stale index detection verified on document modification.
- [x] Confirmed defects reproduced, recorded in defect register, corrected, and covered by regression tests.
- [x] Deliverables produced: `TASK2_BASELINE.md`, `evidence_packet/audit_raw_output.json`, `evidence_packet/defect_register.md`.
- [x] Committed and pushed to GitHub (`ab16a4c`).

### [x] DAY 2 — BUILD THE END-TO-END WORKFLOW
- [x] Reused existing RAG components (ingestion, chunking, embeddings, indexing, retrieval, conflict detection, context builder).
- [x] Structured request model (`WorkflowRequest`) with mandatory `request_id`, `title`, and `proposal_text`.
- [x] Input validation safely rejecting malformed requests with `INVALID_REQUEST`.
- [x] Source provenance preserved across all retrieved passages.
- [x] Evidence set built with source IDs, chunk IDs, rankings, and relevance scores.
- [x] Insufficient evidence detected and returned with `INSUFFICIENT_EVIDENCE`.
- [x] Material conflicts detected and returned with `CONFLICT_DETECTED`.
- [x] Citations verified against retrieved chunks with strict formatting support (`[...]` and `【...】`).
- [x] Recommendation report cleanly separating:
  - Verified Facts
  - Inferences
  - Assumptions
  - Unknowns
- [x] Sources cited for every material factual claim.
- [x] Structured JSON result with consistent statuses (`AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, `INSUFFICIENT_EVIDENCE`, `CONFLICT_DETECTED`, `INVALID_REQUEST`, `INDEX_UNAVAILABLE`).
- [x] **Mandatory Human Approval Gate enforced**: System stops before any consequential action; zero autonomous external action.
- [x] Persistent local record store (`RecordStore`) tracking request, evidence, recommendation, decision, and history without exposing secrets.
- [x] Realistic synthetic marketing campaign corpus (`data/marketing_corpus/`) with controlled budget ceilings, benchmarks, missing-info cases, and intentional influencer spend conflict.
- [x] Comprehensive automated workflow test suite (`tests/functional/test_workflow.py`): 8 tests passing, total suite 55 passing tests.
- [x] Documentation updated: `CHANGELOG.md`, `INTEGRATION.md`, `PROJECT_CHECKLIST.md`.

### [x] DAY 3 — INTEGRATION AND FAILURE TESTING
- [x] Documented CLI commands implemented (`workflow evaluate`, `workflow approve`, `workflow show`, `workflow list`) in `src/evidence_rag/cli.py`.
- [x] Matrix of 10 failure and integration scenarios automated and tested:
  - [x] Scenario 1: Valid request with sufficient evidence (`AWAITING_APPROVAL`)
  - [x] Scenario 2: Request with no adequate evidence (`INSUFFICIENT_EVIDENCE`)
  - [x] Scenario 3: Conflicting source documents (`CONFLICT_DETECTED`)
  - [x] Scenario 4: Malformed request or missing required fields (`INVALID_REQUEST`)
  - [x] Scenario 5: Prompt-injection attempt inside input (prompt takeover prevented, non-approved)
  - [x] Scenario 6: Unsupported factual claim or invalid citation (bad citations caught and rejected)
  - [x] Scenario 7: Empty corpus or unavailable index (`INDEX_UNAVAILABLE` handled gracefully)
  - [x] Scenario 8: Generation service offline / safe fallback (deterministic evidence synthesis)
  - [x] Scenario 9: Corpus update followed by retrieval (automatic index refresh on content modification)
  - [x] Scenario 10: Human approval boundary enforced (halts at gate; requires explicit reviewer action)
- [x] Dedicated test suite implemented: `tests/functional/test_day3_scenarios.py` (10/10 passed).
- [x] Total test suite passes: 65/65 tests passed in 0.63s.
- [x] Real execution artifacts generated: `evidence_packet/day3_scenario_matrix.md` and `evidence_packet/day3_raw_output.json`.

### [x] DAY 4 — REPRODUCIBILITY, EVALUATION AND HANDOVER
- [x] Clean environment reproduction tested and verified (`.venv_audit`).
- [x] 25-question evaluation benchmark executed (`evaluation/questions.jsonl`):
  - 100.0% Retrieval Success Rate (19/19 applicable queries)
  - 88.0% Status Accuracy (22/25 exact status matches)
  - 100.0% Failure Detection Rate (8/8 negative cases correctly flagged)
  - 100.0% Citation Validity Rate (28/28 citations verified against source text)
  - Real results saved to `evaluation/results/evaluation_run_20261023_133650.json`.
- [x] Comprehensive evaluation documentation: `EVALUATION.md`.
- [x] Reviewer Packet and Code Packet completed: `REVIEW_PACKET.md` and `evidence_packet/code_packet.md`.
- [x] Architecture specification updated with Decision Workflow & Human Gate: `ARCHITECTURE.md`.
- [x] Full automated test suite passes: 65/65 passed in 0.72s.
- [x] Final git tag and submission prepared.

---

## Mandatory Acceptance Conditions

| Acceptance Condition | Current Status | Verification Evidence |
|---|---|---|
| **Schema & Status Match** | Verified | Statuses reflect exact execution path (`AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, etc.) |
| **Corpus Change Detection** | Verified | Fingerprint covers full corpus; stale index detection active |
| **Evidence Grounding** | Verified | Citations verified against retrieved passages; support both ASCII and unicode brackets |
| **Unknown Handling** | Verified | Explicit `INSUFFICIENT_EVIDENCE` status, zero fabricated facts |
| **Conflict Handling** | Verified | Contradictions surfaced with `CONFLICT_DETECTED` and conflicting sources |
| **Security & Secrets** | Verified | Automated secret scrubber in `RecordStore`; prompt injection rejected |
| **Approval Boundary** | Verified | System halts at gate; human decision required for `APPROVED`/`REJECTED` |
| **Task 1 Compatibility** | Verified | All 47 original Task 1 tests continue passing without regression |
