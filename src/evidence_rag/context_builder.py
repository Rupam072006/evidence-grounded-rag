"""Context construction, passage delimitation, budgeting, and untrusted data quarantining."""
from typing import List, Tuple
from evidence_rag.schemas import RetrievedChunk
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.context_builder")


class ContextBuilder:
    """Formats retrieved evidence passages into structured, boundary-isolated context."""

    DEFAULT_MAX_CHARS = 6000  # Approximately 1,500 tokens

    def __init__(self, max_chars: int = DEFAULT_MAX_CHARS):
        self.max_chars = max_chars

    def build_context(self, evidence: List[RetrievedChunk]) -> Tuple[str, List[str]]:
        """Construct isolated context string from ranked evidence chunks.

        Returns:
            Tuple of (formatted_context_string, list_of_included_chunk_ids)
        """
        if not evidence:
            return "", []

        passages = []
        included_chunk_ids = []
        current_chars = 0

        for item in evidence:
            chunk = item.chunk
            header = f"=== PASSAGE [{chunk.chunk_id}] (SOURCE: {chunk.document_id} | RELEVANCE: {item.score:.2f}) ==="
            footer = "=== END PASSAGE ==="
            passage_block = f"{header}\n{chunk.text}\n{footer}\n"

            block_len = len(passage_block)
            if current_chars + block_len > self.max_chars:
                logger.debug(
                    f"Context budget reached ({current_chars}/{self.max_chars} chars). Excluding chunk {chunk.chunk_id}."
                )
                break

            passages.append(passage_block)
            included_chunk_ids.append(chunk.chunk_id)
            current_chars += block_len

        context_body = "\n".join(passages)
        return context_body, included_chunk_ids
