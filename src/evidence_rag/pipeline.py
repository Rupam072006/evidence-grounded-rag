"""Unified, end-to-end Evidence-Grounded RAG Pipeline."""
import time
from typing import Optional, List, Tuple
from pathlib import Path

from evidence_rag.config import RAGConfig, load_config
from evidence_rag.schemas import (
    RAGResponse,
    ResponseStatus,
    RetrievedChunk,
    Citation,
    ConflictEvidence,
    IndexNotFoundError
)
from evidence_rag.ingestion import IngestionEngine
from evidence_rag.chunking import Chunker
from evidence_rag.embeddings import create_embedding_engine
from evidence_rag.indexing import VectorIndex
from evidence_rag.retrieval import Retriever
from evidence_rag.context_builder import ContextBuilder
from evidence_rag.conflict_detection import ConflictDetector
from evidence_rag.generation import create_generator, BaseGenerator
from evidence_rag.evidence import CitationValidator
from evidence_rag.confidence import ConfidenceScorer
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.pipeline")


class RAGPipeline:
    """Master orchestrator for ingestion, indexing, retrieval, and grounded generation."""

    CANONICAL_REFUSAL = (
        "INSUFFICIENT EVIDENCE: The available knowledge base does not contain "
        "enough information to answer this question reliably."
    )

    def __init__(self, config: Optional[RAGConfig] = None, base_dir: Optional[Path] = None):
        self.config = config or load_config()
        self.base_dir = base_dir or Path.cwd()
        self.index: Optional[VectorIndex] = None
        self.generator: BaseGenerator = create_generator(self.config.generation)
        self.conflict_detector = ConflictDetector()
        self.citation_validator = CitationValidator()
        self.confidence_scorer = ConfidenceScorer()
        self.context_builder = ContextBuilder()

    def compute_corpus_fingerprint(self) -> str:
        """Compute SHA-256 fingerprint across all loaded documents."""
        import hashlib
        ingestion_engine = IngestionEngine(self.config.corpus, base_dir=self.base_dir)
        documents = ingestion_engine.load_corpus()
        combined = "|".join(sorted(d.content_hash for d in documents))
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def is_index_stale(self, index: Optional[VectorIndex] = None) -> bool:
        """Check if persistent index fingerprint differs from the current corpus."""
        target_index = index or self.index
        if target_index is None:
            return True
        cached_fp = target_index.metadata.get("corpus_fingerprint", "")
        current_fp = self.compute_corpus_fingerprint()
        return cached_fp != current_fp

    def build_index(self) -> VectorIndex:
        """Execute full ingestion, chunking, and index build from source corpus."""
        logger.info("Starting index build workflow...")
        start_time = time.time()

        # 1. Ingestion
        ingestion_engine = IngestionEngine(self.config.corpus, base_dir=self.base_dir)
        documents = ingestion_engine.load_corpus()

        # 2. Chunking
        chunker = Chunker(self.config.chunking)
        chunks = chunker.chunk_corpus(documents)
        logger.info(f"Chunked {len(documents)} documents into {len(chunks)} passages.")

        # 3. Embeddings & Indexing
        embedding_engine = create_embedding_engine(self.config.embeddings)
        import hashlib as _hashlib
        combined = "|".join(sorted(d.content_hash for d in documents))
        corpus_fingerprint = _hashlib.sha256(combined.encode()).hexdigest()[:16]
        index = VectorIndex.build(chunks, embedding_engine, corpus_fingerprint=corpus_fingerprint)

        # 4. Save persistent index
        index_dir = self.base_dir / self.config.indexing.index_dir
        index.save(str(index_dir))

        self.index = index
        elapsed = time.time() - start_time
        logger.info(f"Index build completed in {elapsed:.2f}s with {len(chunks)} chunks.")
        return index

    def load_index(self) -> VectorIndex:
        """Load persistent vector index from configured directory."""
        index_dir = self.base_dir / self.config.indexing.index_dir
        embedding_engine = create_embedding_engine(self.config.embeddings)
        self.index = VectorIndex.load(str(index_dir), embedding_engine=embedding_engine)
        return self.index

    def ensure_index(self, check_staleness: bool = True) -> VectorIndex:
        """Ensure an index is loaded, attempting to load from disk or build if absent or stale."""
        if self.index is not None:
            if check_staleness and self.is_index_stale(self.index):
                logger.info("Loaded index is stale compared to corpus; rebuilding...")
                return self.build_index()
            return self.index
        try:
            idx = self.load_index()
            if check_staleness and self.is_index_stale(idx):
                logger.info("Persistent index is stale compared to corpus; rebuilding...")
                return self.build_index()
            return idx
        except IndexNotFoundError:
            logger.info("Persistent index not found; building from corpus...")
            return self.build_index()

    def validate_input(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate input query boundaries and content."""
        if query is None or not isinstance(query, str):
            return False, "Query must be a non-empty string."

        stripped = query.strip()
        if not stripped:
            return False, "Query cannot be empty or contain only whitespace."

        if len(stripped) < 3:
            return False, "Query must contain at least 3 non-whitespace characters."

        if len(stripped) > 500:
            return False, f"Query exceeds maximum allowed length of 500 characters (length: {len(stripped)})."

        # Reject control characters or null bytes
        if any(ord(c) < 32 and c not in ("\t", "\n", "\r") for c in stripped):
            return False, "Query contains invalid or disallowed control characters."

        return True, None

    def query(self, user_query: str) -> RAGResponse:
        """Process user query end-to-end through the RAG pipeline."""
        start_time = time.time()

        # Step 1: Input Validation
        is_valid, validation_error = self.validate_input(user_query)
        if not is_valid:
            return RAGResponse(
                query=user_query or "",
                status=ResponseStatus.INVALID_INPUT,
                answer=f"INVALID INPUT: {validation_error}",
                latency_ms=round((time.time() - start_time) * 1000, 2),
                limitations=["Request rejected prior to retrieval due to input validation violation."]
            )

        clean_query = user_query.strip()

        # Step 2: Ensure Index
        try:
            index = self.ensure_index()
        except Exception as e:
            logger.error(f"Failed to access index: {e}")
            return RAGResponse(
                query=clean_query,
                status=ResponseStatus.INDEX_UNAVAILABLE,
                answer=f"INDEX UNAVAILABLE: Unable to load knowledge index: {e}",
                latency_ms=round((time.time() - start_time) * 1000, 2)
            )

        # Step 3: Retrieval
        retriever = Retriever(index, self.config.retrieval)
        retrieved_chunks = retriever.retrieve(clean_query)

        source_doc_ids = list(dict.fromkeys([rc.chunk.document_id for rc in retrieved_chunks]))
        source_chunk_ids = [rc.chunk.chunk_id for rc in retrieved_chunks]

        # Step 4: Evidence Sufficiency Assessment
        sufficient = retriever.assess_evidence_sufficiency(retrieved_chunks, query=clean_query)
        if not sufficient or not retrieved_chunks:
            confidence, limitations = self.confidence_scorer.calculate_confidence(clean_query, retrieved_chunks)
            limitations.append("Retrieval similarity below evidence sufficiency floor (0.25).")
            return RAGResponse(
                query=clean_query,
                status=ResponseStatus.INSUFFICIENT_EVIDENCE,
                answer=self.CANONICAL_REFUSAL,
                evidence=retrieved_chunks,
                source_document_ids=source_doc_ids,
                source_chunk_ids=source_chunk_ids,
                citations=[],
                confidence=confidence,
                limitations=limitations,
                latency_ms=round((time.time() - start_time) * 1000, 2),
                model_name=getattr(self.generator, "model_name", "deterministic_mock")
            )

        # Step 5: Conflict Detection
        conflict_evidence = None
        if self.config.conflict_detection.enabled:
            conflict_evidence = self.conflict_detector.detect_conflicts(clean_query, retrieved_chunks)

        # Step 6: Context Construction
        context_str, included_chunk_ids = self.context_builder.build_context(retrieved_chunks)

        # Step 7: Grounded Generation
        raw_answer, response_status = self.generator.generate_answer(
            query=clean_query,
            context=context_str,
            retrieved_chunks=retrieved_chunks,
            conflict=conflict_evidence
        )

        # Step 8: Citation Extraction & Validation
        validated_citations = self.citation_validator.validate_citations(raw_answer, retrieved_chunks)

        # Step 9: Confidence & Uncertainty Scoring
        confidence, limitations = self.confidence_scorer.calculate_confidence(clean_query, retrieved_chunks)
        if conflict_evidence:
            limitations.append("Contradictory knowledge sources detected; answer presents multiple perspectives.")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return RAGResponse(
            query=clean_query,
            status=response_status,
            answer=raw_answer,
            evidence=retrieved_chunks,
            source_document_ids=source_doc_ids,
            source_chunk_ids=source_chunk_ids,
            citations=validated_citations,
            confidence=confidence,
            limitations=limitations,
            conflicting_evidence=conflict_evidence,
            latency_ms=elapsed_ms,
            model_name=getattr(self.generator, "model_name", "deterministic_mock")
        )
