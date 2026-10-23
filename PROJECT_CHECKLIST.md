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

### [ ] DAY 3 — INTEGRATION AND FAILURE TESTING
- [ ] Documented CLI and local API exposure for the decision workflow.
- [ ] Matrix of 10 failure and edge-case scenarios tested with real outputs.
- [ ] Regression test verification for all scenarios.

### [ ] DAY 4 — REPRODUCIBILITY, EVALUATION AND HANDOVER
- [ ] Clean environment reproduction.
- [ ] 25-question evaluation benchmark with metrics.
- [ ] Handover and Reviewer Packets completed.
- [ ] Final tag and submission.

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
