"""Configuration loading, validation, and environment variable integration."""
import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class CorpusConfig(BaseModel):
    document_dir: str = "data/documents"
    manifest_path: str = "data/manifest.json"
    required_count: int = 20


class CleaningConfig(BaseModel):
    normalize_unicode: bool = True
    collapse_whitespace: bool = True
    remove_control_characters: bool = True
    strip_external_tags: bool = True


class ChunkingConfig(BaseModel):
    strategy: str = "paragraph_window"
    chunk_size_chars: int = 400
    chunk_overlap_chars: int = 60
    min_chunk_chars: int = 40


class EmbeddingConfig(BaseModel):
    provider: str = "hybrid_tfidf"
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 512


class IndexingConfig(BaseModel):
    index_dir: str = "data/index"
    index_file: str = "knowledge_index.json"
    vectors_file: str = "vectors.npy"
    similarity_metric: str = "cosine"


class RetrievalConfig(BaseModel):
    top_k: int = 4
    similarity_threshold: float = 0.12
    evidence_sufficiency_floor: float = 0.20
    margin_threshold: float = 0.05


class GenerationConfig(BaseModel):
    mode: str = "mock"  # "mock" or "gemini"
    gemini_model: str = "gemini-1.5-flash"
    temperature: float = 0.0
    max_tokens: int = 512
    system_instruction: str = (
        "You are a strictly evidence-grounded AI knowledge assistant. "
        "Answer the user query ONLY using the provided evidence passages. "
        "Every factual assertion MUST cite its source document ID and chunk ID. "
        "If the context does not contain sufficient factual evidence, reply with INSUFFICIENT EVIDENCE. "
        "If multiple sources contradict each other, report CONFLICT DETECTED and summarize both sides."
    )


class ConflictConfig(BaseModel):
    enabled: bool = True
    polarity_contrast_weight: float = 0.6
    content_contradiction_threshold: float = 0.35


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_file: str = "logs/rag_system.log"
    mask_secrets: bool = True


class RAGConfig(BaseModel):
    version: str = "1.0"
    corpus: CorpusConfig = Field(default_factory=CorpusConfig)
    cleaning: CleaningConfig = Field(default_factory=CleaningConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    embeddings: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    conflict_detection: ConflictConfig = Field(default_factory=ConflictConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    random_seed: int = 42


def load_config(config_path: Optional[str] = None) -> RAGConfig:
    """Load configuration from a YAML file with environment variable overrides."""
    data = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        # Default search path
        default_path = Path("configs/default.yaml")
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

    config = RAGConfig(**data)

    # Environment variable overrides
    env_mode = os.getenv("RAG_GENERATION_MODE")
    if env_mode:
        config.generation.mode = env_mode

    env_gemini_model = os.getenv("GEMINI_MODEL")
    if env_gemini_model:
        config.generation.gemini_model = env_gemini_model

    env_log_level = os.getenv("RAG_LOG_LEVEL")
    if env_log_level:
        config.logging.level = env_log_level

    env_seed = os.getenv("RAG_RANDOM_SEED")
    if env_seed and env_seed.isdigit():
        config.random_seed = int(env_seed)

    return config
