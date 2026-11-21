"""Knowledge QA query route wrapping evidence-grounded retrieval and generation."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from evidence_rag.api.schemas import KnowledgeQueryRequest, KnowledgeQueryResponse
from evidence_rag.api.dependencies import get_workflow, verify_tantra_token
from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.api.routes.query")

router = APIRouter(tags=["Knowledge QA"])


@router.post("/query", response_model=KnowledgeQueryResponse)
def query_knowledge_base(
    req: KnowledgeQueryRequest,
    workflow: DecisionWorkflow = Depends(get_workflow),
    token: str = Depends(verify_tantra_token)
) -> KnowledgeQueryResponse:
    """Ask an informational policy, benchmark, or marketing question without creating a proposal."""
    trace_id = f"TRC-QRY-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    try:
        response = workflow.ask_policy_question(req.query)
        citations_data = [c.model_dump() for c in response.citations]
        evidence_data = [
            {
                "chunk_id": rc.chunk.chunk_id,
                "document_id": rc.chunk.document_id,
                "score": rc.score,
                "rank": rc.rank,
                "text": rc.chunk.text
            }
            for rc in response.evidence[: (req.top_k or 5)]
        ]

        return KnowledgeQueryResponse(
            query=req.query,
            answer=response.answer,
            confidence=response.confidence,
            citations=citations_data,
            evidence=evidence_data,
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"Error handling query request: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")
