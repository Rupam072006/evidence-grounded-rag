"""Unit tests for schemas, data models, and exception types."""
import pytest
from pydantic import ValidationError
from evidence_rag.schemas import (
    ResponseStatus,
    DocumentMetadata,
    Chunk,
    RAGResponse,
    RAGException,
    CorpusError,
    IndexNotFoundError,
    RetrievalError,
    InputValidationError
)


def test_response_statuses_complete():
    expected = {
        "ANSWERED",
        "INSUFFICIENT_EVIDENCE",
        "CONFLICT_DETECTED",
        "INVALID_INPUT",
        "GENERATION_UNAVAILABLE"
    }
    actual = {s.value for s in ResponseStatus}
    assert expected == actual


def test_document_metadata_validation():
    valid_data = {
        "document_id": "DOC-001",
        "title": "Valid Title",
        "source": "docs/test.md",
        "source_type": "technical_specification",
        "version": "1.0.0",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-02T00:00:00Z",
        "topic": "Testing"
    }
    meta = DocumentMetadata(**valid_data)
    assert meta.document_id == "DOC-001"

    # Missing required field triggers ValidationError
    invalid_data = valid_data.copy()
    del invalid_data["title"]
    with pytest.raises(ValidationError):
        DocumentMetadata(**invalid_data)


def test_exception_hierarchy():
    assert issubclass(CorpusError, RAGException)
    assert issubclass(IndexNotFoundError, RAGException)
    assert issubclass(RetrievalError, RAGException)
    assert issubclass(InputValidationError, RAGException)
