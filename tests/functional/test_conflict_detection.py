"""Functional tests for conflict detection and contradiction analysis."""
import pytest
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.schemas import ResponseStatus


def test_conflict_detection_doc009_vs_doc020(indexed_pipeline):
    query = "What is the default production top-k parameter and candidate pool size for the retrieval service?"
    response = indexed_pipeline.query(query)

    assert response.status == ResponseStatus.CONFLICT_DETECTED
    assert "CONFLICT DETECTED" in response.answer
    assert response.conflicting_evidence is not None
    assert "DOC-009" in response.conflicting_evidence.conflicting_sources
    assert "DOC-020" in response.conflicting_evidence.conflicting_sources
    assert len(response.conflicting_evidence.items) == 2


def test_non_conflicting_query_does_not_trigger_conflict(indexed_pipeline):
    query = "What character encoding is mandatory for all incoming documents in AegisCore?"
    response = indexed_pipeline.query(query)

    assert response.status == ResponseStatus.ANSWERED
    assert response.conflicting_evidence is None
