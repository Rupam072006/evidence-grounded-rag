"""Functional integration test suite for CMO Agent Path B REST Microservice."""
import pytest
from fastapi.testclient import TestClient

from evidence_rag.api.app import create_app
from evidence_rag.workflow_schemas import WorkflowStatus
from evidence_rag.api.masterdb_client import MasterDBPersistenceAdapter


@pytest.fixture(scope="module")
def api_client(tmp_path_factory):
    """Create isolated TestClient with dedicated temporary storage for records."""
    temp_dir = tmp_path_factory.mktemp("api_test_records")
    app = create_app()

    # Override persistence adapter to use temp directory
    from evidence_rag.record_store import RecordStore
    from evidence_rag.api import dependencies

    temp_store = RecordStore(storage_dir=temp_dir)
    adapter = MasterDBPersistenceAdapter(
        base_url="http://127.0.0.1:8000",
        record_store=temp_store
    )
    dependencies._persistence_adapter = adapter

    from evidence_rag.workflow import DecisionWorkflow
    wf = DecisionWorkflow(record_store=temp_store)
    wf.ensure_index()
    dependencies._workflow_instance = wf

    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    """Standard Bearer token authorization header."""
    return {"Authorization": "Bearer mock-rs256-test-token"}


# -----------------------------------------------------------------------------
# 1. Health & Kernel Probe Tests
# -----------------------------------------------------------------------------
def test_health_probe_endpoints(api_client):
    """Verify GET /health and GET /api/v1/health return 200 OK with Path B metadata."""
    for path in ("/health", "/api/v1/health"):
        resp = api_client.get(path)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"
        assert data["path"] == "Path B"
        assert data["kernel_status"] == "READY"
        assert len(data["index_fingerprint"]) == 64  # Valid SHA-256 length
        assert data["persistence_status"] == "READY"
        assert "masterdb_status" in data


# -----------------------------------------------------------------------------
# 2. Authentication Enforcement Tests
# -----------------------------------------------------------------------------
def test_auth_enforcement_on_protected_routes(api_client):
    """Verify protected routes reject missing or invalid authorization tokens with 401."""
    # Missing header
    resp = api_client.post("/api/v1/query", json={"query": "What is our marketing budget?"})
    assert resp.status_code == 401
    assert "Missing Authorization header" in resp.json()["detail"]

    # Malformed header
    resp = api_client.post(
        "/api/v1/query",
        json={"query": "What is our marketing budget?"},
        headers={"Authorization": "Basic invalid-creds"}
    )
    assert resp.status_code == 401
    assert "Malformed Authorization header" in resp.json()["detail"]


