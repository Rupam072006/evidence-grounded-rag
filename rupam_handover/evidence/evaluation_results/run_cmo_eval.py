import json
import time
from pathlib import Path
from datetime import datetime, timezone

from evidence_rag.config import load_config
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus
from evidence_rag.schemas import ResponseStatus
from evidence_rag.record_store import RecordStore

def main():
    repo_root = Path("c:/Pratik_Bhuwad/CMO_Agent/evidence-grounded-rag-main")
    cfg = load_config(repo_root / "configs/default.yaml")
    pipeline = RAGPipeline(config=cfg, base_dir=repo_root)
    pipeline.ensure_index()

    test_store_dir = Path("c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/evaluation_results/temp_records")
    test_store_dir.mkdir(parents=True, exist_ok=True)
    store = RecordStore(test_store_dir)
    workflow = DecisionWorkflow(config=cfg, record_store=store, base_dir=repo_root)
    workflow.ensure_index()

    results = []

    # 1. Informational Queries
    queries = [
        {
            "id": "MKT-Q01",
            "name": "Marketing Budget Ceilings",
            "query": "What is the maximum allowable budget allocation for any individual marketing campaign or initiative?",
            "expected_docs": ["DOC-022"],
            "expected_status": "ANSWERED",
            "key_fact": "$50,000.00"
        },
        {
            "id": "MKT-Q02",
            "name": "Historical Performance Metrics CTR & CAC",
            "query": "What are the standard historical performance metrics for Click-Through Rate (CTR) and Customer Acquisition Cost (CAC) across digital campaigns?",
            "expected_docs": ["DOC-023"],
            "expected_status": "ANSWERED",
            "key_fact": "2.4%"
        },
        {
            "id": "MKT-Q03",
            "name": "Channel Specific Baselines (Paid Search)",
            "query": "What are the specific performance baselines for Paid Search including CAC and conversion rate?",
            "expected_docs": ["DOC-023"],
            "expected_status": "ANSWERED",
            "key_fact": "$29.50"
        },
        {
            "id": "MKT-Q04",
            "name": "Cross-Domain: SQL Relational Analysis of Marketing Data",
            "query": "How can relational database SQL queries and schema models be used to analyze marketing campaign conversion metrics?",
            "expected_docs": ["DOC-008", "DOC-023"],
            "expected_status": "ANSWERED",
            "key_fact": "SQL"
        },
        {
            "id": "MKT-Q05",
            "name": "Policy Contradiction: Influencer Spending Ceilings",
            "query": "What conflict exists between the two influencer spending policies regarding spending limits?",
            "expected_docs": ["DOC-024", "DOC-025"],
            "expected_status": "CONFLICT_DETECTED",
            "key_fact": "conflict"
        },
        {
            "id": "MKT-Q06",
            "name": "Semantic Abstention on Unsupported Channel: Linear TV (Q-MKT-10)",
            "query": "What is the benchmark CTR or CAC for Linear TV campaigns?",
            "expected_docs": [],
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "key_fact": "INSUFFICIENT EVIDENCE"
        },
        {
            "id": "MKT-Q07",
            "name": "Negative Control: Out-of-Domain Physical Drilling",
            "query": "What are the safety procedures and operational protocols for deep-sea offshore oil drilling?",
            "expected_docs": [],
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "key_fact": "INSUFFICIENT EVIDENCE"
        }
    ]

    for q in queries:
        t0 = time.perf_counter()
        resp = pipeline.query(q["query"])
        latency = (time.perf_counter() - t0) * 1000

        res_item = {
            "test_id": q["id"],
            "test_name": q["name"],
            "type": "query",
            "query": q["query"],
            "expected_status": q["expected_status"],
            "actual_status": resp.status.value,
            "status_match": resp.status.value == q["expected_status"],
            "expected_docs": q["expected_docs"],
            "retrieved_sources": resp.source_document_ids,
            "retrieval_hit": any(d in resp.source_document_ids for d in q["expected_docs"]) if q["expected_docs"] else len(resp.source_document_ids) == 0,
            "confidence": resp.confidence,
            "citations_count": len(resp.citations),
            "citations_valid": all(c.is_valid for c in resp.citations) if resp.citations else True,
            "answer_snippet": resp.answer[:300],
            "latency_ms": round(latency, 2)
        }
        results.append(res_item)

    # 2. Workflow Decision Proposals
    proposals = [
        {
            "id": "MKT-WF01",
            "name": "Budget Compliant Proposal ($35k Growth Campaign)",
            "request": WorkflowRequest(
                request_id="REQ-EVAL-01",
                title="Q4 Enterprise Growth Initiative",
                proposal_text="Allocate $35,000 across Google search ads and content syndication aiming for 450 conversions with target CTR of 2.4%.",
                department="Marketing",
                requested_budget=35000.0,
                submitted_by="growth_analyst"
            ),
            "expected_status": "AWAITING_APPROVAL",
            "expected_action": "APPROVE"
        },
        {
            "id": "MKT-WF02",
            "name": "Budget Overspend Proposal ($75k Budget Breach)",
            "request": WorkflowRequest(
                request_id="REQ-EVAL-02",
                title="Excessive Budget Marketing Initiative",
                proposal_text="Allocate $75,000 for massive paid search expansion across global territories.",
                department="Marketing",
                requested_budget=75000.0,
                submitted_by="growth_analyst"
            ),
            "expected_status": "AWAITING_APPROVAL",
            "expected_action": "REJECT"
        },
        {
            "id": "MKT-WF03",
            "name": "Unsupported Channel Proposal: Linear TV (DEFECT-SEMANTIC-001)",
            "request": WorkflowRequest(
                request_id="REQ-EVAL-03",
                title="National Linear TV Broadcast Campaign",
                proposal_text="Allocate $30,000 for nationwide Linear TV advertising spots and broadcast commercials.",
                department="Marketing",
                requested_budget=30000.0,
                submitted_by="media_planner"
            ),
            "expected_status": "INSUFFICIENT_EVIDENCE",
            "expected_action": None
        }
    ]

    for p in proposals:
        t0 = time.perf_counter()
        rec = workflow.evaluate_proposal(p["request"])
        latency = (time.perf_counter() - t0) * 1000

        action = rec.recommendation.recommended_action if rec.recommendation else None
        res_item = {
            "test_id": p["id"],
            "test_name": p["name"],
            "type": "workflow_proposal",
            "request_id": p["request"].request_id,
            "title": p["request"].title,
            "requested_budget": p["request"].requested_budget,
            "expected_status": p["expected_status"],
            "actual_status": rec.status.value,
            "status_match": rec.status.value == p["expected_status"],
            "expected_action": p["expected_action"],
            "actual_action": action,
            "action_match": action == p["expected_action"],
            "evidence_chunk_count": len(rec.evidence_set),
            "verified_facts_count": len(rec.recommendation.verified_facts) if rec.recommendation else 0,
            "inferences_count": len(rec.recommendation.inferences) if rec.recommendation else 0,
            "unknowns_count": len(rec.recommendation.unknowns) if rec.recommendation else 0,
            "latency_ms": round(latency, 2),
            "approval_gate_paused": rec.approval is None
        }
        results.append(res_item)

    out_file = Path("c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/evaluation_results/cmo_marketing_rag_benchmark.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_evaluated": len(results),
            "results": results
        }, f, indent=2)

    print(f"Evaluated {len(results)} items successfully. Written to {out_file}")

if __name__ == "__main__":
    main()

