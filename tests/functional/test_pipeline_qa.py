"""Functional tests for end-to-end question answering and structured responses."""
import pytest
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.schemas import ResponseStatus


def test_answerable_question_flow(indexed_pipeline):
    query = "What is the target chunk size and sliding overlap window used by the AegisCore chunker?"
    response = indexed_pipeline.query(query)

    assert response.status == ResponseStatus.ANSWERED
    assert response.confidence > 0.4
    assert len(response.evidence) > 0
    assert "DOC-006" in response.source_document_ids
    assert "400" in response.answer
    assert "60" in response.answer
    assert len(response.citations) > 0
    assert response.citations[0].is_valid is True
    assert response.latency_ms > 0.0


def test_unknown_question_rejection_canonical_refusal(indexed_pipeline):
    query = "What is the secret recipe for baking chocolate cookies?"
    response = indexed_pipeline.query(query)

    assert response.status == ResponseStatus.INSUFFICIENT_EVIDENCE
    assert "INSUFFICIENT EVIDENCE" in response.answer
    assert "The available knowledge base does not contain enough information" in response.answer
    assert len(response.citations) == 0


def test_irrelevant_technical_question(indexed_pipeline):
    query = "How do you configure Kubernetes ingress controllers on AWS EKS with Helm charts?"
    response = indexed_pipeline.query(query)

    assert response.status == ResponseStatus.INSUFFICIENT_EVIDENCE
    assert "INSUFFICIENT EVIDENCE" in response.answer
