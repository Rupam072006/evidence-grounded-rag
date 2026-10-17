"""Integration tests for retrieval relevance, top-k behavior, and source traceability."""
import pytest
from evidence_rag.retrieval import Retriever
from evidence_rag.config import RetrievalConfig


def test_retrieval_relevance_and_top_k(indexed_pipeline):
    retriever = Retriever(indexed_pipeline.index, RetrievalConfig(top_k=3))
    query = "What character encoding is mandatory for all incoming documents in AegisCore?"
    results = retriever.retrieve(query, top_k=3)

    assert len(results) > 0
    assert len(results) <= 3

    top_chunk = results[0].chunk
    # Expect DOC-004 (Document Processing & Extraction, specifies UTF-8)
    assert top_chunk.document_id == "DOC-004"
    assert "utf-8" in top_chunk.text.lower()
    assert results[0].rank == 1
    assert results[0].score >= 0.25


def test_retrieval_traceability(indexed_pipeline):
    retriever = Retriever(indexed_pipeline.index)
    results = retriever.retrieve("SHA-256 cryptographic hashing provenance", top_k=2)

    assert len(results) > 0
    for r in results:
        # Full traceability from chunk to parent document metadata
        assert r.chunk.document_id.startswith("DOC-")
        assert r.chunk.chunk_id.startswith(r.chunk.document_id)
        assert "title" in r.chunk.metadata
        assert "source" in r.chunk.metadata
