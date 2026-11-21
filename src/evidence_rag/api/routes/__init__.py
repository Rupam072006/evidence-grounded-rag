"""REST Route modules for CMO Agent API."""
from evidence_rag.api.routes.health import router as health_router
from evidence_rag.api.routes.query import router as query_router
from evidence_rag.api.routes.proposals import router as proposals_router

__all__ = ["health_router", "query_router", "proposals_router"]
