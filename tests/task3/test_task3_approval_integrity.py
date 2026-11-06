"""Task 3 — Approval Integrity Tests.

Tests all approval workflow scenarios including:
- Empty reviewer validation
- Invalid decisions
- Nonexistent request IDs
- Duplicate approval prevention
- Decision after finalization
- State transition validation
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from evidence_rag.record_store import RecordStore
from evidence_rag.workflow_schemas import (
    WorkflowRecord, WorkflowRequest, WorkflowStatus, ApprovalDecision
)


def _make_record(request_id: str, status: WorkflowStatus = WorkflowStatus.AWAITING_APPROVAL) -> WorkflowRecord:
    """Build a minimal WorkflowRecord for testing."""
    now = datetime.now(timezone.utc).isoformat()
    req = WorkflowRequest(
        request_id=request_id,
        title="Test Proposal",
        proposal_text="Allocate $20,000 for digital advertising.",
        department="Marketing",
        requested_budget=20000.0,
        submitted_by="test_analyst"
    )
    return WorkflowRecord(
        request_id=request_id,
        status=status,
        request=req,
        created_at=now,
        updated_at=now
    )


def _make_decision(request_id: str, decision: str = "APPROVED", reviewer: str = "Prof_Evaluator") -> ApprovalDecision:
    return ApprovalDecision(
        request_id=request_id,
        decision=decision,
        reviewer=reviewer,
        decision_notes="Reviewed and approved."
    )


@pytest.fixture
def temp_store():
    """RecordStore backed by a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield RecordStore(storage_dir=Path(tmpdir))


# --- Test: Empty reviewer name rejected ---
def test_empty_reviewer_rejected(temp_store):
    """Task 3 AI-02: Empty reviewer name must be rejected."""
    record = _make_record("REQ-T3-001")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-001", reviewer="")
    with pytest.raises(ValueError, match="Reviewer name cannot be empty"):
        temp_store.record_decision("REQ-T3-001", decision)


def test_whitespace_reviewer_rejected(temp_store):
    """Task 3 AI-03: Whitespace-only reviewer name must be rejected."""
    record = _make_record("REQ-T3-002")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-002", reviewer="   ")
    with pytest.raises(ValueError, match="Reviewer name cannot be empty"):
        temp_store.record_decision("REQ-T3-002", decision)


# --- Test: Valid decision recorded ---
def test_valid_approval_recorded(temp_store):
    """Task 3 AI-01: Valid approval with non-empty reviewer is accepted."""
    record = _make_record("REQ-T3-003")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-003", decision="APPROVED", reviewer="Prof_Evaluator")
    result = temp_store.record_decision("REQ-T3-003", decision)
    assert result is not None
    assert result.status == WorkflowStatus.APPROVED
    assert result.approval.reviewer == "Prof_Evaluator"


def test_valid_rejection_recorded(temp_store):
    """Task 3 AI-01b: Valid rejection with non-empty reviewer is accepted."""
    record = _make_record("REQ-T3-004")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-004", decision="REJECTED", reviewer="Prof_Evaluator")
    result = temp_store.record_decision("REQ-T3-004", decision)
    assert result is not None
    assert result.status == WorkflowStatus.REJECTED


# --- Test: Nonexistent request ID ---
def test_nonexistent_request_id_returns_none(temp_store):
    """Task 3 AI-04: Approving a nonexistent request ID returns None."""
    decision = _make_decision("REQ-DOES-NOT-EXIST")
    result = temp_store.record_decision("REQ-DOES-NOT-EXIST", decision)
    assert result is None


# --- Test: Duplicate approval prevented ---
def test_duplicate_approval_prevented(temp_store):
    """Task 3 AI-05: A second approval on an already-APPROVED record raises ValueError."""
    record = _make_record("REQ-T3-005")
    temp_store.save_record(record)

    decision1 = _make_decision("REQ-T3-005", decision="APPROVED", reviewer="Prof_Evaluator")
    temp_store.record_decision("REQ-T3-005", decision1)

    decision2 = _make_decision("REQ-T3-005", decision="APPROVED", reviewer="Another_Reviewer")
    with pytest.raises(ValueError, match="already finalized"):
        temp_store.record_decision("REQ-T3-005", decision2)


def test_duplicate_rejection_prevented(temp_store):
    """Task 3 AI-06: A second rejection on an already-REJECTED record raises ValueError."""
    record = _make_record("REQ-T3-006")
    temp_store.save_record(record)

    decision1 = _make_decision("REQ-T3-006", decision="REJECTED", reviewer="Prof_Evaluator")
    temp_store.record_decision("REQ-T3-006", decision1)

    decision2 = _make_decision("REQ-T3-006", decision="REJECTED", reviewer="Another_Reviewer")
    with pytest.raises(ValueError, match="already finalized"):
        temp_store.record_decision("REQ-T3-006", decision2)


def test_approval_after_rejection_prevented(temp_store):
    """Task 3 AI-07: Cannot approve a request that is already REJECTED."""
    record = _make_record("REQ-T3-007")
    temp_store.save_record(record)

    rejection = _make_decision("REQ-T3-007", decision="REJECTED", reviewer="Prof_Evaluator")
    temp_store.record_decision("REQ-T3-007", rejection)

    approval = _make_decision("REQ-T3-007", decision="APPROVED", reviewer="Override_Attempt")
    with pytest.raises(ValueError, match="already finalized"):
        temp_store.record_decision("REQ-T3-007", approval)


# --- Test: Decision history is preserved ---
def test_decision_recorded_in_history(temp_store):
    """Task 3 AI-08: Approval decision is appended to record history."""
    record = _make_record("REQ-T3-008")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-008", decision="APPROVED", reviewer="Prof_Evaluator")
    result = temp_store.record_decision("REQ-T3-008", decision)
    assert len(result.history) >= 1
    last = result.history[-1]
    assert last["reviewer"] == "Prof_Evaluator"
    assert "APPROVED" in last["action"]


# --- Test: Decision timestamp is recorded ---
def test_approval_timestamp_stored(temp_store):
    """Task 3 AI-09: Approval timestamp is an ISO 8601 string."""
    record = _make_record("REQ-T3-009")
    temp_store.save_record(record)
    decision = _make_decision("REQ-T3-009", decision="APPROVED", reviewer="Prof_Evaluator")
    result = temp_store.record_decision("REQ-T3-009", decision)
    # Verify timestamp is parseable ISO 8601
    ts = result.approval.decided_at
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert parsed is not None


# --- Test: Approval metadata is complete ---
def test_approval_metadata_complete(temp_store):
    """Task 3 AI-10: Approval record contains all required metadata fields."""
    record = _make_record("REQ-T3-010")
    temp_store.save_record(record)
    decision = ApprovalDecision(
        request_id="REQ-T3-010",
        decision="APPROVED",
        reviewer="Prof_Evaluator",
        decision_notes="Verified against DOC-022 budget policy."
    )
    result = temp_store.record_decision("REQ-T3-010", decision)
    assert result.approval.request_id == "REQ-T3-010"
    assert result.approval.decision == "APPROVED"
    assert result.approval.reviewer == "Prof_Evaluator"
    assert result.approval.decision_notes != ""
    assert result.approval.decided_at != ""


# --- Test: Record store handles corrupt JSON ---
def test_corrupt_json_does_not_crash_read(temp_store):
    """Task 3 RI-03: Corrupted JSON in record store returns empty dict (graceful degradation)."""
    # Write corrupt JSON
    temp_store.store_file.write_text("{corrupt: json")
    # Should not raise — returns empty
    result = temp_store.list_records()
    assert isinstance(result, list)

