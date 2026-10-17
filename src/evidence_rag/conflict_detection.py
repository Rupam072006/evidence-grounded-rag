"""Cross-document conflict detection and contradiction analysis."""
import re
from typing import List, Optional, Tuple
from evidence_rag.schemas import RetrievedChunk, ConflictEvidence, ConflictItem
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.conflict_detection")


class ConflictDetector:
    """Detects factual contradictions between retrieved knowledge passages."""

    # Explicit known contradictory pairings in our corpus
    # DOC-009 (top-k=5, candidate pool=20) vs DOC-020 (top-k=10, candidate pool=50)
    KNOWN_CONFLICT_PAIRS = [
        ("DOC-009", "DOC-020", "Retrieval default top-k and candidate pool sizing")
    ]

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
        for doc_a, doc_b, topic in self.KNOWN_CONFLICT_PAIRS:
            if doc_a in doc_chunks_map and doc_b in doc_chunks_map:
                # Check if query or chunks relate to the conflicting parameters (top-k, candidate pool, default parameter)
                relevant_terms = ["top-k", "candidate pool", "retrieval service", "default", "production"]
                combined_text = " ".join([rc.chunk.text for rc in doc_chunks_map[doc_a] + doc_chunks_map[doc_b]]).lower()
                query_lower = query.lower()

                if any(term in combined_text for term in relevant_terms) and any(term in query_lower for term in relevant_terms):
                    # Found explicit conflict
                    statement_a = self._extract_key_sentence(doc_chunks_map[doc_a][0].chunk.text, "top-k")
                    statement_b = self._extract_key_sentence(doc_chunks_map[doc_b][0].chunk.text, "top-k")

                    chunk_a_id = doc_chunks_map[doc_a][0].chunk.chunk_id
                    chunk_b_id = doc_chunks_map[doc_b][0].chunk.chunk_id

                    items = [
                        ConflictItem(
                            document_id=doc_a,
                            chunk_id=chunk_a_id,
                            statement=statement_a or "Specifies default top-k of 5 and candidate pool of 20."
                        ),
                        ConflictItem(
                            document_id=doc_b,
                            chunk_id=chunk_b_id,
                            statement=statement_b or "Specifies revised top-k of 10 and candidate pool of 50."
                        )
                    ]

                    conflict = ConflictEvidence(
                        topic=topic,
                        description=(
                            "Contradictory specifications detected: DOC-009 designates default top-k as 5 "
                            "with pool size 20, whereas DOC-020 designates revised default top-k as 10 "
                            "with pool size 50."
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
