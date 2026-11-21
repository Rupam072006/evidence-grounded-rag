"""FastAPI application factory for the CMO Agent Path B microservice."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from evidence_rag.api.config import api_settings
from evidence_rag.api.routes import health_router, query_router, proposals_router
from evidence_rag.api.dependencies import get_workflow
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.api.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to warm up RAG indices and dependencies."""
    logger.info("Initializing CMO Agent Path B microservice lifespan...")
    try:
        wf = get_workflow()
        wf.ensure_index()
        logger.info("Knowledge index successfully verified and loaded.")
    except Exception as e:
        logger.warning(f"Index warm-up encountered non-fatal notice: {e}")
    yield
    logger.info("Shutting down CMO Agent Path B microservice.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=api_settings.api_title,
        version=api_settings.api_version,
        description=(
            "Path B Stateless REST Microservice for Evidence-Grounded Marketing Intelligence, "
            "Policy Retrieval, and Human-in-the-Loop Proposal Governance."
        ),
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers under root path
    app.include_router(health_router)
    app.include_router(query_router)
    app.include_router(proposals_router)

    # Mount routers under /api/v1 prefix as canonical API version
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(query_router, prefix="/api/v1")
    app.include_router(proposals_router, prefix="/api/v1")

    # Global exception handler for ValueError
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        msg = str(exc)
        status_code = 409 if "already finalized" in msg.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content={"detail": msg, "error_code": "VALUE_ERROR"}
        )

    return app


app = create_app()
