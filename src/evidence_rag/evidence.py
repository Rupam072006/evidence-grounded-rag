"""Evidence verification, citation extraction, and grounding validation."""
import re
from typing import List, Set, Dict
from evidence_rag.schemas import Citation, RetrievedChunk
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.evidence")


class CitationValidator:
    """Extracts, validates, and audits claim-level citations in generated answers."""

    # Matches formats: [DOC-001:DOC-001-C001], [DOC-001:C001], [DOC-001-C001], [DOC-001], 【DOC-001-C001】
    CITATION_PATTERN = re.compile(
        r"[\[\u3010](DOC-\d{3})(?:[:-]([A-Za-z0-9\-_]+))?[\]\u3011]"
    )

    def extract_citations(self, text: str) -> List[Citation]:
        """Extract all candidate citations from answer text."""
        citations = []
        if not text:
            return citations

        matches = self.CITATION_PATTERN.findall(text)
        for doc_id, chunk_spec in matches:
            if chunk_spec:
                # If chunk_spec is like 'C001', normalize to 'DOC-001-C001'
                if chunk_spec.startswith("C") and len(chunk_spec) == 4 and chunk_spec[1:].isdigit():
                    chunk_id = f"{doc_id}-{chunk_spec}"
                else:
                    chunk_id = chunk_spec
            else:
                chunk_id = f"{doc_id}-C001"  # Default reference if only doc cited

            citations.append(
                Citation(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    is_valid=True
                )
            )
        return citations

    def validate_citations(
        self,
        text: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> List[Citation]:
        """Validate citations against the actual retrieved context chunks."""
        raw_citations = self.extract_citations(text)
        if not raw_citations:
            return []

        # Build lookup of valid retrieved chunks
        valid_chunks_map: Dict[str, RetrievedChunk] = {
            item.chunk.chunk_id: item for item in retrieved_chunks
        }
        valid_doc_ids: Set[str] = {
            item.chunk.document_id for item in retrieved_chunks
        }

        validated_citations: List[Citation] = []
        seen = set()

        for cit in raw_citations:
            key = (cit.document_id, cit.chunk_id)
            if key in seen:
                continue
            seen.add(key)

            # Check 1: Did document exist in retrieved context?
            if cit.document_id not in valid_doc_ids:
                cit.is_valid = False
                cit.validation_reason = f"Document {cit.document_id} was not in retrieved context."
            # Check 2: Did specific chunk exist in retrieved context?
            elif cit.chunk_id not in valid_chunks_map:
                # Check if it was at least from the same document
                cit.is_valid = False
                cit.validation_reason = f"Chunk {cit.chunk_id} was not retrieved for this query."
            else:
                # Valid citation
                cit.is_valid = True
                cit.validation_reason = "Verified in retrieved context."

            validated_citations.append(cit)

        return validated_citations
