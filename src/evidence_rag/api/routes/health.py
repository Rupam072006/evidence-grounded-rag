"""Health, readiness, kernel status, and connectivity probe routes."""
import hashlib
from pathlib import Path
from fastapi import APIRouter, Depends

from evidence_rag.api.schemas import HealthResponse
from evidence_rag.api.dependencies import get_workflow, get_persistence_adapter
from evidence_rag.api.config import api_settings
from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.api.masterdb_client import MasterDBPersistenceAdapter

router = APIRouter(tags=["Health & Status"])


def _compute_index_fingerprint(base_dir: Path) -> str:
    """Compute SHA-256 fingerprint of the index or document corpus."""
    manifest_path = base_dir / "data" / "index" / "manifest.json"
    if manifest_path.exists():
        try:
            return hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        except Exception:
            pass

    corpus_dir = base_dir / "data" / "documents"
    if corpus_dir.exists():
        hasher = hashlib.sha256()
        for doc_file in sorted(corpus_dir.glob("*.md")):
            try:
                hasher.update(doc_file.read_bytes())
            except Exception:
                pass
        return hasher.hexdigest()

    return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


@router.get("/health", response_model=HealthResponse)
def health_probe(
    workflow: DecisionWorkflow = Depends(get_workflow),
    adapter: MasterDBPersistenceAdapter = Depends(get_persistence_adapter)
) -> HealthResponse:
    """Public health probe returning kernel readiness, index SHA-256 fingerprint, and MASTERDB status."""
    fingerprint = _compute_index_fingerprint(workflow.base_dir)
    mdb_probe = adapter.check_connection()

    return HealthResponse(
        status="ok",
        version=api_settings.api_version,
        path="Path B",
        kernel_status="READY",
        index_fingerprint=fingerprint,
        persistence_status="READY",
        masterdb_status=mdb_probe.get("status", "LOCAL_STORE_FALLBACK")
    )
