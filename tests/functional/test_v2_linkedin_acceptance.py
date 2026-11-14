"""Acceptance test suite for V2 LinkedIn Campaign Proposal (AC-4, AC-5, AC-6).

Author: Rhugved (Senior Python Backend Engineer, RAG Architect, Software Auditor)
Target: BHIV CMO Agent V2 - Governance Hard Stop, Reviewer Identity, Duplicate Decision.
"""
import pytest
from click.testing import CliRunner

from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus
from evidence_rag.cli import main
from evidence_rag.record_store import RecordStore


@pytest.fixture
def cli_runner():
    """Provide a Click test runner."""
    return CliRunner()


@pytest.fixture
def isolated_record_store(tmp_path, monkeypatch):
    """Ensure records are stored in an isolated temporary directory during testing."""
    records_dir = tmp_path / "data" / "workflow_records"
    records_dir.mkdir(parents=True, exist_ok=True)

    from evidence_rag import workflow
    orig_init = workflow.DecisionWorkflow.__init__

    def patched_init(self, config_path="configs/default.yaml", record_store=None):
        if record_store is None:
            record_store = RecordStore(records_dir)
        orig_init(self, config_path=config_path, record_store=record_store)

    monkeypatch.setattr(workflow.DecisionWorkflow, "__init__", patched_init)
    return RecordStore(records_dir)


@pytest.fixture
def workflow_env(tmp_path):
    """Isolated workflow instance with temporary record storage."""
    store = RecordStore(tmp_path / "v2_records")
    return DecisionWorkflow(record_store=store)


def test_ac4_governance_hard_stop(workflow_env):
    """AC-4: Verify proposal stops at AWAITING_APPROVAL with zero external side effects."""
    req = WorkflowRequest(
        request_id="REQ-MKT-2026-LI-01",
        title="Q4 Enterprise LinkedIn Lead Gen Campaign",
        proposal_text="Objective: Increase enterprise SQLs by 25%. Channel: LinkedIn Ads. Budget: $30,000 USD.",
        department="Marketing",
        requested_budget=30000.0,
        submitted_by="Rhugved"
    )

    record = workflow_env.evaluate_proposal(req)

    # 1. State must halt strictly at AWAITING_APPROVAL
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.request_id == "REQ-MKT-2026-LI-01"

    # 2. Automated system must not approve or record approval autonomously
    assert record.approval is None

    # 3. Recommendations and verified facts are synthesized
    assert record.recommendation is not None
    assert len(record.recommendation.verified_facts) > 0

    # 4. History reflects governance pause
    actions = [h["action"] for h in record.history]
    assert "REQUEST_SUBMITTED" in actions
    assert "EVIDENCE_RETRIEVED" in actions
    assert "RECOMMENDATION_SYNTHESIZED" in actions
    assert "AWAITING_HUMAN_APPROVAL" in actions


def test_ac5_reviewer_identity_validation(workflow_env):
    """AC-5: Verify blank reviewer and default Prof_Evaluator are rejected."""
    req = WorkflowRequest(
        request_id="REQ-MKT-2026-LI-01",
        title="Q4 Enterprise LinkedIn Lead Gen Campaign",
        proposal_text="Objective: Increase enterprise SQLs by 25%. Channel: LinkedIn Ads. Budget: $30,000 USD.",
        department="Marketing",
        requested_budget=30000.0,
        submitted_by="Rhugved"
    )
    workflow_env.evaluate_proposal(req)

    # 1. Blank reviewer must be rejected
    with pytest.raises(ValueError, match="Reviewer identity cannot be blank"):
        workflow_env.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="REJECTED",
            reviewer="",
            notes="Rejected due to cap breach"
        )

    # 2. Whitespace-only reviewer must be rejected
    with pytest.raises(ValueError, match="Reviewer identity cannot be blank"):
        workflow_env.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="REJECTED",
            reviewer="   ",
            notes="Rejected due to cap breach"
        )

    # 3. Default placeholder 'Prof_Evaluator' must be rejected
    with pytest.raises(ValueError, match="Default reviewer placeholder 'Prof_Evaluator' is rejected"):
        workflow_env.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="REJECTED",
            reviewer="Prof_Evaluator",
            notes="Rejected due to cap breach"
        )

    # 4. Empty justification notes must be rejected
    with pytest.raises(ValueError, match="Decision justification notes are mandatory"):
        workflow_env.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="REJECTED",
            reviewer="Pratik Bhuwad - CMO Product Owner",
            notes=""
        )

    # 5. Explicit authorized reviewer 'Pratik Bhuwad - CMO Product Owner' must succeed
    decided = workflow_env.submit_approval(
        request_id="REQ-MKT-2026-LI-01",
        decision="REJECTED",
        reviewer="Pratik Bhuwad - CMO Product Owner",
        notes="Rejected: Proposed budget of $30,000 USD exceeds the $15,000 USD LinkedIn Ads channel cap specified in DOC-MKT-002."
    )
    assert decided.status == WorkflowStatus.REJECTED
    assert decided.approval.reviewer == "Pratik Bhuwad - CMO Product Owner"
    assert "DOC-MKT-002" in decided.approval.decision_notes


