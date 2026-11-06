"""Tests for strict separation between 'workflow ask' and 'workflow evaluate' CLI commands.

Verifies:
1. 'workflow ask' performs pure policy Q&A without asking for budget or creating records.
2. 'workflow evaluate' executes full 7-stage proposal evaluation and enforces human approval gate.
3. Presets (growth, incomplete, conflict, overspend) continue to work properly.
4. Approval and rejection CLI commands update audit trail and prevent duplicate finalization.
5. Replay, list, and show subcommands function deterministically.
"""
import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from evidence_rag.cli import main
from evidence_rag.record_store import RecordStore
from evidence_rag.workflow_schemas import WorkflowStatus


@pytest.fixture
def cli_runner():
    """Provide a Click test runner."""
    return CliRunner()


@pytest.fixture
def isolated_record_store(tmp_path, monkeypatch):
    """Ensure records are stored in an isolated temporary directory during testing."""
    records_dir = tmp_path / "data" / "workflow_records"
    records_dir.mkdir(parents=True, exist_ok=True)
    
    # Patch DecisionWorkflow default records dir
    from evidence_rag import workflow
    orig_init = workflow.DecisionWorkflow.__init__
    
    def patched_init(self, config_path="configs/default.yaml", record_store=None):
        if record_store is None:
            record_store = RecordStore(records_dir)
        orig_init(self, config_path=config_path, record_store=record_store)
        
    monkeypatch.setattr(workflow.DecisionWorkflow, "__init__", patched_init)
    return RecordStore(records_dir)


def test_workflow_ask_policy_question_no_budget_prompt_no_record(cli_runner, isolated_record_store):
    """Assertion 1 & 11: 'workflow ask' answers policy questions without budget prompt or record creation."""
    initial_records = isolated_record_store.list_records()
    initial_count = len(initial_records)

    result = cli_runner.invoke(main, [
        "workflow", "ask", "What is the budget ceiling in DOC-022?"
    ])

    assert result.exit_code == 0, f"Command failed: {result.output}"
    # Must contain evidence answer and document reference
    assert "DOC-022" in result.output
    assert "ANSWERED" in result.output

    # Must NOT prompt for budget or treat as proposal
    assert "Requested budget" not in result.output
    assert "Proposal Title" not in result.output
    assert "Request ID: REQ-" not in result.output
    assert "AWAITING_APPROVAL" not in result.output
    assert "Human Approval Gate" not in result.output
    assert "Reviewer name" not in result.output

    # Must NOT create a record in records.json
    records_after = isolated_record_store.list_records()
    assert len(records_after) == initial_count


def test_workflow_ask_interactive_prompt(cli_runner, isolated_record_store):
    """Assertion 1: 'workflow ask' without arguments prompts for a question interactively."""
    result = cli_runner.invoke(
        main,
        ["workflow", "ask"],
        input="What is the daily spend ceiling for new digital ad campaigns in DOC-022?\n"
    )

    assert result.exit_code == 0, f"Interactive ask failed: {result.output}"
    assert "Enter your policy question" in result.output
    assert "DOC-022" in result.output
    assert "Requested budget" not in result.output


def test_workflow_evaluate_creates_record_and_awaiting_approval(cli_runner, isolated_record_store):
    """Assertion 2: 'workflow evaluate' creates an AWAITING_APPROVAL record and evaluates budget."""
    initial_count = len(isolated_record_store.list_records())

    result = cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--title", "Enterprise Expansion",
        "--proposal", "Deploy paid search campaigns across Google and Bing targeting B2B leads.",
        "--budget", "20000"
    ])

    assert result.exit_code == 0, f"Evaluate failed: {result.output}"
    assert "AWAITING_APPROVAL" in result.output
    assert "REQ-" in result.output
    assert "Workflow Proposal Evaluation" in result.output

    # Record store count must increase by exactly 1
    records_after = isolated_record_store.list_records()
    assert len(records_after) == initial_count + 1


