# Rupam Patne Handover — WP3 RAG Quality Evaluation Summary

**Canonical Reference:** See the comprehensive technical report at [03_rag_evaluation.md](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/03_rag_evaluation.md)  
**Governing Authority / CMO Product Owner:** Prateek  
**Author:** Rupam Patne (CMO Agent Engineering Lead)  
**Status:** WP3 Complete — 100% Status Accuracy, 100% Citation Validity, DEFECT-SEMANTIC-001 Certified  
**Date:** November 14, 2026  

---

## Key Measured Results

1. **Benchmark Suite A (25 Canonical System Queries):**
   - **Retrieval Success Rate:** 94.7% (18/19 applicable queries retrieved expected sources).
   - **Status Accuracy:** 100.0% (25/25 status match).
   - **Failure Detection Rate:** 100.0% (8/8 negative cases correctly flagged).
   - **Citation Validity Rate:** 100.0% (45/45 citations strictly valid).
   - **Average Query Latency:** 10.0 ms.

2. **Benchmark Suite B (10 Targeted CMO Marketing & Workflow Queries):**
   - **Budget Ceilings (`DOC-022`):** Correctly extracted $50,000.00 maximum campaign budget.
   - **Historical Performance (`DOC-023`):** Correctly extracted 2.4% baseline CTR and $29.50 CAC for Paid Search.
   - **Policy Conflict Detection (`DOC-024` vs `DOC-025`):** 100% detection of contradictory influencer spend limits ($25k vs $10k).
   - **Semantic Abstention (`DEFECT-SEMANTIC-001` / Q-MKT-10):** Verified immediate abstention with `INSUFFICIENT_EVIDENCE` and canonical refusal for Linear TV queries.
   - **Workflow Proposal Evaluation:** 
     - $35k compliant proposal -> `APPROVE` recommendation.
     - $75k overspend proposal -> `REJECT` recommendation.
     - $30k Linear TV proposal -> Stage 4 `SUFFICIENCY_FAILED` halt with 0 ungrounded facts.
     - **Human Approval Gate:** 100% preserved; system stops at `AWAITING_APPROVAL`.

3. **Evaluation Evidence Files:**
   - 25-Question Run Data: [benchmark_run_25q.json](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/evaluation_results/benchmark_run_25q.json)
   - 10-Question CMO Marketing Run Data: [cmo_marketing_rag_benchmark.json](file:///c:/Pratik_Bhuwad/CMO_Agent/rupam_handover/evidence/evaluation_results/cmo_marketing_rag_benchmark.json)

WP3 is complete and ready for handoff to **WP4 (Compare all three RAG systems)**.

