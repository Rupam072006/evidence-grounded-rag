"""Boundary tests for empty knowledge base conditions."""
import pytest
from evidence_rag.indexing import VectorIndex
from evidence_rag.embeddings import HybridTfidfEmbeddingEngine
from evidence_rag.retrieval import Retriever
from evidence_rag.config import RetrievalConfig


def test_empty_vector_index_search():
    engine = HybridTfidfEmbeddingEngine(dimension=32)
    # Empty index
    index = VectorIndex(chunks=[], vectors=engine.encode([]), embedding_engine=engine)
    retriever = Retriever(index, RetrievalConfig())

    results = retriever.retrieve("Any query here")
    assert results == []
    assert retriever.assess_evidence_sufficiency(results) is False
