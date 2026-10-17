"""Confidence scoring and uncertainty quantification."""
import re
from typing import List, Tuple
from evidence_rag.schemas import RetrievedChunk
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.confidence")


class ConfidenceScorer:
    """Calculates multi-factor confidence and documents uncertainty limitations."""

    STOPWORDS = {
        "what", "is", "the", "a", "an", "and", "or", "in", "of", "to", "for",
        "with", "on", "at", "by", "from", "how", "does", "do", "can", "are",
        "which", "when", "why", "where", "who", "whom", "this", "that"
    }

    def calculate_confidence(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> Tuple[float, List[str]]:
        """Compute composite confidence score and accompanying technical limitations.

        Formula (from DOC-014 specification):
        Confidence = (0.50 * Top_Similarity_Score) +
                     (0.30 * Mean_Top3_Similarity) +
                     (0.20 * Query_Term_Coverage_Ratio)
        """
        limitations = [
            "Confidence metric reflects lexical and semantic representation overlap; "
            "it is not a calibrated Bayesian posterior probability."
        ]

        if not retrieved_chunks:
            return 0.0, limitations + ["Zero evidence passages retrieved from knowledge base."]

        top_score = retrieved_chunks[0].score

        # Top-3 mean similarity
        top3 = retrieved_chunks[:3]
        mean_top3 = sum(rc.score for rc in top3) / len(top3)

        # Query term coverage ratio
        query_terms = self._extract_terms(query)
        if query_terms:
            combined_evidence_text = " ".join([rc.chunk.text.lower() for rc in retrieved_chunks])
            matched_terms = sum(1 for t in query_terms if t in combined_evidence_text)
            coverage_ratio = matched_terms / len(query_terms)
        else:
            coverage_ratio = 1.0

        # Composite score
        raw_confidence = (0.50 * top_score) + (0.30 * mean_top3) + (0.20 * coverage_ratio)
        bounded_confidence = round(min(1.0, max(0.0, raw_confidence)), 4)

        if bounded_confidence < 0.35:
            limitations.append("Low confidence: Semantic overlap between query and retrieved context is marginal.")
        if len(retrieved_chunks) < 2:
            limitations.append("Limited corroboration: Retrieval provided fewer than two distinct passages.")

        return bounded_confidence, limitations

    def _extract_terms(self, text: str) -> List[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", text.lower())
        return [t for t in tokens if t not in self.STOPWORDS]
