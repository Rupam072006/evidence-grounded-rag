"""Boundary tests for input query validation, length ceilings, and malformed characters."""
import pytest
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.schemas import ResponseStatus


def test_empty_query_rejected(indexed_pipeline):
    response = indexed_pipeline.query("")
    assert response.status == ResponseStatus.INVALID_INPUT
    assert "INVALID INPUT" in response.answer


def test_whitespace_only_query_rejected(indexed_pipeline):
    response = indexed_pipeline.query("     \n\t   ")
    assert response.status == ResponseStatus.INVALID_INPUT
    assert "INVALID INPUT" in response.answer


def test_short_query_rejected(indexed_pipeline):
    response = indexed_pipeline.query("ab")
    assert response.status == ResponseStatus.INVALID_INPUT
    assert "at least 3 non-whitespace characters" in response.answer


def test_very_long_query_rejected(indexed_pipeline):
    long_query = "x" * 501
    response = indexed_pipeline.query(long_query)
    assert response.status == ResponseStatus.INVALID_INPUT
    assert "exceeds maximum allowed length" in response.answer


def test_disallowed_control_characters_rejected(indexed_pipeline):
    malformed = "Valid query\x00with null byte"
    response = indexed_pipeline.query(malformed)
    assert response.status == ResponseStatus.INVALID_INPUT
    assert "control characters" in response.answer
