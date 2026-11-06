"""Task 3 — Replay Tests.

Verifies that workflow replay reconstructs original evidence correctly
and clearly documents what replay can and cannot prove.
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from evidence_rag.record_store import RecordStore
from evidence_rag.workflow_schemas import (
    WorkflowRecord, WorkflowRequest, WorkflowStatus, ApprovalDecision,
    RecommendationReport, VerifiedFact
)
from evidence_rag.schemas import RetrievedChunk, Chunk, Citation


def _make_full_record(request_id: str) -> WorkflowRecord:
    now = datetime.now(timezone.utc).isoformat()
    req = WorkflowRequest(
        request_id=request_id,
        title="Q4 Growth Campaign",
        proposal_text="Allocate $35,000 for Google Search Ads.",
        department="Marketing",
        requested_budget=35000.0,
        submitted_by="analyst"
    )
    citation = Citation(document_id="DOC-022", chunk_id="DOC-022-C001", is_valid=True)
    fact = VerifiedFact(
        statement="Budget policy cap is $50,000 per campaign.",
        citation=citation,
        source_document_id="DOC-022",
        source_chunk_id="DOC-022-C001"
    )
    rec_report = RecommendationReport(
        summary="Budget is within policy limit of $50,000. Recommend approval.",
        verified_facts=[fact],
        inferences=["CTR of 2.4% is consistent with historical benchmarks."],
        assumptions=["Google Ads CPCs remain stable."],
        unknowns=[],
        risk_assessment="Low risk. Budget compliant.",
        recommended_action="APPROVE_WITH_CONDITIONS"
    )
    evidence_chunk = RetrievedChunk(
        chunk=Chunk(
            chunk_id="DOC-022-C001",
            document_id="DOC-022",
            chunk_index=0,
            text="Marketing budget cap is $50,000 per campaign cycle.",
            category="budget_policy"
        ),
        score=0.85,
        rank=1,
        raw_similarity=0.85
    )
    approval = ApprovalDecision(
        request_id=request_id,
        decision="APPROVED",
        reviewer="Prof_Evaluator",
        decision_notes="Budget compliant with DOC-022 policy.",
        decided_at=now
    )
    return WorkflowRecord(
        request_id=request_id,
        status=WorkflowStatus.APPROVED,
        request=req,
        evidence_set=[evidence_chunk],
        citations=[citation],
        recommendation=rec_report,
        approval=approval,
        history=[
            {"action": "HUMAN_APPROVED", "reviewer": "Prof_Evaluator",
             "decision_notes": "OK", "timestamp": now}
        ],
        created_at=now,
        updated_at=now
    )


def test_replay_record_retrievable(tmp_path):
    """Replay: Original record must be retrievable from store."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-001")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-001")
    assert retrieved is not None
    assert retrieved.request_id == "REQ-REPLAY-001"


def test_replay_original_evidence_preserved(tmp_path):
    """Replay: Original evidence set is preserved in the stored record."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-002")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-002")
    assert retrieved is not None
    assert len(retrieved.evidence_set) == 1
    assert retrieved.evidence_set[0].chunk.document_id == "DOC-022"


def test_replay_recommendation_preserved(tmp_path):
    """Replay: Original recommendation is preserved in stored record."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-003")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-003")
    assert retrieved.recommendation is not None
    assert retrieved.recommendation.recommended_action == "APPROVE_WITH_CONDITIONS"


def test_replay_approval_decision_preserved(tmp_path):
    """Replay: Approval decision metadata is preserved and retrievable."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-004")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-004")
    assert retrieved.approval is not None
    assert retrieved.approval.decision == "APPROVED"
    assert retrieved.approval.reviewer == "Prof_Evaluator"


def test_replay_does_not_prove_approval_legitimacy(tmp_path):
    """Replay: Recorded reviewer name is text — not authenticated identity proof."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-005")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-005")
    # Reviewer name is a string, not a verified cryptographic identity
    reviewer_name = retrieved.approval.reviewer
    assert isinstance(reviewer_name, str)
    # No cryptographic proof exists — this is a known limitation
    # The test asserts the limitation is structurally visible
    assert len(reviewer_name) > 0  # Name was recorded
    # But there is no signature or token to verify identity
    assert not hasattr(retrieved.approval, "identity_token")


def test_replay_history_audit_trail_preserved(tmp_path):
    """Replay: Full history audit trail is preserved in stored record."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-006")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-006")
    assert len(retrieved.history) >= 1
    assert retrieved.history[0]["reviewer"] == "Prof_Evaluator"


def test_replay_roundtrip_serialization(tmp_path):
    """Replay: Record survives JSON serialization/deserialization round-trip."""
    store = RecordStore(storage_dir=tmp_path)
    record = _make_full_record("REQ-REPLAY-007")
    store.save_record(record)

    retrieved = store.get_record("REQ-REPLAY-007")
    assert retrieved.request.requested_budget == 35000.0
    assert retrieved.request.title == "Q4 Growth Campaign"
    assert retrieved.status == WorkflowStatus.APPROVED

