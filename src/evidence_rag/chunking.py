"""Boundary-aware text chunking and deterministic chunk identity generation."""
import re
from typing import List
from evidence_rag.config import ChunkingConfig
from evidence_rag.schemas import Document, Chunk
from evidence_rag.cleaning import TextCleaner


class Chunker:
    """Chunks documents into coherent passages with stable IDs and boundary awareness."""

    def __init__(self, config: ChunkingConfig = None, cleaner: TextCleaner = None):
        self.config = config or ChunkingConfig()
        self.cleaner = cleaner or TextCleaner()

    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Split a single document into deterministic chunks."""
        cleaned_text = self.cleaner.clean(doc.content)
        if not cleaned_text:
            return []

        # Split into paragraph blocks
        paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]
        raw_chunks: List[str] = []
        current_chunk = ""

        target_size = self.config.chunk_size_chars
        overlap_size = self.config.chunk_overlap_chars
        min_size = self.config.min_chunk_chars

        for para in paragraphs:
            # If paragraph itself is very long, split by sentences
            if len(para) > target_size * 1.5:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current_chunk) + len(sent) + 1 <= target_size:
                        current_chunk = f"{current_chunk} {sent}".strip()
                    else:
                        if current_chunk:
                            raw_chunks.append(current_chunk)
                            # Compute overlap suffix
                            overlap = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                            current_chunk = f"{overlap} {sent}".strip()
                        else:
                            current_chunk = sent
            else:
                if len(current_chunk) + len(para) + 2 <= target_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip() if current_chunk else para
                else:
                    if current_chunk:
                        raw_chunks.append(current_chunk)
                        overlap = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                        current_chunk = f"{overlap}\n\n{para}".strip()
                    else:
                        current_chunk = para

        if current_chunk:
            raw_chunks.append(current_chunk)

        # Merge orphan fragments shorter than min_size
        final_chunks: List[str] = []
        for rc in raw_chunks:
            rc = rc.strip()
            if not rc:
                continue
            if len(rc) < min_size and final_chunks:
                # Merge into previous chunk
                final_chunks[-1] = f"{final_chunks[-1]} {rc}".strip()
            else:
                final_chunks.append(rc)

        # Assemble structured Chunk objects with stable IDs
        chunk_objects: List[Chunk] = []
        doc_id = doc.metadata.document_id

        # Trace character offsets approximately in cleaned text
        search_cursor = 0
        for idx, chunk_text in enumerate(final_chunks, start=1):
            chunk_id = f"{doc_id}-C{idx:03d}"
            char_start = cleaned_text.find(chunk_text[:30], search_cursor)
            if char_start == -1:
                char_start = search_cursor
            char_end = char_start + len(chunk_text)
            search_cursor = max(search_cursor, char_end - overlap_size)

            token_count = len(chunk_text.split())

            chunk_obj = Chunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                chunk_index=idx - 1,
                text=chunk_text,
                char_start=char_start,
                char_end=char_end,
                token_count=token_count,
                metadata={
                    "title": doc.metadata.title,
                    "topic": doc.metadata.topic,
                    "source": doc.metadata.source,
                    "version": doc.metadata.version,
                    "source_type": doc.metadata.source_type,
                }
            )
            chunk_objects.append(chunk_obj)

        return chunk_objects

    def chunk_corpus(self, documents: List[Document]) -> List[Chunk]:
        """Chunk an entire corpus of documents."""
        all_chunks: List[Chunk] = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
