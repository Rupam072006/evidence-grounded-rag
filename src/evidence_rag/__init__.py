"""Evidence-Grounded RAG System.

A reliable, reproducible, evidence-grounded Retrieval-Augmented Generation system.
"""

__version__ = "1.0.0"
__author__ = "Rupam Patne"

from evidence_rag.pipeline import RAGPipeline
from evidence_rag.config import RAGConfig, load_config
from evidence_rag.schemas import (
    RAGResponse,
    ResponseStatus,
    Citation,
    RetrievedChunk,
    DocumentMetadata,
)

__all__ = [
    "RAGPipeline",
    "RAGConfig",
    "load_config",
    "RAGResponse",
    "ResponseStatus",
    "Citation",
    "RetrievedChunk",
    "DocumentMetadata",
]