def test_ac6_duplicate_decision_prevention(workflow_env):
    """AC-6: Attempt to re-decide a finalized proposal and verify ValueError: Request already finalized."""
    req = WorkflowRequest(
        request_id="REQ-MKT-2026-LI-01",
        title="Q4 Enterprise LinkedIn Lead Gen Campaign",
        proposal_text="Objective: Increase enterprise SQLs by 25%. Channel: LinkedIn Ads. Budget: $30,000 USD.",
        department="Marketing",
        requested_budget=30000.0,
        submitted_by="Rhugved"
    )
    workflow_env.evaluate_proposal(req)

    # Initial decision finalized
    workflow_env.submit_approval(
        request_id="REQ-MKT-2026-LI-01",
        decision="REJECTED",
        reviewer="Pratik Bhuwad - CMO Product Owner",
        notes="First decision recorded."
    )

    # Second decision attempt must raise exact error: ValueError: Request already finalized
    with pytest.raises(ValueError, match="Request already finalized"):
        workflow_env.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="APPROVED",
            reviewer="Pratik Bhuwad - CMO Product Owner",
            notes="Attempting second decision on finalized proposal."
        )


def test_cli_v2_acceptance_flow(cli_runner, isolated_record_store):
    """Verify AC-4, AC-5, and AC-6 end-to-end through Click CLI."""
    # AC-4: Evaluate proposal via CLI
    eval_res = cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--request-id", "REQ-MKT-2026-LI-01",
        "--title", "Q4 Enterprise LinkedIn Lead Gen Campaign",
        "--proposal", "Objective: Increase enterprise SQLs by 25%. Channel: LinkedIn Ads. Budget: $30,000 USD.",
        "--budget", "30000"
    ])
    assert eval_res.exit_code == 0
    assert "REQ-MKT-2026-LI-01" in eval_res.output
    assert "AWAITING_APPROVAL" in eval_res.output

    # AC-5: Blank reviewer via CLI is rejected
    res_blank = cli_runner.invoke(main, [
        "workflow", "reject", "REQ-MKT-2026-LI-01",
        "--reviewer", " ",
        "--reason", "Test"
    ])
    assert res_blank.exit_code != 0
    assert "Reviewer identity cannot be blank" in res_blank.output

    # AC-5: Default Prof_Evaluator via CLI is rejected
    res_prof = cli_runner.invoke(main, [
        "workflow", "reject", "REQ-MKT-2026-LI-01",
        "--reviewer", "Prof_Evaluator",
        "--reason", "Test"
    ])
    assert res_prof.exit_code != 0
    assert "Default reviewer placeholder 'Prof_Evaluator' is rejected" in res_prof.output

    # AC-5: Valid reviewer succeeds
    res_valid = cli_runner.invoke(main, [
        "workflow", "reject", "REQ-MKT-2026-LI-01",
        "--reviewer", "Pratik Bhuwad - CMO Product Owner",
        "--reason", "Rejected: Exceeds the $15,000 USD LinkedIn Ads cap."
    ])
    assert res_valid.exit_code == 0
    assert "REJECTED" in res_valid.output
    assert "Pratik Bhuwad - CMO Product Owner" in res_valid.output

    # AC-6: Duplicate decision via CLI is rejected with 'Request already finalized'
    res_dup = cli_runner.invoke(main, [
        "workflow", "approve", "REQ-MKT-2026-LI-01",
        "--reviewer", "Pratik Bhuwad - CMO Product Owner",
        "--notes", "Attempting second decision"
    ])
    assert res_dup.exit_code != 0
    assert "Request already finalized" in res_dup.output
