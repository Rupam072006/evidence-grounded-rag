"""Embedding generation engines supporting reproducible hybrid sparse-dense and neural models."""
import os
import pickle
from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from evidence_rag.config import EmbeddingConfig
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.embeddings")


class BaseEmbeddingEngine(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def fit(self, texts: List[str]) -> None:
        """Fit embedding vocabulary/parameters if needed."""
        pass

    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts into unit-normalized vectors."""
        pass

    @abstractmethod
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query string into a unit-normalized vector."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Serialize engine state to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Deserialize engine state from disk."""
        pass


class HybridTfidfEmbeddingEngine(BaseEmbeddingEngine):
    """Deterministic, high-precision hybrid TF-IDF + n-gram vectorizer.

    Produces L2-normalized representations that support exact keyword matching
    alongside semantic phrase overlap, without network calls or GPU requirements.
    """

    def __init__(self, dimension: int = 512):
        self.dimension = dimension
        self.vectorizer = TfidfVectorizer(
            max_features=dimension,
            sublinear_tf=True,
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[\w-]+\b",
            norm="l2",
            strip_accents="unicode"
        )
        self.is_fitted = False

    def fit(self, texts: List[str]) -> None:
        if not texts:
            raise ValueError("Cannot fit embedding engine on empty text list.")
        self.vectorizer.fit(texts)
        self.is_fitted = True
        logger.info(
            f"Fitted HybridTfidfEmbeddingEngine with vocabulary size: {len(self.vectorizer.vocabulary_)}"
        )

    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        if not self.is_fitted:
            return np.zeros((len(texts), self.dimension), dtype=np.float32)

        sparse_matrix = self.vectorizer.transform(texts)
        dense_matrix = sparse_matrix.toarray().astype(np.float32)

        # Ensure L2 unit normalization
        norms = np.linalg.norm(dense_matrix, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        normalized_matrix = dense_matrix / norms
        return normalized_matrix

    def encode_query(self, query: str) -> np.ndarray:
        batch = self.encode([query])
        return batch[0]

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self.vectorizer, f)
        logger.info(f"Saved embedding model to {filepath}")

    def load(self, filepath: str) -> None:
        with open(filepath, "rb") as f:
            self.vectorizer = pickle.load(f)
        self.is_fitted = True
        logger.info(f"Loaded embedding model from {filepath}")


class SentenceTransformerEmbeddingEngine(BaseEmbeddingEngine):
    """Neural dense embedding engine using Sentence-Transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None

    def _ensure_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load SentenceTransformer model '{self.model_name}': {e}"
                )

    def fit(self, texts: List[str]) -> None:
        # Pretrained models do not require corpus fitting
        self._ensure_model()

    def encode(self, texts: List[str]) -> np.ndarray:
        self._ensure_model()
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return vectors.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        self._ensure_model()
        vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True
        )[0]
        return vector.astype(np.float32)

    def save(self, filepath: str) -> None:
        # Pretrained model identity is preserved via model_name
        pass

    def load(self, filepath: str) -> None:
        self._ensure_model()


def create_embedding_engine(config: EmbeddingConfig) -> BaseEmbeddingEngine:
    """Factory function to instantiate configured embedding engine."""
    provider = config.provider.lower()
    if provider in ("hybrid_tfidf", "tfidf"):
        return HybridTfidfEmbeddingEngine(dimension=config.dimension)
    elif provider in ("sentence_transformers", "neural", "minilm"):
        return SentenceTransformerEmbeddingEngine(model_name=config.model_name)
    else:
        logger.warning(
            f"Unknown embedding provider '{config.provider}', defaulting to hybrid_tfidf."
        )
        return HybridTfidfEmbeddingEngine(dimension=config.dimension)
