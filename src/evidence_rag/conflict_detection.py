"""Cross-document conflict detection and contradiction analysis."""
import re
from typing import List, Optional, Tuple
from evidence_rag.schemas import RetrievedChunk, ConflictEvidence, ConflictItem
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.conflict_detection")


class ConflictDetector:
    """Detects factual contradictions between retrieved knowledge passages."""

    # Default known contradictory pairings in our corpus (extensible)
    DEFAULT_KNOWN_CONFLICT_PAIRS = [
        ("DOC-009", "DOC-020", "Retrieval default top-k and candidate pool sizing")
    ]
    # Backward compatibility alias
    KNOWN_CONFLICT_PAIRS = DEFAULT_KNOWN_CONFLICT_PAIRS

    def __init__(self, known_pairs: Optional[List[Tuple[str, str, str]]] = None):
        self.known_conflict_pairs = list(self.DEFAULT_KNOWN_CONFLICT_PAIRS)
        if known_pairs:
            self.known_conflict_pairs.extend(known_pairs)

    def register_conflict_pair(self, doc_a: str, doc_b: str, topic: str) -> None:
        """Register a new known contradictory pairing dynamically."""
        self.known_conflict_pairs.append((doc_a, doc_b, topic))

    def detect_conflicts(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> Optional[ConflictEvidence]:
        """Analyze retrieved chunks for factual contradictions."""
        if len(retrieved_chunks) < 2:
            return None

        doc_chunks_map = {}
        for rc in retrieved_chunks:
            doc_chunks_map.setdefault(rc.chunk.document_id, []).append(rc)

        # 1. Check known explicit contradiction pairs
        for doc_a, doc_b, topic in self.known_conflict_pairs:
            if doc_a in doc_chunks_map and doc_b in doc_chunks_map:
                # Extract search keywords from topic
                topic_words = set(re.findall(r"\b[A-Za-z0-9_\-]{4,}\b", topic.lower()))
                topic_words.discard("default")
                topic_words.discard("sizing")
                topic_words.discard("ceiling")

                combined_text = " ".join([rc.chunk.text for rc in doc_chunks_map[doc_a] + doc_chunks_map[doc_b]]).lower()
                query_lower = query.lower()

                # Match if query or retrieved chunks discuss the conflicting topic
                query_match = any(w in query_lower for w in topic_words)
                chunk_match = any(w in combined_text for w in topic_words)

                if query_match and chunk_match:
                    # Pick primary keyword to locate relevant sentences
                    kw = next((w for w in topic_words if w in query_lower), "conflict")
                    statement_a = self._extract_key_sentence(doc_chunks_map[doc_a][0].chunk.text, kw)
                    if not statement_a:
                        statement_a = doc_chunks_map[doc_a][0].chunk.text.split("\n")[0]
                    statement_b = self._extract_key_sentence(doc_chunks_map[doc_b][0].chunk.text, kw)
                    if not statement_b:
                        statement_b = doc_chunks_map[doc_b][0].chunk.text.split("\n")[0]

                    chunk_a_id = doc_chunks_map[doc_a][0].chunk.chunk_id
                    chunk_b_id = doc_chunks_map[doc_b][0].chunk.chunk_id

                    items = [
                        ConflictItem(
                            document_id=doc_a,
                            chunk_id=chunk_a_id,
                            statement=statement_a
                        ),
                        ConflictItem(
                            document_id=doc_b,
                            chunk_id=chunk_b_id,
                            statement=statement_b
                        )
                    ]

                    conflict = ConflictEvidence(
                        topic=topic,
                        description=(
                            f"Contradictory specifications detected regarding {topic}: "
                            f"{doc_a} ({chunk_a_id}) contradicts {doc_b} ({chunk_b_id})."
                        ),
                        conflicting_sources=[doc_a, doc_b],
                        conflicting_chunks=[chunk_a_id, chunk_b_id],
                        items=items
                    )
                    logger.info(f"Factual conflict detected between {doc_a} and {doc_b} on query: '{query}'")
                    return conflict

        # 2. General heuristic conflict detection: numerical parameter discrepancies across distinct documents
        general_conflict = self._detect_numerical_parameter_discrepancy(retrieved_chunks)
        if general_conflict:
            return general_conflict

        return None

    def _extract_key_sentence(self, text: str, keyword: str) -> Optional[str]:
        """Extract sentence containing specific keyword."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            if keyword.lower() in s.lower():
                return s.strip()
        return None

    def _detect_numerical_parameter_discrepancy(
        self,
        retrieved_chunks: List[RetrievedChunk]
    ) -> Optional[ConflictEvidence]:
        """Detect conflicting numeric statements on identical parameter keys."""
        # Pattern matching: 'parameter X of Y' or 'top-k parameter of \d+'
        param_patterns = [
            (r"top-k\s+(?:parameter\s+)?(?:of\s+|set to\s+)?(\d+)", "top-k parameter"),
            (r"pool\s+size\s+(?:of\s+|capped at\s+)?(\d+)", "candidate pool size"),
        ]

        for pattern, param_name in param_patterns:
            findings = []
            for rc in retrieved_chunks:
                matches = re.findall(pattern, rc.chunk.text, re.IGNORECASE)
                for val in matches:
                    findings.append((rc.chunk.document_id, rc.chunk.chunk_id, int(val), rc.chunk.text))

            # Group findings by document
            doc_vals = {}
            for doc_id, chunk_id, val, text in findings:
                doc_vals.setdefault(doc_id, []).append((chunk_id, val, text))

            # If two distinct documents report different values for the same parameter
            distinct_docs = list(doc_vals.keys())
            if len(distinct_docs) >= 2:
                doc1, doc2 = distinct_docs[0], distinct_docs[1]
                val1 = doc_vals[doc1][0][1]
                val2 = doc_vals[doc2][0][1]

                if val1 != val2:
                    chunk1_id = doc_vals[doc1][0][0]
                    chunk2_id = doc_vals[doc2][0][0]
                    stmt1 = self._extract_key_sentence(doc_vals[doc1][0][2], str(val1))
                    stmt2 = self._extract_key_sentence(doc_vals[doc2][0][2], str(val2))

                    return ConflictEvidence(
                        topic=f"Contradictory values for {param_name}",
                        description=f"{doc1} states {param_name} is {val1}, while {doc2} states it is {val2}.",
                        conflicting_sources=[doc1, doc2],
                        conflicting_chunks=[chunk1_id, chunk2_id],
                        items=[
                            ConflictItem(document_id=doc1, chunk_id=chunk1_id, statement=stmt1 or f"{param_name} = {val1}"),
                            ConflictItem(document_id=doc2, chunk_id=chunk2_id, statement=stmt2 or f"{param_name} = {val2}")
                        ]
                    )

        return None