def test_workflow_evaluate_interactive_approve(cli_runner, isolated_record_store):
    """Assertion 3: Interactive evaluate allows approving at the human approval gate."""
    result = cli_runner.invoke(
        main,
        [
            "workflow", "evaluate",
            "--title", "Content Marketing Campaign",
            "--proposal", "Produce quarterly thought leadership research whitepapers with paid promotion.",
            "--budget", "18000",
            "--interactive"
        ],
        input="a\nRupam Patne\nAudited against DOC-022 budget ceiling; approved.\n"
    )

    assert result.exit_code == 0, f"Interactive evaluate failed: {result.output}"
    assert "APPROVED by Rupam Patne" in result.output

    # Verify latest record is stored as APPROVED
    latest_record = isolated_record_store.list_records()[0]
    assert latest_record.status == WorkflowStatus.APPROVED
    assert latest_record.approval is not None
    assert latest_record.approval.reviewer == "Rupam Patne"


def test_workflow_evaluate_interactive_reject(cli_runner, isolated_record_store):
    """Assertion 3: Interactive evaluate allows rejecting at the human approval gate."""
    result = cli_runner.invoke(
        main,
        [
            "workflow", "evaluate",
            "--title", "Uncapped Influencer Push",
            "--proposal", "Deploy broad influencer sponsorships on unverified social channels.",
            "--budget", "85000",
            "--interactive"
        ],
        input="r\nRupam Patne\nExceeds departmental discretionary spend ceiling.\n"
    )

    assert result.exit_code == 0, f"Interactive reject failed: {result.output}"
    assert "REJECTED by Rupam Patne" in result.output

    latest_record = isolated_record_store.list_records()[0]
    assert latest_record.status == WorkflowStatus.REJECTED
    assert latest_record.approval is not None
    assert latest_record.approval.reviewer == "Rupam Patne"


def test_workflow_evaluate_interactive_skip(cli_runner, isolated_record_store):
    """Assertion 3: Interactive evaluate allows skipping to leave proposal in initial evaluated state."""
    result = cli_runner.invoke(
        main,
        [
            "workflow", "evaluate",
            "--title", "Paid Enterprise Search",
            "--proposal", "Deploy paid search campaigns on Google targeting enterprise decision makers with $15,000 budget.",
            "--budget", "15000",
            "--interactive"
        ],
        input="s\n"
    )

    assert result.exit_code == 0
    assert "remains PAUSED in AWAITING_APPROVAL state" in result.output

    latest_record = isolated_record_store.list_records()[0]
    assert latest_record.status == WorkflowStatus.AWAITING_APPROVAL
    assert latest_record.approval is None


def test_workflow_approve_and_reject_commands(cli_runner, isolated_record_store):
    """Assertion 4 & 5: 'workflow approve' and 'workflow reject' commands transition records."""
    # Create proposal 1 (to approve)
    eval1 = cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--request-id", "REQ-TEST-APP-01",
        "--title", "Webinar Series",
        "--proposal", "Host 4 technical webinars with paid registration promotion.",
        "--budget", "15000"
    ])
    assert eval1.exit_code == 0

    # Approve proposal 1
    app_res = cli_runner.invoke(main, [
        "workflow", "approve", "REQ-TEST-APP-01",
        "--reviewer", "Rupam Patne",
        "--notes", "Fully compliant with DOC-022."
    ])
    assert app_res.exit_code == 0
    assert "APPROVED" in app_res.output
    assert "Rupam Patne" in app_res.output

    rec1 = isolated_record_store.get_record("REQ-TEST-APP-01")
    assert rec1 is not None
    assert rec1.status == WorkflowStatus.APPROVED
    assert rec1.approval.reviewer == "Rupam Patne"

    # Create proposal 2 (to reject)
    eval2 = cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--request-id", "REQ-TEST-REJ-01",
        "--title", "Experimental Ads",
        "--proposal", "Experimental untracked paid ads across gaming networks.",
        "--budget", "30000"
    ])
    assert eval2.exit_code == 0

    # Reject proposal 2
    rej_res = cli_runner.invoke(main, [
        "workflow", "reject", "REQ-TEST-REJ-01",
        "--reviewer", "Rupam Patne",
        "--reason", "Unapproved channel violating DOC-025."
    ])
    assert rej_res.exit_code == 0
    assert "REJECTED" in rej_res.output
    assert "Rupam Patne" in rej_res.output

    rec2 = isolated_record_store.get_record("REQ-TEST-REJ-01")
    assert rec2 is not None
    assert rec2.status == WorkflowStatus.REJECTED


