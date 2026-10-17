"""Data models, enums, and exception hierarchy for Evidence-Grounded RAG."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Execution status of the RAG pipeline."""
    ANSWERED = "ANSWERED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    INVALID_INPUT = "INVALID_INPUT"
    GENERATION_UNAVAILABLE = "GENERATION_UNAVAILABLE"


class DocumentMetadata(BaseModel):
    """Metadata schema for a knowledge base document."""
    document_id: str = Field(..., description="Stable unique ID, e.g. DOC-001")
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Relative filesystem path")
    source_type: str = Field(..., description="Category of documentation")
    version: str = Field(..., description="Semantic version string")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 update timestamp")
    topic: str = Field(..., description="Primary topic or subject matter")


class Document(BaseModel):
    """In-memory representation of an ingested document."""
    metadata: DocumentMetadata
    content: str
    content_hash: str


class Chunk(BaseModel):
    """Text chunk generated from a source document."""
    chunk_id: str = Field(..., description="Unique chunk ID, e.g. DOC-001-C001")
    document_id: str = Field(..., description="Parent document ID")
    chunk_index: int = Field(..., description="0-indexed position within document")
    text: str = Field(..., description="Cleaned chunk text")
    char_start: int = Field(default=0)
    char_end: int = Field(default=0)
    token_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """A chunk retrieved by the similarity engine with ranking scores."""
    chunk: Chunk
    score: float = Field(..., description="Calibrated similarity/relevance score")
    rank: int = Field(..., description="1-based retrieval ranking")
    raw_similarity: float = Field(..., description="Raw cosine similarity score")


class Citation(BaseModel):
    """A claim-level attribution reference in the generated answer."""
    document_id: str
    chunk_id: str
    quote: Optional[str] = None
    is_valid: bool = True
    validation_reason: Optional[str] = None


class ConflictItem(BaseModel):
    """A single side of a documented factual conflict."""
    document_id: str
    chunk_id: str
    statement: str


class ConflictEvidence(BaseModel):
    """Structured record of conflicting evidence discovered during retrieval."""
    topic: str
    description: str
    conflicting_sources: List[str]
    conflicting_chunks: List[str]
    items: List[ConflictItem] = Field(default_factory=list)


class RAGResponse(BaseModel):
    """Unified structured response emitted by the RAG pipeline."""
    query: str
    status: ResponseStatus
    answer: str
    evidence: List[RetrievedChunk] = Field(default_factory=list)
    source_document_ids: List[str] = Field(default_factory=list)
    source_chunk_ids: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    limitations: List[str] = Field(default_factory=list)
    conflicting_evidence: Optional[ConflictEvidence] = None
    latency_ms: float = 0.0
    model_name: Optional[str] = None


# Exception Hierarchy
class RAGException(Exception):
    """Base exception for all RAG system errors."""
    pass


class CorpusError(RAGException):
    """Raised when documents directory, manifest, or document structure is invalid."""
    pass


class IndexNotFoundError(RAGException):
    """Raised when the vector index has not been built or cannot be loaded."""
    pass


class RetrievalError(RAGException):
    """Raised when similarity computation or candidate retrieval fails."""
    pass


class GenerationProviderError(RAGException):
    """Raised when an external generation provider (e.g. Gemini) encounters a failure."""
    pass


class InputValidationError(RAGException):
    """Raised when incoming user query violates validation rules."""
    pass
