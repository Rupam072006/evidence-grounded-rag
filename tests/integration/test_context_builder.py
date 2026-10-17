"""Integration tests for context construction and token budgeting."""
import pytest
from evidence_rag.context_builder import ContextBuilder
from evidence_rag.schemas import RetrievedChunk, Chunk


def test_context_construction_boundaries():
    builder = ContextBuilder(max_chars=2000)
    chunk = Chunk(
        chunk_id="DOC-001-C001",
        document_id="DOC-001",
        chunk_index=0,
        text="AegisCore architecture specifies 99.95% uptime SLA."
    )
    retrieved = [RetrievedChunk(chunk=chunk, score=0.8, rank=1, raw_similarity=0.8)]

    context_str, chunk_ids = builder.build_context(retrieved)

    assert "=== PASSAGE [DOC-001-C001]" in context_str
    assert "=== END PASSAGE ===" in context_str
    assert "99.95% uptime SLA" in context_str
    assert chunk_ids == ["DOC-001-C001"]


def test_context_budget_capping():
    builder = ContextBuilder(max_chars=120)
    chunk1 = Chunk(
        chunk_id="DOC-001-C001",
        document_id="DOC-001",
        chunk_index=0,
        text="First passage content."
    )
    chunk2 = Chunk(
        chunk_id="DOC-002-C001",
        document_id="DOC-002",
        chunk_index=0,
        text="Second passage content that should be excluded due to budget."
    )
    retrieved = [
        RetrievedChunk(chunk=chunk1, score=0.9, rank=1, raw_similarity=0.9),
        RetrievedChunk(chunk=chunk2, score=0.8, rank=2, raw_similarity=0.8),
    ]

    context_str, chunk_ids = builder.build_context(retrieved)
    assert len(chunk_ids) == 1
    assert chunk_ids[0] == "DOC-001-C001"
