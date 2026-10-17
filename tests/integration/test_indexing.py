"""Integration tests for index creation, disk persistence, and reload."""
import pytest
from pathlib import Path
from evidence_rag.chunking import Chunker
from evidence_rag.embeddings import HybridTfidfEmbeddingEngine
from evidence_rag.indexing import VectorIndex
from evidence_rag.schemas import IndexNotFoundError


def test_index_build_persistence_and_reload(mini_corpus, temp_dir):
    chunker = Chunker()
    chunks = chunker.chunk_corpus(mini_corpus)
    assert len(chunks) >= 2

    engine = HybridTfidfEmbeddingEngine(dimension=128)
    index = VectorIndex.build(chunks, engine, corpus_fingerprint="test_fp")

    # Persist to temp_dir
    index_dir = str(temp_dir / "index")
    index.save(index_dir)

    # Verify files created on disk
    assert (temp_dir / "index" / "vectors.npy").exists()
    assert (temp_dir / "index" / "knowledge_index.json").exists()
    assert (temp_dir / "index" / "embedding_model.pkl").exists()

    # Reload from disk
    loaded_index = VectorIndex.load(index_dir)
    assert len(loaded_index.chunks) == len(chunks)
    assert loaded_index.vectors.shape == index.vectors.shape
    assert loaded_index.metadata["corpus_fingerprint"] == "test_fp"


def test_load_index_missing_raises_error(temp_dir):
    with pytest.raises(IndexNotFoundError):
        VectorIndex.load(str(temp_dir / "non_existent_dir"))
