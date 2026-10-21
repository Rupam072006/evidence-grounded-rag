"""Functional tests for citation extraction and validity auditing."""
import pytest
from evidence_rag.evidence import CitationValidator
from evidence_rag.schemas import RetrievedChunk, Chunk


def test_valid_citation_verification():
    validator = CitationValidator()
    chunk = Chunk(
        chunk_id="DOC-001-C001",
        document_id="DOC-001",
        chunk_index=0,
        text="AegisCore architecture specifies 99.95% uptime SLA."
    )
    retrieved = [RetrievedChunk(chunk=chunk, score=0.8, rank=1, raw_similarity=0.8)]

    answer = "The platform delivers 99.95% uptime SLA [DOC-001:DOC-001-C001]."
    citations = validator.validate_citations(answer, retrieved)

    assert len(citations) == 1
    assert citations[0].document_id == "DOC-001"
    assert citations[0].chunk_id == "DOC-001-C001"
    assert citations[0].is_valid is True


def test_invented_citation_rejected():
    validator = CitationValidator()
    chunk = Chunk(
        chunk_id="DOC-001-C001",
        document_id="DOC-001",
        chunk_index=0,
        text="AegisCore architecture specifies 99.95% uptime SLA."
    )
    retrieved = [RetrievedChunk(chunk=chunk, score=0.8, rank=1, raw_similarity=0.8)]

    # Answer cites DOC-099 which was never retrieved
    answer = "Hallucinated statement [DOC-099:DOC-099-C001]."
    citations = validator.validate_citations(answer, retrieved)

    assert len(citations) == 1
    assert citations[0].document_id == "DOC-099"
    assert citations[0].is_valid is False
    assert "was not in retrieved context" in citations[0].validation_reason


def test_alternate_citation_delimiters():
    """Verify that both hyphen delimiters and lenticular unicode brackets are correctly parsed."""
    validator = CitationValidator()
    chunk = Chunk(
        chunk_id="DOC-006-C007",
        document_id="DOC-006",
        chunk_index=7,
        text="The chunk size target is 400 chars."
    )
    retrieved = [RetrievedChunk(chunk=chunk, score=0.85, rank=1, raw_similarity=0.85)]

    # Test hyphen delimiter [DOC-006-C007]
    ans1 = "Target chunk size is 400 chars [DOC-006-C007]."
    cits1 = validator.validate_citations(ans1, retrieved)
    assert len(cits1) == 1
    assert cits1[0].chunk_id == "DOC-006-C007"
    assert cits1[0].is_valid is True

    # Test unicode lenticular bracket 【DOC-006-C007】
    ans2 = "Target chunk size is 400 chars 【DOC-006-C007】."
    cits2 = validator.validate_citations(ans2, retrieved)
    assert len(cits2) == 1
    assert cits2[0].chunk_id == "DOC-006-C007"
    assert cits2[0].is_valid is True
