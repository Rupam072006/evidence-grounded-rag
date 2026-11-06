# TASK3_REPLAY_REPORT.md
## AegisCore — Deterministic Replay Verification Report
**Date:** 2026-11-05  
**Evidence:** `evidence_packet/replay_comparison.json`

---

## 1. What Replay Provides

| Capability | Supported | Notes |
|---|---|---|
| Reconstruct what was recorded | ✓ YES | RecordStore.get_record() retrieves full audit record |
| Re-execute with same input | ✓ YES | DecisionWorkflow.evaluate_proposal() re-runs with original WorkflowRequest |
| Compare original and replay status | ✓ YES | workflow replay CLI command |
| Verify evidence document IDs match | ✓ YES | evidence_set.chunk.document_id comparison |
| Prove approval was legitimate | ✗ NO | Cannot verify reviewer was authorized (see Section 3) |
| Guarantee identical LLM output | ✗ NO | Mock generator is deterministic; online LLMs may vary |

---

## 2. CLI Replay Command (Task 3 New Feature)

```powershell
# Replay and compare a past proposal
python -m evidence_rag.cli workflow replay REQ-GROWTH-01

# Replay with JSON output for audit
python -m evidence_rag.cli workflow replay REQ-GROWTH-01 --json-out
```

**Output includes:**
- Original status vs. replay status
- Original retrieved document IDs vs. replay document IDs  
- Original recommended action vs. replay recommended action
- Original approval record (reviewer, timestamp, decision)
- Replay limitations disclaimer

---

## 3. Replay Test Results

| Test | Scenario | Result |
|---|---|---|
| test_replay_record_retrievable | Record retrieved from store | ✓ PASS |
| test_replay_original_evidence_preserved | Evidence set preserved in record | ✓ PASS |
| test_replay_recommendation_preserved | Recommendation preserved in record | ✓ PASS |
| test_replay_approval_decision_preserved | Approval metadata preserved | ✓ PASS |
| test_replay_does_not_prove_approval_legitimacy | Reviewer is text string only | ✓ PASS |
| test_replay_history_audit_trail_preserved | History list preserved | ✓ PASS |
| test_replay_roundtrip_serialization | JSON round-trip preserves data | ✓ PASS |

**Result: 7/7 PASSED**

---

## 4. Important Distinctions

### Reconstruction
Recovering what was recorded in the audit store. **This is supported** — `workflow show <request_id>` and `workflow replay <request_id>` both reconstruct the original record.

### Reproduction  
Re-executing the same request under current conditions. **This is supported** — `workflow replay` calls `evaluate_proposal()` with the original `WorkflowRequest` and compares results.

### Approval Legitimacy
Proving the original approval was submitted by an authorized human. **This is NOT supported** without an identity provider. The reviewer name is recorded text — it cannot be cryptographically verified retroactively.

---

## 5. What Can Differ Between Replay and Original

| Factor | Can Differ? | Reason |
|---|---|---|
| Mock generator output | No (deterministic) | Fixed extraction algorithm |
| Online LLM output | Yes | Model updates, temperature, API changes |
| Retrieved document IDs | No (same corpus) | Same TF-IDF index |
| Retrieved document IDs | Yes (if corpus changed) | Adding/removing documents changes index |
| Workflow status | Usually No | Depends on retrieval + generation |
| Approval record | Preserved exactly | Stored as-is in RecordStore |

---

## 6. Replay Limitations

> [!WARNING]
> Replay does not independently prove approval legitimacy. A manually entered reviewer name is recorded identity, not independently authenticated identity.

The following limitations apply and are explicitly documented:

1. **No identity verification:** Reviewer name is a text field.
2. **No external audit storage:** Records are local JSON — not immutable blockchain or external trusted store.
3. **LLM variability:** Online providers may produce different outputs across replays.
4. **Corpus dependency:** Replay accuracy depends on corpus being unchanged since original request.
5. **No digital signatures:** Records are not cryptographically signed with a protected key.