def test_duplicate_approval_prevention(cli_runner, isolated_record_store):
    """Assertion 6: Approving an already finalized proposal is strictly blocked."""
    cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--request-id", "REQ-TEST-DUP-01",
        "--title", "Brand Lift Survey",
        "--proposal", "Execute third-party brand perception survey.",
        "--budget", "10000"
    ])
    cli_runner.invoke(main, [
        "workflow", "approve", "REQ-TEST-DUP-01",
        "--reviewer", "Rupam Patne",
        "--notes", "Approved."
    ])

    # Second approval attempt must fail
    dup_res = cli_runner.invoke(main, [
        "workflow", "approve", "REQ-TEST-DUP-01",
        "--reviewer", "Another Reviewer",
        "--notes", "Attempting second approval."
    ])
    assert dup_res.exit_code != 0
    assert "already finalized" in dup_res.output or "Error" in dup_res.output


def test_workflow_presets(cli_runner, isolated_record_store):
    """Assertion 7: Presets (growth, incomplete, conflict, overspend) evaluate correctly."""
    # Growth preset ($35,000 LinkedIn)
    growth_res = cli_runner.invoke(main, ["workflow", "evaluate", "--preset", "growth"])
    assert growth_res.exit_code == 0
    assert "REQ-GROWTH-01" in growth_res.output
    assert "AWAITING_APPROVAL" in growth_res.output

    # Incomplete preset (missing required details)
    incomp_res = cli_runner.invoke(main, ["workflow", "evaluate", "--preset", "incomplete"])
    assert incomp_res.exit_code == 0
    assert "REQ-INCOMPLETE-01" in incomp_res.output

    # Conflict preset (influencer spend discrepancy)
    conflict_res = cli_runner.invoke(main, ["workflow", "evaluate", "--preset", "conflict"])
    assert conflict_res.exit_code == 0
    assert "REQ-CONFLICT-01" in conflict_res.output

    # Overspend preset (budget exceeding limit)
    over_res = cli_runner.invoke(main, ["workflow", "evaluate", "--preset", "overspend"])
    assert over_res.exit_code == 0
    assert "REQ-OVERSPEND-01" in over_res.output


def test_workflow_list_show_and_replay(cli_runner, isolated_record_store):
    """Assertion 8, 9, 10: 'list', 'show', and 'replay' subcommands work properly."""
    # Create a proposal to inspect and replay
    cli_runner.invoke(main, [
        "workflow", "evaluate",
        "--request-id", "REQ-TEST-INSPECT-01",
        "--title", "Podcast Sponsorship",
        "--proposal", "Sponsor 5 episodes of enterprise engineering podcast.",
        "--budget", "15000"
    ])

    # Test list
    list_res = cli_runner.invoke(main, ["workflow", "list"])
    assert list_res.exit_code == 0
    assert "Podcast" in list_res.output

    # Test show
    show_res = cli_runner.invoke(main, ["workflow", "show", "REQ-TEST-INSPECT-01"])
    assert show_res.exit_code == 0
    assert "Podcast Sponsorship" in show_res.output

    # Test replay
    replay_res = cli_runner.invoke(main, ["workflow", "replay", "REQ-TEST-INSPECT-01"])
    assert replay_res.exit_code == 0
    assert "Workflow Replay" in replay_res.output
    assert "Original Status" in replay_res.output
