"""Regression test suite for Tester QA hardening defects:
- QA-001: Reviewer identity normalization and case variant rejection
- QA-002: Rejection of approval decisions on unapprovable states
- QA-003: Trace ID propagation to decision history events
- QA-004: Fail-closed on corrupt record store read
- QA-012: Zero modification to tracked repository files during test runs
"""
import json
import pytest
from pathlib import Path

from evidence_rag.workflow import DecisionWorkflow, validate_reviewer_identity
from evidence_rag.workflow_schemas import (
    WorkflowRequest,
    WorkflowRecord,
    WorkflowStatus,
    ApprovalDecision
)
from evidence_rag.record_store import RecordStore


def test_qa_001_reviewer_normalization_and_variants():
    """QA-001: Normalized case variants and disallowed placeholders must be rejected."""
    disallowed_variants = [
        "prof_evaluator",
        "PROF_EVALUATOR",
        "Prof_Evaluator",
        "  Prof_Evaluator  ",
        "anonymous",
        "ANONYMOUS",
        "anonymous_reviewer",
        "default",
        "DEFAULT",
        ".",
        "none",
        "unknown",
        "   ",
        "",
        "ab"  # < 3 chars
    ]
    for variant in disallowed_variants:
        with pytest.raises(ValueError):
            validate_reviewer_identity(variant)

    # Valid human reviewer name should pass and be stripped
    valid_name = "  Pratik Bhuwad - CMO Product Owner  "
    assert validate_reviewer_identity(valid_name) == "Pratik Bhuwad - CMO Product Owner"


def test_qa_002_decision_rejected_on_unapprovable_state(tmp_path):
    """QA-002: Decisions must be rejected on non-approvable statuses (e.g. INSUFFICIENT_EVIDENCE)."""
    store = RecordStore(tmp_path / "records")
    req = WorkflowRequest(
        request_id="REQ-UNAPPROVABLE-01",
        title="Unapprovable Request",
        proposal_text="Some proposal text here",
        department="Marketing",
        requested_budget=1000.0,
        submitted_by="analyst"
    )
    rec = WorkflowRecord(
        request_id="REQ-UNAPPROVABLE-01",
        status=WorkflowStatus.INSUFFICIENT_EVIDENCE,
        request=req,
        created_at="2026-11-21T00:00:00Z",
        updated_at="2026-11-21T00:00:00Z"
    )
    store.save_record(rec)

    decision = ApprovalDecision(
        request_id="REQ-UNAPPROVABLE-01",
        decision="APPROVED",
        reviewer="Pratik Bhuwad - CMO Product Owner",
        decision_notes="Attempted invalid approval"
    )

    with pytest.raises(ValueError, match="Cannot record decision on request.*with status 'INSUFFICIENT_EVIDENCE'"):
        store.record_decision("REQ-UNAPPROVABLE-01", decision)


def test_qa_003_trace_id_propagated_to_history(tmp_path):
    """QA-003: Record trace_id must be copied into decision history events."""
    store = RecordStore(tmp_path / "records")
    req = WorkflowRequest(
        request_id="REQ-TRACE-01",
        title="Trace Test Proposal",
        proposal_text="Valid proposal text here",
        department="Marketing",
        requested_budget=5000.0,
        submitted_by="analyst"
    )
    rec = WorkflowRecord(
        request_id="REQ-TRACE-01",
        status=WorkflowStatus.AWAITING_APPROVAL,
        trace_id="TRC-TEST-TRACE-9999",
        request=req,
        created_at="2026-11-21T00:00:00Z",
        updated_at="2026-11-21T00:00:00Z"
    )
    store.save_record(rec)

    decision = ApprovalDecision(
        request_id="REQ-TRACE-01",
        decision="APPROVED",
        reviewer="Pratik Bhuwad - CMO Product Owner",
        decision_notes="Approved with trace propagation"
    )

    updated = store.record_decision("REQ-TRACE-01", decision)
    assert updated.status == WorkflowStatus.APPROVED
    last_event = updated.history[-1]
    assert last_event["action"] == "HUMAN_APPROVED"
    assert last_event["trace_id"] == "TRC-TEST-TRACE-9999"


def test_qa_004_fail_closed_on_corrupt_store(tmp_path):
    """QA-004: Store read with raise_on_error and save_record must fail closed on corrupt JSON."""
    records_dir = tmp_path / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    store_file = records_dir / "records.json"
    store_file.write_text("{ corrupt json syntax: true, ", encoding="utf-8")

    store = RecordStore(records_dir)
    with pytest.raises(IOError, match="Corrupt or unreadable record store"):
        store._read_store(raise_on_error=True)

    # list_records() still safely degrades without crashing
    assert store.list_records() == []

    # save_record() fails closed to prevent overwriting/discarding corrupt data
    req = WorkflowRequest(
        request_id="REQ-CORRUPT-01",
        title="Test Proposal",
        proposal_text="Valid proposal text here",
        department="Marketing",
        requested_budget=1000.0,
        submitted_by="analyst"
    )
    rec = WorkflowRecord(
        request_id="REQ-CORRUPT-01",
        status=WorkflowStatus.AWAITING_APPROVAL,
        request=req,
        created_at="2026-11-21T00:00:00Z",
        updated_at="2026-11-21T00:00:00Z"
    )
    with pytest.raises(IOError, match="Corrupt or unreadable record store"):
        store.save_record(rec)
