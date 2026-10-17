"""Persistent vector indexing, serialization, lookup tables, and candidate search."""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timezone

from evidence_rag.config import IndexingConfig
from evidence_rag.schemas import Chunk, IndexNotFoundError
from evidence_rag.embeddings import BaseEmbeddingEngine, create_embedding_engine, HybridTfidfEmbeddingEngine
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.indexing")


class VectorIndex:
    """Persistent in-memory and disk-backed vector index."""

    def __init__(
        self,
        chunks: List[Chunk],
        vectors: np.ndarray,
        embedding_engine: BaseEmbeddingEngine,
        metadata: Dict[str, Any] = None
    ):
        self.chunks = chunks
        self.vectors = vectors
        self.embedding_engine = embedding_engine
        self.metadata = metadata or {}
        self.chunk_id_to_idx = {c.chunk_id: idx for idx, c in enumerate(chunks)}
        self.doc_id_to_chunk_ids: Dict[str, List[str]] = {}
        for c in chunks:
            self.doc_id_to_chunk_ids.setdefault(c.document_id, []).append(c.chunk_id)

    @classmethod
    def build(
        cls,
        chunks: List[Chunk],
        embedding_engine: BaseEmbeddingEngine,
        corpus_fingerprint: str = ""
    ) -> "VectorIndex":
        """Build vector index from text chunks."""
        if not chunks:
            raise ValueError("Cannot build index with empty chunks list.")

        texts = [c.text for c in chunks]
        logger.info(f"Fitting embedding engine on {len(texts)} chunks...")
        embedding_engine.fit(texts)

        logger.info(f"Encoding {len(texts)} chunks into vector space...")
        vectors = embedding_engine.encode(texts)

        metadata = {
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunk_count": len(chunks),
            "vector_dimension": int(vectors.shape[1]),
            "corpus_fingerprint": corpus_fingerprint,
        }

        return cls(chunks, vectors, embedding_engine, metadata)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filter_doc_ids: Optional[List[str]] = None
    ) -> List[Tuple[Chunk, float, float]]:
        """Perform cosine similarity search against indexed chunks.

        Returns list of (Chunk, calibrated_score, raw_similarity).
        """
        if self.vectors.shape[0] == 0:
            return []

        # Cosine similarity is dot product because vectors are L2-normalized
        # query_vector: (D,), vectors: (N, D) -> similarities: (N,)
        similarities = np.dot(self.vectors, query_vector)
        # Ensure scores are within [0.0, 1.0]
        similarities = np.clip(similarities, 0.0, 1.0)

        # Apply metadata filters if provided
        candidate_indices = np.arange(len(self.chunks))
        if filter_doc_ids:
            allowed_ids = set(filter_doc_ids)
            candidate_indices = np.array([
                i for i in candidate_indices if self.chunks[i].document_id in allowed_ids
            ])
            if len(candidate_indices) == 0:
                return []

        # Sort candidate indices by similarity descending
        sub_similarities = similarities[candidate_indices]
        sorted_sub_order = np.argsort(-sub_similarities)
        top_indices = candidate_indices[sorted_sub_order][:top_k]

        results = []
        for rank_idx, idx in enumerate(top_indices):
            chunk = self.chunks[idx]
            raw_sim = float(similarities[idx])
            results.append((chunk, raw_sim, raw_sim))

        return results

    def save(self, index_dir: str) -> None:
        """Persist vector matrix, metadata, chunks, and embedding model to disk."""
        target_dir = Path(index_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        vectors_path = target_dir / "vectors.npy"
        np.save(str(vectors_path), self.vectors)

        # Save embedding model state
        model_path = target_dir / "embedding_model.pkl"
        self.embedding_engine.save(str(model_path))

        # Save chunks and index manifest
        chunks_data = [c.model_dump() for c in self.chunks]
        manifest_data = {
            "metadata": self.metadata,
            "chunks": chunks_data
        }

        manifest_path = target_dir / "knowledge_index.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        logger.info(f"Successfully persisted index with {len(self.chunks)} chunks to {index_dir}")

    @classmethod
    def load(cls, index_dir: str, embedding_engine: BaseEmbeddingEngine = None) -> "VectorIndex":
        """Load persistent vector index from disk."""
        target_dir = Path(index_dir)
        vectors_path = target_dir / "vectors.npy"
        manifest_path = target_dir / "knowledge_index.json"
        model_path = target_dir / "embedding_model.pkl"

        if not vectors_path.exists() or not manifest_path.exists():
            raise IndexNotFoundError(
                f"Index files missing at {index_dir}. Must build index before retrieval."
            )

        try:
            vectors = np.load(str(vectors_path))
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            chunks = [Chunk(**cd) for cd in manifest_data["chunks"]]
            metadata = manifest_data.get("metadata", {})

            if embedding_engine is None:
                # Reconstruct engine
                embedding_engine = HybridTfidfEmbeddingEngine(dimension=int(vectors.shape[1]))

            if model_path.exists():
                embedding_engine.load(str(model_path))

            logger.info(f"Loaded index containing {len(chunks)} chunks from {index_dir}")
            return cls(chunks, vectors, embedding_engine, metadata)
        except Exception as e:
            raise IndexNotFoundError(f"Failed to load vector index from {index_dir}: {e}")