# -----------------------------------------------------------------------------
# 3. Knowledge QA Query Route Tests
# -----------------------------------------------------------------------------
def test_knowledge_qa_query(api_client, auth_headers):
    """Verify POST /api/v1/query retrieves policy answers with citations."""
    payload = {
        "query": "What is the maximum allowed budget ceiling for influencer marketing campaigns?"
    }
    resp = api_client.post("/api/v1/query", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == payload["query"]
    assert len(data["answer"]) > 10
    assert "trace_id" in data
    assert data["trace_id"].startswith("TRC-QRY-")


# -----------------------------------------------------------------------------
# 4. Proposal Evaluation & Mandatory Approval Gate Tests
# -----------------------------------------------------------------------------
def test_evaluate_linkedin_proposal_halts_at_awaiting_approval(api_client, auth_headers):
    """Canonical test: $30,000 LinkedIn proposal MUST halt at AWAITING_APPROVAL with approval: null."""
    payload = {
        "proposal_id": "REQ-MKT-TEST-LINKEDIN-001",
        "title": "Q4 LinkedIn Sponsored Content Executive Acquisition",
        "proposal_text": (
            "Deploy sponsored content campaign on LinkedIn targeting enterprise decision makers. "
            "Total proposed media spend is $30,000. Expected CTR is 2.2% with estimated CAC of $35.00."
        ),
        "requested_budget": 30000.0,
        "channel": "LinkedIn",
        "submitted_by": "marketing_team"
    }

    resp = api_client.post("/api/v1/proposals/evaluate", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["request_id"] == "REQ-MKT-TEST-LINKEDIN-001"
    # Strict governance: Must be in AWAITING_APPROVAL
    assert data["status"] == WorkflowStatus.AWAITING_APPROVAL.value
    # Critical invariant: approval must be null
    assert data["approval"] is None

    # Recommendations must note the budget variance ($25,000 active media spend cap exceeded)
    rec = data["recommendation"]
    assert rec is not None
    assert rec["recommended_action"] in ("APPROVE_WITH_CONDITIONS", "REVIEW")
    assert any("30,000" in inf or "budget" in inf.lower() for inf in rec["inferences"])

    # History must record intake and awaiting approval
    actions = [h["action"] for h in data["history"]]
    assert "REQUEST_SUBMITTED" in actions
    assert "AWAITING_HUMAN_APPROVAL" in actions


def test_evaluate_linear_tv_abstains_with_insufficient_evidence(api_client, auth_headers):
    """DEFECT-SEMANTIC-001: Linear TV proposals must abstain with INSUFFICIENT_EVIDENCE."""
    payload = {
        "proposal_id": "REQ-MKT-TEST-LTV-001",
        "title": "National Linear TV Broadcaster Ad Pilot",
        "proposal_text": "Allocate $20,000 to Linear TV broadcasting advertising across primetime networks.",
        "requested_budget": 20000.0,
        "channel": "Linear TV"
    }

    resp = api_client.post("/api/v1/proposals/evaluate", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == WorkflowStatus.INSUFFICIENT_EVIDENCE.value
    assert data["approval"] is None


# -----------------------------------------------------------------------------
# 5. Human Manager Approval Gate Tests
# -----------------------------------------------------------------------------
def test_approval_rejects_placeholder_reviewer_identity(api_client, auth_headers):
    """QA-001: Reviewer identity validation rejects placeholders with 422."""
    disallowed_reviewers = ["prof_evaluator", "anonymous", "default", "none", "."]
    for reviewer in disallowed_reviewers:
        resp = api_client.post(
            "/api/v1/proposals/REQ-MKT-TEST-LINKEDIN-001/approve",
            json={"reviewer_identity": reviewer},
            headers=auth_headers
        )
        assert resp.status_code in (400, 422), f"Expected rejection for reviewer: '{reviewer}'"


def test_approval_succeeds_with_valid_reviewer(api_client, auth_headers):
    """Approve LinkedIn proposal with authorized reviewer Pratik Bhuwad."""
    approval_payload = {
        "reviewer_identity": "Pratik Bhuwad - CMO Product Owner",
        "decision_notes": "Approved with condition that spend is capped at $25,000 for initial 2-week flight."
    }

    resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-TEST-LINKEDIN-001/approve",
        json=approval_payload,
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == WorkflowStatus.APPROVED.value
    assert data["approval"] is not None
    assert data["approval"]["reviewer"] == "Pratik Bhuwad - CMO Product Owner"
    assert "initial 2-week flight" in data["approval"]["decision_notes"]

    # History contains HUMAN_APPROVED with trace_id (QA-003)
    latest_event = data["history"][-1]
    assert latest_event["action"] == "HUMAN_APPROVED"
    assert latest_event["reviewer"] == "Pratik Bhuwad - CMO Product Owner"
    assert latest_event.get("trace_id") == data["trace_id"]


def test_duplicate_approval_rejected_with_409_conflict(api_client, auth_headers):
    """DEFECT-003: Submitting approval on already-finalized proposal returns 409 Conflict."""
    resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-TEST-LINKEDIN-001/approve",
        json={"reviewer_identity": "Pratik Bhuwad - CMO Product Owner"},
        headers=auth_headers
    )
    assert resp.status_code == 409
    assert "already been finalized" in resp.json()["detail"].lower()


def test_approve_unapprovable_state_rejected(api_client, auth_headers):
    """QA-002: Attempting to approve an INSUFFICIENT_EVIDENCE proposal is rejected."""
    resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-TEST-LTV-001/approve",
        json={"reviewer_identity": "Pratik Bhuwad - CMO Product Owner"},
        headers=auth_headers
    )
    assert resp.status_code == 400
    assert "cannot be approved" in resp.json()["detail"].lower()


# -----------------------------------------------------------------------------
# 6. Proposal Rejection & Audit Tests
# -----------------------------------------------------------------------------
def test_rejection_lifecycle(api_client, auth_headers):
    """Submit proposal and reject it with auditable notes."""
    # Create proposal
    eval_resp = api_client.post(
        "/api/v1/proposals/evaluate",
        json={
            "proposal_id": "REQ-MKT-REJECT-001",
            "title": "Experimental Unverified Affiliate Program",
            "proposal_text": "Allocate $12,000 to third-party affiliate network without vendor vetting."
        },
        headers=auth_headers
    )
    assert eval_resp.status_code == 200

    # Reject
    rej_resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-REJECT-001/reject",
        json={
            "reviewer_identity": "Pratik Bhuwad - CMO Product Owner",
            "decision_notes": "Rejected: Vendor security audit not completed."
        },
        headers=auth_headers
    )
    assert rej_resp.status_code == 200
    rej_data = rej_resp.json()
    assert rej_data["status"] == WorkflowStatus.REJECTED.value

    # Subsequent approval rejected with 409
    dup_resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-REJECT-001/approve",
        json={"reviewer_identity": "Pratik Bhuwad - CMO Product Owner"},
        headers=auth_headers
    )
    assert dup_resp.status_code == 409


# -----------------------------------------------------------------------------
# 7. Replay and Retrieval Tests
# -----------------------------------------------------------------------------
def test_replay_and_retrieval(api_client, auth_headers):
    """Verify replay deterministic execution and audit queries."""
    # Get by ID
    get_resp = api_client.get("/api/v1/proposals/REQ-MKT-TEST-LINKEDIN-001", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["request_id"] == "REQ-MKT-TEST-LINKEDIN-001"

    # List all
    list_resp = api_client.get("/api/v1/proposals", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 3

    # Replay
    replay_resp = api_client.post(
        "/api/v1/proposals/REQ-MKT-TEST-LINKEDIN-001/replay",
        headers=auth_headers
    )
    assert replay_resp.status_code == 200
    assert replay_resp.json()["request_id"] == "REQ-MKT-TEST-LINKEDIN-001"


# -----------------------------------------------------------------------------
# 8. MASTERDB Adapter Offline Fallback Tests
# -----------------------------------------------------------------------------
def test_masterdb_persistence_adapter_graceful_offline():
    """Verify adapter handles offline MasterDB smoothly without exceptions."""
    adapter = MasterDBPersistenceAdapter(base_url="http://127.0.0.1:9999")
    status_info = adapter.check_connection()
    assert status_info["connected"] is False
    assert status_info["status"] == "LOCAL_STORE_FALLBACK"

    # Governed retrieve offline fallback
    retrieval = adapter.fetch_marketing_intelligence()
    assert retrieval["status"] == "OFFLINE_FALLBACK"
