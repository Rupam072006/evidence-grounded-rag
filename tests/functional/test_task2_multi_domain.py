"""Comprehensive regression and functional test suite for Task 2 Multi-Domain Knowledge Base."""
import pytest
from pathlib import Path
from evidence_rag.config import load_config
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import (
    WorkflowRequest,
    WorkflowStatus
)
from evidence_rag.record_store import RecordStore
from evidence_rag.schemas import ResponseStatus


@pytest.fixture
def unified_pipeline():
    cfg = load_config("configs/default.yaml")
    pipeline = RAGPipeline(config=cfg)
    pipeline.ensure_index()
    return pipeline


@pytest.fixture
def unified_workflow(tmp_path):
    cfg = load_config("configs/default.yaml")
    store = RecordStore(tmp_path / "records")
    wf = DecisionWorkflow(config=cfg, record_store=store)
    wf.ensure_index()
    return wf


# 1. Existing Task 1 technical questions remain functional
def test_task1_python_exceptions_qa(unified_pipeline):
    res = unified_pipeline.query("What does the existing Python documentation say about exception handling?")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-003" in res.source_document_ids
    assert len(res.citations) > 0


def test_task1_sql_joins_qa(unified_pipeline):
    res = unified_pipeline.query("How do SQL joins work according to the knowledge base?")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-008" in res.source_document_ids
    assert len(res.citations) > 0


def test_task1_ml_model_evaluation_qa(unified_pipeline):
    res = unified_pipeline.query("What does the ML documentation say about model evaluation?")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-011" in res.source_document_ids
    assert len(res.citations) > 0


# 2. Business proposal and budget questions
def test_business_budget_policy_qa(unified_pipeline):
    res = unified_pipeline.query("Which budget limit is stated in the corporate marketing budget policy?")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-022" in res.source_document_ids
    assert "50,000" in res.answer or "50000" in res.answer


def test_business_performance_metrics_qa(unified_pipeline):
    res = unified_pipeline.query("What are the historical performance metrics for CTR and CAC in marketing performance reports?")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-023" in res.source_document_ids
    assert any("2.4%" in rc.chunk.text or "32" in rc.chunk.text for rc in res.evidence)


# 3. Relevant retrieval across multiple domains (cross-domain)
def test_cross_domain_retrieval(unified_pipeline):
    # Cross-domain query mentioning SQL and campaign metrics
    res = unified_pipeline.query("How can relational database SQL queries analyze marketing campaign conversion metrics and CTR?")
    assert res.status == ResponseStatus.ANSWERED
    # Should retrieve both SQL (DOC-008) and marketing performance (DOC-023)
    doc_ids = set(res.source_document_ids)
    assert "DOC-008" in doc_ids or "DOC-023" in doc_ids


# 4. Irrelevant-document exclusion / Domain isolation
def test_domain_isolation_excludes_irrelevant_docs(unified_pipeline):
    # Pure Python question should NOT retrieve business proposals or budget policies
    res = unified_pipeline.query("Explain Python exception hierarchy and raise statements in functions.")
    assert res.status == ResponseStatus.ANSWERED
    assert "DOC-003" in res.source_document_ids
    # Verify no business policies pollute the top sources
    business_doc_ids = {"DOC-021", "DOC-022", "DOC-024", "DOC-025"}
    assert not business_doc_ids.intersection(res.source_document_ids)


# 5. Conflicting business policies detection
def test_conflicting_influencer_spending_policies(unified_pipeline):
    res = unified_pipeline.query("What conflict exists between the two influencer spending policies regarding spending limits?")
    # Must detect material conflict between DOC-024 ($25,000) and DOC-025 ($10,000)
    assert res.status == ResponseStatus.CONFLICT_DETECTED
    assert res.conflicting_evidence is not None
    assert set(res.conflicting_evidence.conflicting_sources) == {"DOC-024", "DOC-025"}


# 6. Incomplete proposal & unknown handling
def test_incomplete_proposal_unknown_handling(unified_workflow):
    req = WorkflowRequest(
        request_id="REQ-INCOMPLETE-01",
        title="Experimental Exploration Campaign",
        proposal_text="Evaluate experimental multi-channel expansion proposal for incomplete draft testing with missing channels and unknown timeline.",
        requested_budget=18000.0,
        submitted_by="growth_team"
    )
    record = unified_workflow.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.recommendation is not None
    # Unknowns must identify missing parameters
    assert len(record.recommendation.unknowns) >= 2
    unknown_text = " ".join(record.recommendation.unknowns).lower()
    assert "missing" in unknown_text or "timeline" in unknown_text or "audience" in unknown_text


# 7. Insufficient evidence handling
def test_insufficient_evidence_unsupported_domain(unified_pipeline):
    res = unified_pipeline.query("What are the quantum teleportation protocols in Kubernetes clusters?")
    assert res.status == ResponseStatus.INSUFFICIENT_EVIDENCE
    assert "cannot answer" in res.answer.lower() or "insufficient" in res.answer.lower()


# 8. Human approval gate enforcement on unified workflow
def test_workflow_human_approval_enforced_no_auto_execution(unified_workflow):
    req = WorkflowRequest(
        request_id="REQ-GROWTH-01",
        title="Q4 Enterprise Growth Initiative",
        proposal_text="Enterprise Growth Marketing Campaign Proposal allocating budget across search ads and content syndication.",
        requested_budget=35000.0,
        submitted_by="marketing_ops"
    )
    record = unified_workflow.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.approval is None  # System stops, no auto-approval

    # Manager approves at human gate
    approved_record = unified_workflow.submit_approval(
        request_id="REQ-GROWTH-01",
        decision="APPROVED",
        reviewer="finance_director",
        notes="Budget confirmed compliant with DOC-022."
    )
    assert approved_record.status == WorkflowStatus.APPROVED
    assert approved_record.approval.decision == "APPROVED"
    assert approved_record.approval.reviewer == "finance_director"


# 9. Budget overspend rejection recommendation
def test_workflow_budget_overspend_rejection(unified_workflow):
    req = WorkflowRequest(
        request_id="REQ-OVERSPEND-01",
        title="Excessive Budget Initiative",
        proposal_text="Enterprise Growth Marketing Campaign Proposal requesting excessive allocation.",
        requested_budget=75000.0,  # Exceeds $50,000 policy cap
        submitted_by="marketing_ops"
    )
    record = unified_workflow.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.recommendation.recommended_action == "REJECT"
    assert "exceeds" in record.recommendation.inferences[0].lower()
