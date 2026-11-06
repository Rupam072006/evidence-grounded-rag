"""Semantic retrieval, similarity scoring, candidate ranking, and evidence filtering."""
import re
from typing import List, Optional
import numpy as np
from evidence_rag.config import RetrievalConfig
from evidence_rag.schemas import Chunk, RetrievedChunk, RetrievalError
from evidence_rag.indexing import VectorIndex
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.retrieval")


class Retriever:
    """Retrieves and ranks relevant document chunks for user queries."""

    STOPWORDS = {
        "what", "is", "the", "a", "an", "and", "or", "in", "of", "to", "for",
        "with", "on", "at", "by", "from", "how", "does", "do", "can", "are",
        "which", "when", "why", "where", "who", "whom", "this", "that", "relate",
        "defined", "describe", "according", "between"
    }

    DOMAIN_KEYWORDS = {
        "python": [
            "python", "def ", "class ", "functions", "exception", "exceptions",
            "try", "except", "finally", "raise", "numpy", "pandas", "dataframe",
            "matplotlib", "data cleaning", "vectorization", "module", "list", "dict"
        ],
        "sql": [
            "sql", "relational", "database", "select ", "join", "joins", "inner join",
            "left join", "right join", "group by", "order by", "table", "schema",
            "foreign key", "primary key", "where "
        ],
        "machine_learning": [
            "machine learning", "ml", "supervised", "unsupervised", "model evaluation",
            "classification", "regression", "precision", "recall", "f1", "auc", "roc",
            "train", "test split", "embedding", "embeddings", "vector search",
            "chunking", "prompt injection", "observability", "rag", "dense", "metric"
        ],
        "business_proposal": [
            "proposal", "campaign proposal", "growth campaign", "initiative",
            "expansion proposal", "incomplete proposal", "preliminary budget"
        ],
        "budget_policy": [
            "budget", "budget policy", "spending policy", "spending cap", "reserve",
            "spend cap", "50,000", "50000", "financial boundaries", "contingency", "cost cap"
        ],
        "marketing_performance": [
            "ctr", "cac", "cvr", "conversion", "conversions", "click-through",
            "acquisition cost", "benchmark", "benchmarks", "performance metrics", "marketing metrics"
        ],
        "business_approval_policy": [
            "influencer", "influencers", "creator", "creators", "approval gate",
            "approval policy", "governance policy", "spending limit", "partnership policy"
        ]
    }

    def __init__(self, index: VectorIndex, config: RetrievalConfig = None):
        self.index = index
        self.config = config or RetrievalConfig()

    def detect_query_domains(self, query: str) -> List[str]:
        """Detect relevant domain categories from query vocabulary."""
        q_lower = f" {query.lower()} "
        matched = []
        for domain, kw_list in self.DOMAIN_KEYWORDS.items():
            for kw in kw_list:
                # Word boundary check for short words, substring for phrases
                if len(kw) <= 3:
                    if re.search(rf"\b{re.escape(kw.strip())}\b", q_lower):
                        matched.append(domain)
                        break
                else:
                    if kw in q_lower:
                        matched.append(domain)
                        break
        return matched

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_doc_ids: Optional[List[str]] = None,
        filter_categories: Optional[List[str]] = None,
        auto_domain_route: bool = True
    ) -> List[RetrievedChunk]:
        """Execute semantic search, domain-aware routing, calibration, and candidate ranking."""
        k = top_k or self.config.top_k
        if not query or not query.strip():
            return []

        # Detect domain signals for domain-aware scoring
        detected_domains = self.detect_query_domains(query) if auto_domain_route else []

        try:
            # 1. Encode query
            query_vector = self.index.embedding_engine.encode_query(query)

            # 2. Retrieve candidates from index
            pool_k = min(len(self.index.chunks), max(k * 4, 30))
            raw_candidates = self.index.search(
                query_vector=query_vector,
                top_k=pool_k,
                filter_doc_ids=filter_doc_ids,
                filter_categories=filter_categories
            )
        except Exception as e:
            logger.error(f"Retrieval error during search: {e}")
            raise RetrievalError(f"Vector search failed: {e}")

        if not raw_candidates:
            return []

        # 3. Extract meaningful query terms for lexical calibration
        query_terms = self._extract_query_terms(query)

        # Check domain classification
        is_biz_query = any(d in {"business_proposal", "budget_policy", "marketing_performance", "business_approval_policy"} for d in detected_domains)
        is_tech_query = any(d in {"python", "sql", "machine_learning"} for d in detected_domains)

        calibrated_results = []
        for chunk, raw_sim, _ in raw_candidates:
            boost = self._calculate_keyword_boost(query_terms, chunk.text)
            chunk_cat = str(getattr(chunk, "category", None) or chunk.metadata.get("category") or "").lower()

            # Domain awareness scoring
            domain_multiplier = 1.0
            if detected_domains:
                if chunk_cat in detected_domains:
                    boost += 0.05
                elif is_biz_query and not is_tech_query and chunk_cat in {"python", "sql", "machine_learning"}:
                    # Prevent irrelevant technical documents from polluting pure business queries
                    domain_multiplier = 0.60
                elif is_tech_query and not is_biz_query and chunk_cat in {"business_proposal", "budget_policy", "marketing_performance", "business_approval_policy"}:
                    # Prevent business policy documents from polluting pure technical queries
                    domain_multiplier = 0.60

            calibrated_score = min(1.0, (raw_sim + boost) * domain_multiplier)

            # Apply candidate similarity threshold
            if calibrated_score >= self.config.similarity_threshold:
                calibrated_results.append((chunk, calibrated_score, raw_sim))

        # 4. Sort by calibrated score descending
        calibrated_results.sort(key=lambda x: x[1], reverse=True)
        top_slice = calibrated_results[:k]

        # 5. Build RetrievedChunk objects with 1-based ranks
        retrieved_chunks = [
            RetrievedChunk(
                chunk=chunk,
                score=round(score, 4),
                rank=idx,
                raw_similarity=round(raw_sim, 4)
            )
            for idx, (chunk, score, raw_sim) in enumerate(top_slice, start=1)
        ]

        logger.debug(
            f"Query '{query[:40]}...' retrieved {len(retrieved_chunks)} chunks (top score: {retrieved_chunks[0].score if retrieved_chunks else 0.0})"
        )
        return retrieved_chunks

    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract alphanumeric tokens excluding basic stopwords."""
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", query.lower())
        return [t for t in tokens if t not in self.STOPWORDS]

    def _calculate_keyword_boost(self, query_terms: List[str], chunk_text: str) -> float:
        """Calculate small additive boost for exact matching key terms."""
        if not query_terms:
            return 0.0

        lower_text = chunk_text.lower()
        matches = sum(1 for term in query_terms if term in lower_text)
        overlap_ratio = matches / len(query_terms)

        # Max boost is 0.08
        return 0.08 * overlap_ratio

    def assess_evidence_sufficiency(
        self,
        retrieved: List[RetrievedChunk],
        query: Optional[str] = None
    ) -> bool:
        """Check whether retrieved evidence passes the sufficiency floor and term coverage."""
        if not retrieved:
            return False
        top_score = retrieved[0].score
        if top_score < self.config.evidence_sufficiency_floor:
            return False

        if query:
            terms = self._extract_query_terms(query)
            if len(terms) >= 3:
                all_text = " ".join(rc.chunk.text.lower() for rc in retrieved)
                matches = sum(1 for t in terms if t in all_text)
                coverage = matches / len(terms)
                # If less than 28% of key query terms appear in the retrieved context, reject as insufficient
                if coverage < 0.28:
                    return False

        return True
