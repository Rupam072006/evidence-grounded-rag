"""Pytest fixtures for unit, integration, and functional tests."""
import os
import shutil
import tempfile
import pytest
from pathlib import Path

from evidence_rag.config import RAGConfig, load_config
from evidence_rag.schemas import Document, DocumentMetadata, Chunk
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.embeddings import HybridTfidfEmbeddingEngine
from evidence_rag.indexing import VectorIndex


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the absolute path to project root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def force_test_mock_mode(monkeypatch):
    """Enforce deterministic offline mock mode for all tests."""
    monkeypatch.setenv("RAG_GENERATION_MODE", "mock")


@pytest.fixture(scope="session")
def default_config() -> RAGConfig:
    """Load default pipeline configuration."""
    cfg = load_config()
    cfg.generation.mode = "mock"
    return cfg



@pytest.fixture
def temp_dir():
    """Create a clean temporary directory for isolated disk operations."""
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_document() -> Document:
    """Provide a standard Document object for testing."""
    return Document(
        metadata=DocumentMetadata(
            document_id="DOC-999",
            title="Sample Test Specification",
            source="docs/sample.md",
            source_type="technical_specification",
            version="1.0.0",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-02T00:00:00Z",
            topic="Testing"
        ),
        content=(
            "# Sample Test Specification\n\n"
            "The AegisCore testing harness validates pipeline invariants. "
            "It enforces a 400-character target chunk size and strict citation syntax.\n\n"
            "All embedding vectors must maintain unit L2 norm for dot product equivalence."
        ),
        content_hash="abc123hash"
    )


@pytest.fixture
def mini_corpus(sample_document) -> list[Document]:
    """Provide a small list of documents for indexing tests."""
    doc2 = Document(
        metadata=DocumentMetadata(
            document_id="DOC-998",
            title="Operational Guidelines",
            source="docs/operational.md",
            source_type="operational_guideline",
            version="1.0.0",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-02T00:00:00Z",
            topic="Operations"
        ),
        content=(
            "# Operational Guidelines\n\n"
            "The default top-k parameter is set to 5 for production retrieval queries. "
            "Candidate pool size is capped at 20 items to preserve low latency."
        ),
        content_hash="def456hash"
    )
    return [sample_document, doc2]


@pytest.fixture
def indexed_pipeline(project_root) -> RAGPipeline:
    """Provide an initialized pipeline with index ready."""
    pipeline = RAGPipeline(base_dir=project_root)
    pipeline.ensure_index()
    return pipeline
