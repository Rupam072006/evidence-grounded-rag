"""Boundary tests for missing or corrupt index files."""
import pytest
from evidence_rag.indexing import VectorIndex
from evidence_rag.schemas import IndexNotFoundError


def test_corrupt_index_manifest_handling(temp_dir):
    # Create invalid non-JSON file
    bad_manifest = temp_dir / "knowledge_index.json"
    with open(bad_manifest, "w", encoding="utf-8") as f:
        f.write("NOT_A_VALID_JSON{")

    vectors_file = temp_dir / "vectors.npy"
    with open(vectors_file, "wb") as f:
        f.write(b"fake_bytes")

    with pytest.raises(IndexNotFoundError):
        VectorIndex.load(str(temp_dir))
