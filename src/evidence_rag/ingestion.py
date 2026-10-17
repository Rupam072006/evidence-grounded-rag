"""Document ingestion, manifest validation, cryptographic fingerprinting, and corpus loading."""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
from evidence_rag.config import CorpusConfig
from evidence_rag.schemas import Document, DocumentMetadata, CorpusError
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.ingestion")


class IngestionEngine:
    """Manages document discovery, manifest validation, and corpus ingestion."""

    REQUIRED_METADATA_FIELDS = [
        "document_id",
        "title",
        "source",
        "source_type",
        "version",
        "created_at",
        "updated_at",
        "topic"
    ]

    def __init__(self, config: CorpusConfig = None, base_dir: Path = None):
        self.config = config or CorpusConfig()
        self.base_dir = base_dir or Path.cwd()

    def load_corpus(self) -> List[Document]:
        """Ingest all documents declared in manifest, verifying counts and cryptographic integrity."""
        manifest_path = self.base_dir / self.config.manifest_path
        if not manifest_path.exists():
            raise CorpusError(f"Corpus manifest not found at: {manifest_path}")

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CorpusError(f"Corrupt or invalid JSON in manifest {manifest_path}: {e}")

        raw_docs = manifest_data.get("documents", [])
        total_in_manifest = manifest_data.get("total_documents", len(raw_docs))

        # Check required document count
        if len(raw_docs) != self.config.required_count:
            raise CorpusError(
                f"Expected exactly {self.config.required_count} documents in manifest, but found {len(raw_docs)}."
            )

        ingested_documents: List[Document] = []
        seen_ids = set()

        for idx, item in enumerate(raw_docs):
            # Validate metadata completeness
            metadata = self._validate_metadata(item, idx)
            if metadata.document_id in seen_ids:
                raise CorpusError(f"Duplicate document_id found: {metadata.document_id}")
            seen_ids.add(metadata.document_id)

            # Resolve file path
            doc_file_path = self.base_dir / metadata.source
            if not doc_file_path.exists():
                raise CorpusError(
                    f"Document file missing on disk: {doc_file_path} for document_id {metadata.document_id}"
                )

            # Read document content and compute hash
            try:
                with open(doc_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                raise CorpusError(f"Failed to read document {doc_file_path}: {e}")

            if not content.strip():
                raise CorpusError(f"Document {metadata.document_id} at {doc_file_path} is empty.")

            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            doc = Document(
                metadata=metadata,
                content=content,
                content_hash=content_hash
            )
            ingested_documents.append(doc)

        logger.info(
            f"Successfully ingested and verified {len(ingested_documents)} documents from manifest."
        )
        return ingested_documents

    def _validate_metadata(self, data: Dict[str, Any], index: int) -> DocumentMetadata:
        """Validate metadata fields against specification."""
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in data or data[field] is None:
                raise CorpusError(
                    f"Document at index {index} is missing required metadata field: '{field}'"
                )
            if isinstance(data[field], str) and not data[field].strip():
                raise CorpusError(
                    f"Document at index {index} has empty string for required metadata field: '{field}'"
                )

        try:
            return DocumentMetadata(**data)
        except Exception as e:
            raise CorpusError(f"Schema validation failed for document at index {index}: {e}")
