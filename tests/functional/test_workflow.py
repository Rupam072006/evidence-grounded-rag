"""Functional tests for DecisionWorkflow engine and human approval gate."""
import pytest
from pathlib import Path
from datetime import datetime, timezone

from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import (
    WorkflowRequest,
    WorkflowStatus,
    ApprovalDecision,
    WorkflowRecord
)
from evidence_rag.record_store import RecordStore


@pytest.fixture
def workflow_instance(tmp_path):
    """Create an isolated DecisionWorkflow instance backed by a temporary record store."""
    record_store = RecordStore(tmp_path / "records")
    wf = DecisionWorkflow(record_store=record_store)
    wf.ensure_index()
    return wf


def test_workflow_valid_proposal_reaches_approval_gate(workflow_instance):
    """Verify that a compliant proposal generates recommendation and stops at approval gate."""
    req = WorkflowRequest(
        request_id="TEST-REQ-001",
        title="Q4 Enterprise Lead Generation via LinkedIn",
        proposal_text="Deploy targeted sponsored content on LinkedIn targeting technical decision makers, aiming for a 25 percent increase in SQLs with a budget of $30,000.",
        department="Marketing",
        requested_budget=30000.0,
        submitted_by="growth_lead"
    )

    record = workflow_instance.evaluate_proposal(req)

    # 1. Verification of status
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.approval is None  # Human approval gate enforced: NOT auto-approved

    # 2. Verification of recommendation report structure
    rep = record.recommendation
    assert rep is not None
    assert len(rep.verified_facts) > 0
    assert len(rep.inferences) > 0
    assert len(rep.assumptions) > 0
    assert len(rep.unknowns) > 0
    assert rep.recommended_action in ("APPROVE", "APPROVE_WITH_CONDITIONS")

    # 3. Verification of citations
    assert len(record.citations) > 0
    for cit in record.citations:
        assert cit.is_valid is True
        assert cit.document_id.startswith("DOC-MKT-")


def test_workflow_human_approval_gate_transition(workflow_instance):
    """Verify that only explicit human action transitions record to APPROVED or REJECTED."""
    req = WorkflowRequest(
        request_id="TEST-REQ-002",
        title="Compliant Pilot Campaign",
        proposal_text="Pilot enterprise search ads on Google Ads adhering to Q4 objectives and budget caps.",
        requested_budget=15000.0
    )

    record = workflow_instance.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL

    # Execute approval at the gate
    approved_record = workflow_instance.submit_approval(
        request_id="TEST-REQ-002",
        decision="APPROVED",
        reviewer="Rupam Patne",
        notes="Budget confirmed; aligns with search caps."
    )

    assert approved_record.status == WorkflowStatus.APPROVED
    assert approved_record.approval is not None
    assert approved_record.approval.decision == "APPROVED"
    assert approved_record.approval.reviewer == "Rupam Patne"


def test_workflow_rejection_at_approval_gate(workflow_instance):
    """Verify human rejection records notes and transitions to REJECTED."""
    req = WorkflowRequest(
        request_id="TEST-REQ-003",
        title="Contingency Pilot",
        proposal_text="Execute Q4 enterprise campaign with $40,000 planned spend.",
        requested_budget=40000.0
    )

    workflow_instance.evaluate_proposal(req)
    rejected_record = workflow_instance.submit_approval(
        request_id="TEST-REQ-003",
        decision="REJECTED",
        reviewer="Finance Director",
        notes="Too close to contingency reserve; defer to Q1."
    )

    assert rejected_record.status == WorkflowStatus.REJECTED
    assert rejected_record.approval.decision == "REJECTED"


def test_workflow_budget_overspend_triggers_rejection_recommendation(workflow_instance):
    """Verify that a proposal exceeding policy budget ceiling is recommended for rejection."""
    req = WorkflowRequest(
        request_id="TEST-REQ-OVERBUDGET",
        title="Excessive Spend Proposal",
        proposal_text="Massive marketing blitz requesting $85,000 across multiple acquisition channels.",
        requested_budget=85000.0
    )

    record = workflow_instance.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.recommendation is not None
    assert record.recommendation.recommended_action == "REJECT"
    assert "exceeds" in record.recommendation.risk_assessment.lower()


def test_workflow_material_conflict_detection(workflow_instance):
    """Verify that conflicting policy rules halt workflow with CONFLICT_DETECTED status."""
    req = WorkflowRequest(
        request_id="TEST-REQ-CONFLICT",
        title="Influencer Spend Scaling",
        proposal_text="Allocate funds for influencer partnership spend ceiling and celebrity creator endorsements.",
        requested_budget=18000.0
    )

    record = workflow_instance.evaluate_proposal(req)
    assert record.status == WorkflowStatus.CONFLICT_DETECTED
    assert record.conflict is not None
    assert "DOC-MKT-002" in record.conflict.conflicting_sources
    assert "DOC-MKT-004" in record.conflict.conflicting_sources
    assert record.recommendation is None  # Does not produce ungrounded recommendation


def test_workflow_insufficient_evidence_handling(workflow_instance):
    """Verify that out-of-domain proposals trigger INSUFFICIENT_EVIDENCE."""
    req = WorkflowRequest(
        request_id="TEST-REQ-UNKNOWN",
        title="Offshore Oil Drilling Exploration",
        proposal_text="Purchase deep-sea petroleum extraction equipment and offshore pipelines.",
        requested_budget=25000.0
    )

    record = workflow_instance.evaluate_proposal(req)
    assert record.status == WorkflowStatus.INSUFFICIENT_EVIDENCE
    assert record.recommendation is None


def test_workflow_invalid_input_validation(workflow_instance):
    """Verify boundary conditions and malformed input handling."""
    # Empty request_id
    bad_req1 = WorkflowRequest(
        request_id="   ",
        title="Valid Title",
        proposal_text="Valid proposal text longer than ten chars."
    )
    rec1 = workflow_instance.evaluate_proposal(bad_req1)
    assert rec1.status == WorkflowStatus.INVALID_REQUEST

    # Negative budget
    bad_req2 = WorkflowRequest(
        request_id="TEST-NEG",
        title="Negative Budget Test",
        proposal_text="Valid proposal text longer than ten chars.",
        requested_budget=-1000.0
    )
    rec2 = workflow_instance.evaluate_proposal(bad_req2)
    assert rec2.status == WorkflowStatus.INVALID_REQUEST


def test_record_store_scrubs_secrets_before_persisting(tmp_path):
    """Verify security constraint: No API keys or secrets are stored in the record store."""
    store = RecordStore(tmp_path / "secure_records")
    fake_secret = "gsk_1234567890abcdef1234567890"

    req = WorkflowRequest(
        request_id="TEST-SECRET",
        title="Key Leak Test",
        proposal_text=f"Testing secret leakage protection with {fake_secret} inside proposal."
    )
    record = WorkflowRecord(
        request_id="TEST-SECRET",
        status=WorkflowStatus.AWAITING_APPROVAL,
        request=req,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat()
    )

    store.save_record(record)

    raw_file_text = (tmp_path / "secure_records" / "records.json").read_text(encoding="utf-8")
    assert fake_secret not in raw_file_text
    assert "[REDACTED_SECRET]" in raw_file_text
