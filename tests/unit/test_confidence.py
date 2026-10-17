"""Unit tests for confidence calculation and uncertainty documentation."""
import pytest
from evidence_rag.confidence import ConfidenceScorer
from evidence_rag.schemas import RetrievedChunk, Chunk


def test_confidence_calculation_within_bounds():
    scorer = ConfidenceScorer()
    dummy_chunk = Chunk(
        chunk_id="DOC-001-C001",
        document_id="DOC-001",
        chunk_index=0,
        text="AegisCore architecture specifies 99.95% uptime SLA."
    )
    retrieved = [
        RetrievedChunk(chunk=dummy_chunk, score=0.85, rank=1, raw_similarity=0.85),
        RetrievedChunk(chunk=dummy_chunk, score=0.75, rank=2, raw_similarity=0.75),
    ]

    confidence, limitations = scorer.calculate_confidence("uptime SLA architecture", retrieved)

    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5
    assert len(limitations) >= 1
    assert "not a calibrated Bayesian posterior probability" in limitations[0]


def test_confidence_zero_on_empty_evidence():
    scorer = ConfidenceScorer()
    confidence, limitations = scorer.calculate_confidence("anything", [])
    assert confidence == 0.0
    assert any("Zero evidence" in l for l in limitations)
