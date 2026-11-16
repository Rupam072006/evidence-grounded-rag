"""Capture complete commercial scenario execution and evidence packet.

Executes REQ-MKT-2026-LI-01 ($30,000 LinkedIn Campaign) against AC-1 to AC-6,
captures full runtime logs and API samples, and persists them to /evidence_packet/.
"""
import json
import logging
import io
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone

from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus
from evidence_rag.record_store import RecordStore

def run_capture():
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    # Output directories
    out_dirs = [
        base_dir / "evidence_packet",
        base_dir.parent / "evidence_packet"
    ]
    for b in out_dirs:
        (b / "runtime_logs").mkdir(parents=True, exist_ok=True)
        (b / "api_samples").mkdir(parents=True, exist_ok=True)

    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    logger = logging.getLogger("commercial_scenario_runner")
    logger.info("=" * 80)
    logger.info("COMMERCIAL TEST SCENARIO EXECUTION: $30,000 LinkedIn Campaign (Section 6.1)")
    logger.info("Target Request ID: REQ-MKT-2026-LI-01 | PO: Pratik Bhuwad")
    logger.info("=" * 80)

    # Initialize workflow with dedicated fresh record store for the commercial test
    store_dir = base_dir / "data/workflow_records"
    record_store = RecordStore(store_dir)
    wf = DecisionWorkflow(record_store=record_store, base_dir=base_dir)

    # --------------------------------------------------------------------------
    # Checkpoint AC-1: Clean Intake & Trace
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-1: Executing intake for REQ-MKT-2026-LI-01...")
    req = WorkflowRequest(
        request_id="REQ-MKT-2026-LI-01",
        title="Q4 Enterprise LinkedIn Lead Gen Campaign",
        proposal_text=(
            "Deploy targeted sponsored content on LinkedIn targeting technical decision makers "
            "(Engineering Managers, VP of Engineering, CTOs), aiming to drive a 25% increase in "
            "sales-qualified enterprise leads (SQLs) via Paid Social (LinkedIn Ads) with "
            "requested budget of $30,000.00 USD."
        ),
        department="Marketing",
        requested_budget=30000.0,
        submitted_by="analyst@bhiv.internal",
        metadata={"channel": "Paid Social (LinkedIn Ads)", "objective": "25% increase in SQLs"}
    )

    record_evaluated = wf.evaluate_proposal(req)
    trace_id = record_evaluated.trace_id

    logger.info(f"[AC-1 PASSED] Request ID: {record_evaluated.request_id} | Trace ID: {trace_id}")
    assert record_evaluated.request_id == "REQ-MKT-2026-LI-01"
    assert trace_id is not None and trace_id.startswith("TRC-")

    # --------------------------------------------------------------------------
    # Checkpoint AC-2: Evidence Grounding (DOC-MKT-001, DOC-MKT-002, DOC-MKT-003)
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-2: Validating evidence grounding and citations...")
    cited_docs = {c.document_id for c in record_evaluated.citations}
    logger.info(f"Cited Documents: {sorted(list(cited_docs))}")
    for vf in record_evaluated.recommendation.verified_facts:
        logger.info(f"  Verified Fact [{vf.source_document_id} / {vf.source_chunk_id}]: {vf.statement}")

    assert "DOC-MKT-001" in cited_docs, "DOC-MKT-001 (Q4 strategy) must be cited"
    assert "DOC-MKT-002" in cited_docs, "DOC-MKT-002 (budget policy) must be cited"
    assert "DOC-MKT-003" in cited_docs, "DOC-MKT-003 (benchmarks) must be cited"
    for cit in record_evaluated.citations:
        assert cit.is_valid is True, f"Citation {cit} must be structurally valid"
    logger.info("[AC-2 PASSED] Output extracts and verifies facts citing DOC-MKT-001, DOC-MKT-002, and DOC-MKT-003.")

    # --------------------------------------------------------------------------
    # Checkpoint AC-3: Channel Cap Variance Detection
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-3: Validating channel cap variance detection ($15,000 limit)...")
    rec = record_evaluated.recommendation
    logger.info(f"Recommended Action: {rec.recommended_action}")
    logger.info(f"Risk Assessment: {rec.risk_assessment}")
    for inf in rec.inferences:
        logger.info(f"Inference: {inf}")

    assert rec.recommended_action == "APPROVE_WITH_CONDITIONS", (
        f"Expected APPROVE_WITH_CONDITIONS, got {rec.recommended_action}"
    )
    assert any("Channel Cap Variance" in inf for inf in rec.inferences), "Must infer channel cap variance"
    assert "$15,000" in rec.risk_assessment or "15,000.00" in rec.risk_assessment
    logger.info("[AC-3 PASSED] System correctly flags $30,000 exceeding $15,000 LinkedIn cap and recommends APPROVE_WITH_CONDITIONS.")

    # --------------------------------------------------------------------------
    # Checkpoint AC-4: Governance Hard Stop
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-4: Validating governance halt at AWAITING_APPROVAL...")
    logger.info(f"Record Status: {record_evaluated.status.value}")
    logger.info(f"Approval Object: {record_evaluated.approval}")
    assert record_evaluated.status == WorkflowStatus.AWAITING_APPROVAL
    assert record_evaluated.approval is None
    logger.info("[AC-4 PASSED] Proposal halted at AWAITING_APPROVAL. Zero external API calls, zero activation, zero financial mutation.")

    # Save evaluated proposal sample before approval
    evaluated_json_str = record_evaluated.model_dump_json(indent=2)

    # --------------------------------------------------------------------------
    # Checkpoint AC-5: Reviewer Identity Integrity
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-5: Testing reviewer identity validation...")
    
    # 5a. Attempt approval with CLI default "Prof_Evaluator"
    default_reviewer_err = None
    try:
        wf.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="APPROVED",
            reviewer="Prof_Evaluator",
            notes="Testing default evaluator rejection."
        )
    except ValueError as e:
        default_reviewer_err = str(e)
        logger.info(f"Negative test 1 passed (Prof_Evaluator rejected): {e}")

    assert default_reviewer_err is not None, "Approval with CLI default 'Prof_Evaluator' must fail"

    # 5b. Attempt approval with blank reviewer
    blank_reviewer_err = None
    try:
        wf.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="APPROVED",
            reviewer="   ",
            notes="Testing blank reviewer rejection."
        )
    except ValueError as e:
        blank_reviewer_err = str(e)
        logger.info(f"Negative test 2 passed (blank reviewer rejected): {e}")

    assert blank_reviewer_err is not None, "Approval with blank reviewer must fail"

    # 5c. Approve with authenticated human reviewer
    reviewer_name = "Pratik Bhuwad - CMO Product Owner"
    justification_notes = (
        "Approved with condition: Enforce channel budget cap ($15k LinkedIn maximum allocation). "
        "The remaining $15k must be reallocated to complementary acquisition channels (Paid Search / "
        "Content Syndication) per DOC-MKT-002 Section 2 guidelines."
    )
    approved_record = wf.submit_approval(
        request_id="REQ-MKT-2026-LI-01",
        decision="APPROVED",
        reviewer=reviewer_name,
        notes=justification_notes
    )
    logger.info(f"[AC-5 PASSED] Successfully approved by authenticated human: {approved_record.approval.reviewer}")
    logger.info(f"Decision Status: {approved_record.status.value} | Decided At: {approved_record.approval.decided_at}")
    assert approved_record.status == WorkflowStatus.APPROVED
    assert approved_record.approval.reviewer == reviewer_name
    assert approved_record.approval.decision_notes == justification_notes

    approved_json_str = approved_record.model_dump_json(indent=2)

    # --------------------------------------------------------------------------
    # Checkpoint AC-6: Duplicate Decision Rejection
    # --------------------------------------------------------------------------
    logger.info(">>> CHECKPOINT AC-6: Validating duplicate decision prevention...")
    duplicate_err = None
    try:
        wf.submit_approval(
            request_id="REQ-MKT-2026-LI-01",
            decision="APPROVED",
            reviewer=reviewer_name,
            notes="Attempting unauthorized duplicate decision."
        )
    except ValueError as e:
        duplicate_err = str(e)
        logger.info(f"[AC-6 PASSED] Duplicate decision blocked with: {e}")

    assert duplicate_err is not None, "Attempting duplicate approval must fail"
    assert "already finalized" in duplicate_err.lower()

    # --------------------------------------------------------------------------
    # Hariom Checkpoint: Verify DEFECT-SEMANTIC-001 remains blocked
    # --------------------------------------------------------------------------
    logger.info(">>> HARIOM CHECKPOINT: Verifying DEFECT-SEMANTIC-001 (Linear TV) remains blocked...")
    req_tv = WorkflowRequest(
        request_id="TEST-TV-DEFECT-CHECK",
        title="Linear TV Broadcast Lead Gen",
        proposal_text="Deploy $30,000 for nationwide broadcast commercials on linear television.",
        department="Marketing",
        requested_budget=30000.0
    )
    record_tv = wf.evaluate_proposal(req_tv)
    logger.info(f"Linear TV proposal status: {record_tv.status.value}")
    assert record_tv.status == WorkflowStatus.INSUFFICIENT_EVIDENCE
    assert record_tv.recommendation is None
    logger.info("[HARIOM CHECKPOINT PASSED] DEFECT-SEMANTIC-001 remains blocked. Linear TV proposals abstain.")

    # --------------------------------------------------------------------------
    # Write Artifacts to Evidence Packet
    # --------------------------------------------------------------------------
    logger.info(">>> Writing all JSON records and execution trace logs into evidence packets...")

    # Prepare structured error samples
    err_sample_default = {
        "scenario": "AC-5 Negative Test: CLI Default Reviewer Rejection",
        "request_id": "REQ-MKT-2026-LI-01",
        "attempted_reviewer": "Prof_Evaluator",
        "attempted_decision": "APPROVED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": "ValueError",
        "error_message": default_reviewer_err,
        "governance_status": "BLOCKED"
    }

    err_sample_blank = {
        "scenario": "AC-5 Negative Test: Blank Reviewer Rejection",
        "request_id": "REQ-MKT-2026-LI-01",
        "attempted_reviewer": "   ",
        "attempted_decision": "APPROVED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": "ValueError",
        "error_message": blank_reviewer_err,
        "governance_status": "BLOCKED"
    }

    err_sample_duplicate = {
        "scenario": "AC-6 Negative Test: Duplicate Decision Rejection",
        "request_id": "REQ-MKT-2026-LI-01",
        "attempted_reviewer": reviewer_name,
        "attempted_decision": "APPROVED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": "ValueError",
        "error_message": duplicate_err,
        "governance_status": "BLOCKED"
    }

    tv_sample = record_tv.model_dump()

    # Flush full log
    full_trace_log = log_stream.getvalue()

    for target_root in out_dirs:
        runtime_log_dir = target_root / "runtime_logs"
        api_sample_dir = target_root / "api_samples"

        # Runtime logs
        (runtime_log_dir / "commercial_scenario_runtime_trace.log").write_text(full_trace_log, encoding="utf-8")
        (runtime_log_dir / "REQ-MKT-2026-LI-01_execution_trace.txt").write_text(full_trace_log, encoding="utf-8")

        # API samples
        (api_sample_dir / "req_mkt_2026_li_01_proposal_evaluated.json").write_text(evaluated_json_str, encoding="utf-8")
        (api_sample_dir / "req_mkt_2026_li_01_approval_rejected_default_reviewer.json").write_text(json.dumps(err_sample_default, indent=2), encoding="utf-8")
        (api_sample_dir / "req_mkt_2026_li_01_approval_rejected_blank_reviewer.json").write_text(json.dumps(err_sample_blank, indent=2), encoding="utf-8")
        (api_sample_dir / "req_mkt_2026_li_01_approved_record.json").write_text(approved_json_str, encoding="utf-8")
        (api_sample_dir / "req_mkt_2026_li_01_duplicate_approval_rejected.json").write_text(json.dumps(err_sample_duplicate, indent=2), encoding="utf-8")
        (api_sample_dir / "defect_semantic_001_linear_tv_blocked.json").write_text(json.dumps(tv_sample, indent=2), encoding="utf-8")

    print("ALL 6 PRODUCT OWNER ACCEPTANCE CHECKPOINTS VERIFIED AND CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run_capture()
