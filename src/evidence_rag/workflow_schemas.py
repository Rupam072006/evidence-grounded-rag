"""Workflow schemas, data contracts, and status models for Decision-Support."""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from evidence_rag.schemas import RetrievedChunk, Citation, ConflictEvidence


class WorkflowStatus(str, Enum):
    """Execution and governance statuses for the decision-support workflow."""
    INVALID_REQUEST = "INVALID_REQUEST"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    RECOMMENDATION_READY = "RECOMMENDATION_READY"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    GENERATION_FAILED = "GENERATION_FAILED"
    INDEX_UNAVAILABLE = "INDEX_UNAVAILABLE"


class WorkflowRequest(BaseModel):
    """Incoming decision request submitted for analysis and human review."""
    request_id: str = Field(..., description="Unique immutable request ID, e.g. REQ-2026-001")
    title: str = Field(..., description="Short descriptive proposal or request title")
    proposal_text: str = Field(..., description="Full text description of the proposed action or question")
    department: str = Field(default="Marketing", description="Requesting department or domain")
    requested_budget: Optional[float] = Field(default=None, description="Proposed spend if financial")
    submitted_by: str = Field(default="analyst", description="User or system submitting the request")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 creation timestamp"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary domain parameters")


class VerifiedFact(BaseModel):
    """Material factual statement backed by an explicit citation to retrieved evidence."""
    statement: str = Field(..., description="Grounded factual statement")
    citation: Citation = Field(..., description="Source citation reference")
    source_document_id: str = Field(..., description="Document ID providing evidence")
    source_chunk_id: str = Field(..., description="Chunk ID providing evidence")


class RecommendationReport(BaseModel):
    """Structured decision analysis clearly separating facts, inferences, assumptions, and unknowns."""
    summary: str = Field(..., description="Executive summary of the evaluation")
    verified_facts: List[VerifiedFact] = Field(
        default_factory=list,
        description="Explicit factual claims backed by retrieved document citations"
    )
    inferences: List[str] = Field(
        default_factory=list,
        description="Logical deductions drawn from the verified facts"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit conditions assumed to hold true"
    )
    unknowns: List[str] = Field(
        default_factory=list,
        description="Information gaps or missing criteria not addressed in the corpus"
    )
    risk_assessment: str = Field(..., description="Identified operational, compliance, or financial risks")
    recommended_action: str = Field(
        ...,
        description="Proposed action for human manager (e.g. APPROVE_WITH_CONDITIONS, REJECT, REQUEST_MORE_INFO)"
    )


class ApprovalDecision(BaseModel):
    """Record of human manager approval or rejection at the governance gate."""
    request_id: str = Field(..., description="Target request ID")
    decision: str = Field(..., description="Final decision: APPROVED or REJECTED")
    reviewer: str = Field(..., description="Name or identifier of human decision-maker")
    decision_notes: str = Field(..., description="Justification or feedback provided by reviewer")
    decided_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 decision timestamp"
    )


class WorkflowRecord(BaseModel):
    """Complete audit record for a decision-support transaction."""
    request_id: str
    status: WorkflowStatus
    request: WorkflowRequest
    evidence_set: List[RetrievedChunk] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    conflict: Optional[ConflictEvidence] = None
    recommendation: Optional[RecommendationReport] = None
    approval: Optional[ApprovalDecision] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str
