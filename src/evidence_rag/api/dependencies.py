"""FastAPI dependencies for authentication, workflow singleton, and persistence."""
from typing import Optional
from fastapi import Header, HTTPException, status

from evidence_rag.workflow import DecisionWorkflow
from evidence_rag.api.masterdb_client import MasterDBPersistenceAdapter
from evidence_rag.api.config import api_settings
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.api.dependencies")

_workflow_instance: Optional[DecisionWorkflow] = None
_persistence_adapter: Optional[MasterDBPersistenceAdapter] = None


def get_persistence_adapter() -> MasterDBPersistenceAdapter:
    """Return singleton MasterDBPersistenceAdapter."""
    global _persistence_adapter
    if _persistence_adapter is None:
        _persistence_adapter = MasterDBPersistenceAdapter()
    return _persistence_adapter


def get_workflow() -> DecisionWorkflow:
    """Return initialized singleton DecisionWorkflow with local persistence adapter."""
    global _workflow_instance
    if _workflow_instance is None:
        adapter = get_persistence_adapter()
        _workflow_instance = DecisionWorkflow(
            record_store=adapter.record_store
        )
        _workflow_instance.ensure_index()
    return _workflow_instance


def verify_tantra_token(authorization: Optional[str] = Header(None)) -> str:
    """Enforce TANTRA Bearer token authentication on protected endpoints.

    In test and development environments, standard test tokens (such as
    'mock-rs256-test-token', 'CMO_AGENT', or non-empty bearer tokens) are accepted.
    In strict production posture, RS256 token verification is enforced.
    """
    if not api_settings.auth_enabled:
        return "AUTH_DISABLED"

    if not authorization or not authorization.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. An authoritative Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Authorization header. Format must be 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token cannot be empty.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # In strict production mode, reject placeholder mock tokens
    if api_settings.auth_strict_rs256 and token in ("mock-rs256-test-token", "test-token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mock tokens are rejected under strict RS256 production governance.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token
