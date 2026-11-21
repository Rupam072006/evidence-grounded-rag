"""Proposal lifecycle routes: intake evaluation, approval, rejection, replay, and audit."""
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from evidence_rag.api.schemas import (
    ProposalEvaluateRequest,
    ProposalApprovalRequest,
    ProposalRejectionRequest,
)
from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowRecord, WorkflowStatus
from evidence_rag.api.dependencies import get_workflow, verify_tantra_token
from evidence_rag.workflow import DecisionWorkflow, validate_reviewer_identity
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.api.routes.proposals")

router = APIRouter(tags=["Proposal Governance"])


@router.post("/proposals/evaluate", response_model=WorkflowRecord)
def evaluate_proposal(
    req: ProposalEvaluateRequest,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> WorkflowRecord:
    """Submit a campaign proposal for automated evidence evaluation.

    MANDATORY GOVERNANCE GATE:
    The service stops strictly at AWAITING_APPROVAL (or INSUFFICIENT_EVIDENCE / CONFLICT_DETECTED).
    Proposals awaiting review are returned with approval: null. No autonomous approval or external
    ad spend is ever triggered.
    """
    request_id = req.proposal_id or req.request_id
    if not request_id:
        request_id = f"REQ-MKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    metadata = dict(req.metadata or {})
    if req.channel:
        metadata["channel"] = req.channel

    wf_req = WorkflowRequest(
        request_id=request_id,
        title=req.title,
        proposal_text=req.proposal_text,
        department=req.department or "Marketing",
        requested_budget=req.requested_budget,
        submitted_by=req.submitted_by or "analyst",
        metadata=metadata
    )

    record = workflow.evaluate_proposal(wf_req)
    # Verification of hard stop: Must not be auto-approved
    if record.status == WorkflowStatus.APPROVED:
        logger.error(f"CRITICAL SAFETY VIOLATION: Proposal {request_id} was auto-approved!")
        record.status = WorkflowStatus.AWAITING_APPROVAL
        record.approval = None
        record = workflow.record_store.save_record(record)

    return record


@router.post("/proposals/{proposal_id}/approve", response_model=WorkflowRecord)
def approve_proposal(
    proposal_id: str,
    req: ProposalApprovalRequest,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> WorkflowRecord:
    """Submit human managerial approval for a proposal in AWAITING_APPROVAL state.

    Enforces:
    - Reviewer identity validation (QA-001)
    - State transition check (QA-002)
    - Rejection of duplicate decisions with HTTP 409 Conflict (DEFECT-003)
    """
    # 1. Check record existence
    record = workflow.get_record(proposal_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal record '{proposal_id}' not found."
        )

    # 2. Duplicate decision check -> 409 Conflict
    if record.status in (WorkflowStatus.APPROVED, WorkflowStatus.REJECTED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Proposal '{proposal_id}' has already been finalized with status '{record.status.value}'."
        )

    # 3. State transition validity check
    if record.status not in (WorkflowStatus.AWAITING_APPROVAL, WorkflowStatus.RECOMMENDATION_READY):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal '{proposal_id}' is in state '{record.status.value}' and cannot be approved."
        )

    # 4. Reviewer validation
    try:
        clean_reviewer = validate_reviewer_identity(req.reviewer_identity)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    notes = req.decision_notes or "Managerial approval granted based on documented Q4 strategic alignment."
    try:
        updated = workflow.submit_approval(
            request_id=proposal_id,
            decision="APPROVED",
            reviewer=clean_reviewer,
            notes=notes
        )
        return updated
    except ValueError as e:
        if "already finalized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/proposals/{proposal_id}/reject", response_model=WorkflowRecord)
def reject_proposal(
    proposal_id: str,
    req: ProposalRejectionRequest,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> WorkflowRecord:
    """Submit human managerial rejection for a proposal with mandatory justification.

    Enforces:
    - Reviewer identity validation (QA-001)
    - Non-empty justification notes
    - Rejection of duplicate decisions with HTTP 409 Conflict (DEFECT-003)
    """
    record = workflow.get_record(proposal_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal record '{proposal_id}' not found."
        )

    if record.status in (WorkflowStatus.APPROVED, WorkflowStatus.REJECTED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Proposal '{proposal_id}' has already been finalized with status '{record.status.value}'."
        )

    try:
        clean_reviewer = validate_reviewer_identity(req.reviewer_identity)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        updated = workflow.submit_approval(
            request_id=proposal_id,
            decision="REJECTED",
            reviewer=clean_reviewer,
            notes=req.decision_notes
        )
        return updated
    except ValueError as e:
        if "already finalized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/proposals/{proposal_id}/replay", response_model=WorkflowRecord)
def replay_proposal(
    proposal_id: str,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> WorkflowRecord:
    """Replay an existing proposal evaluation deterministically against the knowledge base."""
    record = workflow.get_record(proposal_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal record '{proposal_id}' not found for replay."
        )

    # Re-evaluate using original request payload
    replayed = workflow.evaluate_proposal(record.request)
    return replayed


@router.get("/proposals/{proposal_id}", response_model=WorkflowRecord)
def get_proposal(
    proposal_id: str,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> WorkflowRecord:
    """Retrieve an audit record by proposal ID."""
    record = workflow.get_record(proposal_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal record '{proposal_id}' not found."
        )
    return record


@router.get("/proposals", response_model=List[WorkflowRecord])
def list_proposals(
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> List[WorkflowRecord]:
    """List all stored proposal audit records."""
    return workflow.list_records()
