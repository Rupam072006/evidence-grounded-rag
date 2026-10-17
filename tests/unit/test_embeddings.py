"""Unit tests for embedding engines and L2 unit-normalization."""
import numpy as np
import pytest
from evidence_rag.embeddings import HybridTfidfEmbeddingEngine, create_embedding_engine
from evidence_rag.config import EmbeddingConfig


def test_hybrid_tfidf_unit_normalization():
    engine = HybridTfidfEmbeddingEngine(dimension=128)
    texts = [
        "AegisCore distributed intelligence platform.",
        "Vector indexing and cosine similarity calculation.",
        "Deterministic grounded answer generation with citations."
    ]
    engine.fit(texts)
    vectors = engine.encode(texts)

    assert vectors.shape[0] == 3
    assert vectors.shape[1] <= 128
    assert vectors.shape[1] > 0
    # Verify L2 norms are all 1.0 (within float precision)
    norms = np.linalg.norm(vectors, axis=1)
    for norm in norms:
        assert np.isclose(norm, 1.0, atol=1e-5)


def test_encode_query_matches_batch():
    engine = HybridTfidfEmbeddingEngine(dimension=64)
    texts = ["Production retrieval service operates with top-k of 5."]
    engine.fit(texts)

    query = "top-k retrieval service"
    single_vector = engine.encode_query(query)
    batch_vector = engine.encode([query])[0]

    np.testing.assert_allclose(single_vector, batch_vector, atol=1e-6)
    assert np.isclose(np.linalg.norm(single_vector), 1.0, atol=1e-5)


def test_dot_product_is_cosine_similarity():
    engine = HybridTfidfEmbeddingEngine(dimension=64)
    texts = [
        "Authentication credentials and secret key management.",
        "Completely unrelated recipe for baking chocolate cookies."
    ]
    engine.fit(texts)

    v1 = engine.encode_query("secret credentials")
    v2 = engine.encode_query("secret key credentials")
    v3 = engine.encode_query("baking cookies")

    # High similarity between related queries
    sim_related = np.dot(v1, v2)
    # Low similarity between unrelated queries
    sim_unrelated = np.dot(v1, v3)

    assert sim_related > sim_unrelated
    assert 0.0 <= sim_related <= 1.0
    assert 0.0 <= sim_unrelated <= 1.0


def test_factory_creates_configured_engine():
    cfg = EmbeddingConfig(provider="hybrid_tfidf", dimension=256)
    engine = create_embedding_engine(cfg)
    assert isinstance(engine, HybridTfidfEmbeddingEngine)
    assert engine.dimension == 256
