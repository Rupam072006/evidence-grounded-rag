"""Pydantic API request and response data contracts for Path B."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from evidence_rag.workflow_schemas import WorkflowStatus, WorkflowRecord


class HealthResponse(BaseModel):
    """Path B microservice health, kernel, and adapter connectivity status."""
    status: str = Field(default="ok", description="Overall health state")
    version: str = Field(default="2.0.0", description="Service semantic version")
    path: str = Field(default="Path B", description="CMO Agent architectural delivery path")
    kernel_status: str = Field(default="READY", description="Knowledge engine kernel readiness")
    index_fingerprint: str = Field(..., description="Cryptographic SHA-256 fingerprint of knowledge index")
    persistence_status: str = Field(default="READY", description="Persistence adapter operational status")
    masterdb_status: str = Field(..., description="Local/Live MASTERDB connectivity status")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp"
    )


class KnowledgeQueryRequest(BaseModel):
    """Knowledge QA question request against the verified marketing corpus."""
    query: str = Field(..., min_length=3, description="Informational policy, benchmark, or strategy query")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum retrieved chunks")
    mode: Optional[str] = Field(default="retrieval_and_generation", description="Execution pipeline mode")


class KnowledgeQueryResponse(BaseModel):
    """Evidence-grounded response to a marketing knowledge question."""
    query: str
    answer: str
    confidence: float
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    trace_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProposalEvaluateRequest(BaseModel):
    """Campaign proposal submission for automated evaluation and approval gate."""
    proposal_id: Optional[str] = Field(default=None, description="Optional caller-specified proposal ID")
    request_id: Optional[str] = Field(default=None, description="Alias for proposal_id")
    title: str = Field(..., min_length=3, description="Descriptive title of campaign proposal")
    proposal_text: str = Field(..., min_length=10, description="Full narrative description and terms")
    department: Optional[str] = Field(default="Marketing", description="Requesting department")
    requested_budget: Optional[float] = Field(default=None, ge=0.0, description="Requested spend allocation in USD")
    channel: Optional[str] = Field(default=None, description="Primary advertising or execution channel")
    submitted_by: Optional[str] = Field(default="analyst", description="Identity of submitting agent or user")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom domain metadata")


class ProposalApprovalRequest(BaseModel):
    """Human manager approval submission."""
    reviewer_identity: str = Field(..., min_length=3, description="Explicit human reviewer name and title")
    decision_notes: Optional[str] = Field(
        default="Approved after review against Q4 strategic allocation ceilings and documented benchmarks.",
        description="Justification and sign-off notes"
    )


class ProposalRejectionRequest(BaseModel):
    """Human manager rejection submission."""
    reviewer_identity: str = Field(..., min_length=3, description="Explicit human reviewer name and title")
    decision_notes: str = Field(..., min_length=5, description="Mandatory audit justification for rejection")


class ErrorResponse(BaseModel):
    """Standardized API error response payload."""
    detail: str
    error_code: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
