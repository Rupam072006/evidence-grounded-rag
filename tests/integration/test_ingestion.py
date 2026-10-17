"""Integration tests for document ingestion, manifest validation, and corpus integrity."""
import json
import pytest
from pathlib import Path
from evidence_rag.ingestion import IngestionEngine
from evidence_rag.schemas import CorpusError
from evidence_rag.config import CorpusConfig


def test_ingestion_loads_exactly_20_documents(project_root):
    engine = IngestionEngine(base_dir=project_root)
    documents = engine.load_corpus()

    assert len(documents) == 20
    # Verify IDs from DOC-001 to DOC-020
    doc_ids = {d.metadata.document_id for d in documents}
    expected_ids = {f"DOC-{i:03d}" for i in range(1, 21)}
    assert doc_ids == expected_ids


def test_ingestion_validates_all_metadata_fields(project_root):
    engine = IngestionEngine(base_dir=project_root)
    documents = engine.load_corpus()

    for doc in documents:
        meta = doc.metadata
        assert meta.document_id.startswith("DOC-")
        assert len(meta.title) > 0
        assert len(meta.source) > 0
        assert len(meta.source_type) > 0
        assert len(meta.version) > 0
        assert len(meta.created_at) > 0
        assert len(meta.updated_at) > 0
        assert len(meta.topic) > 0
        assert len(doc.content_hash) == 64  # SHA-256


def test_ingestion_fails_on_missing_manifest(temp_dir):
    engine = IngestionEngine(base_dir=temp_dir)
    with pytest.raises(CorpusError, match="manifest not found"):
        engine.load_corpus()


def test_ingestion_fails_on_count_mismatch(temp_dir):
    # Create manifest with only 1 document when 20 are required
    manifest_data = {
        "manifest_version": "1.0",
        "total_documents": 1,
        "documents": [
            {
                "document_id": "DOC-001",
                "title": "Solo Doc",
                "source": "data/documents/solo.md",
                "source_type": "spec",
                "version": "1.0.0",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "topic": "Solo"
            }
        ]
    }
    manifest_path = temp_dir / "data" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    engine = IngestionEngine(base_dir=temp_dir)
    with pytest.raises(CorpusError, match="Expected exactly 20 documents"):
        engine.load_corpus()
