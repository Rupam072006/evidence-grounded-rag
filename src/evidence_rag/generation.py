"""Language model generation layer supporting offline deterministic mock and Google Gemini API."""
import os
import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import httpx

from evidence_rag.config import GenerationConfig
from evidence_rag.schemas import (
    RetrievedChunk,
    ResponseStatus,
    ConflictEvidence,
    GenerationProviderError
)
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.generation")


class BaseGenerator(ABC):
    """Abstract generation interface."""

    @abstractmethod
    def generate_answer(
        self,
        query: str,
        context: str,
        retrieved_chunks: List[RetrievedChunk],
        conflict: Optional[ConflictEvidence] = None
    ) -> Tuple[str, ResponseStatus]:
        """Generate grounded answer from evidence context."""
        pass


class DeterministicMockGenerator(BaseGenerator):
    """Deterministic, grounded offline generator.

    Extracts verified factual statements strictly from retrieved passages,
    applies claim-level citations, handles conflicts, and emits canonical refusals.
    """

    CANONICAL_REFUSAL = (
        "INSUFFICIENT EVIDENCE: The available knowledge base does not contain "
        "enough information to answer this question reliably."
    )

    def generate_answer(
        self,
        query: str,
        context: str,
        retrieved_chunks: List[RetrievedChunk],
        conflict: Optional[ConflictEvidence] = None
    ) -> Tuple[str, ResponseStatus]:
        # 1. Conflict handling
        if conflict:
            items_text = []
            for item in conflict.items:
                items_text.append(f"- [{item.document_id}:{item.chunk_id}]: {item.statement}")
            answer = (
                f"CONFLICT DETECTED: Contradictory evidence exists in the knowledge base regarding '{conflict.topic}'.\n\n"
                f"{conflict.description}\n\n"
                "Documented contradictions:\n" + "\n".join(items_text)
            )
            return answer, ResponseStatus.CONFLICT_DETECTED

        # 2. Insufficient context check
        if not retrieved_chunks or not context.strip():
            return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE

        # 3. Grounded extraction from retrieved chunks
        query_words = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query.lower()))
        stopwords = {"what", "how", "does", "the", "and", "for", "with", "from", "are", "can", "is"}
        core_query_words = query_words - stopwords

        candidate_sentences: List[Tuple[str, str, str, int]] = []
        for rc in retrieved_chunks:
            sentences = re.split(r"(?<=[.!?])\s+", rc.chunk.text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) < 15 or s_clean.startswith("#"):
                    continue
                s_lower = s_clean.lower()
                overlap = sum(1 for w in core_query_words if w in s_lower)
                if overlap > 0:
                    candidate_sentences.append(
                        (s_clean, rc.chunk.document_id, rc.chunk.chunk_id, overlap)
                    )

        if not candidate_sentences:
            return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE

        # Sort candidate sentences by overlap descending
        candidate_sentences.sort(key=lambda x: x[3], reverse=True)

        # Pick top 1 to 3 distinct informative sentences
        selected_lines = []
        seen_texts = set()
        for s_clean, doc_id, chunk_id, _ in candidate_sentences:
            # Normalize to avoid duplicate sentences
            norm = s_clean.lower()[:40]
            if norm in seen_texts:
                continue
            seen_texts.add(norm)
            citation = f"[{doc_id}:{chunk_id}]"
            selected_lines.append(f"{s_clean} {citation}")
            if len(selected_lines) >= 3:
                break

        final_answer = " ".join(selected_lines)
        return final_answer, ResponseStatus.ANSWERED


class GeminiGenerator(BaseGenerator):
    """Google Gemini GenAI generator with strict grounding prompt and error resilience."""

    CANONICAL_REFUSAL = (
        "INSUFFICIENT EVIDENCE: The available knowledge base does not contain "
        "enough information to answer this question reliably."
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.0
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.temperature = temperature

    def check_availability(self) -> Tuple[bool, str]:
        """Verify API key presence and live access."""
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return False, "GEMINI_API_KEY is not configured or is a placeholder."

        # Quick connectivity test
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}?key={self.api_key}"
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    return True, "Gemini API accessible."
                elif res.status_code == 403:
                    return False, f"403 PERMISSION_DENIED: {res.text}"
                else:
                    return False, f"HTTP {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"Connection error: {e}"

    def generate_answer(
        self,
        query: str,
        context: str,
        retrieved_chunks: List[RetrievedChunk],
        conflict: Optional[ConflictEvidence] = None
    ) -> Tuple[str, ResponseStatus]:
        if not self.api_key:
            logger.warning("Gemini API key missing; falling back to GENERATION_UNAVAILABLE.")
            return (
                "GENERATION UNAVAILABLE: GEMINI_API_KEY is not set. Use mock mode or configure API key.",
                ResponseStatus.GENERATION_UNAVAILABLE
            )

        # 1. Explicit conflict override
        if conflict:
            items_text = [f"- [{i.document_id}:{i.chunk_id}]: {i.statement}" for i in conflict.items]
            answer = (
                f"CONFLICT DETECTED: Contradictory evidence exists in the knowledge base regarding '{conflict.topic}'.\n\n"
                f"{conflict.description}\n\n"
                "Documented contradictions:\n" + "\n".join(items_text)
            )
            return answer, ResponseStatus.CONFLICT_DETECTED

        # 2. Insufficient context check
        if not retrieved_chunks or not context.strip():
            return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE

        # Format prompt
        prompt = (
            f"You are the AegisCore Grounded Technical Assistant. "
            f"Answer the query using ONLY the provided evidence passages. "
            f"Every factual claim MUST cite its source chunk ID using format [DOC-XXX:CHUNK_ID]. "
            f"If the evidence is not sufficient to answer, reply strictly with: '{self.CANONICAL_REFUSAL}'\n\n"
            f"EVIDENCE CONTEXT:\n{context}\n\n"
            f"USER QUERY: {query}\n\n"
            f"ANSWER:"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 512
            }
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 403:
                    logger.error(f"Gemini API 403 PERMISSION_DENIED: {res.text}")
                    return (
                        "GENERATION UNAVAILABLE: 403 PERMISSION_DENIED from Google Gemini API.",
                        ResponseStatus.GENERATION_UNAVAILABLE
                    )
                elif res.status_code != 200:
                    logger.error(f"Gemini API error {res.status_code}: {res.text}")
                    return (
                        f"GENERATION UNAVAILABLE: Provider error HTTP {res.status_code}.",
                        ResponseStatus.GENERATION_UNAVAILABLE
                    )

                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

                if "INSUFFICIENT EVIDENCE" in raw_text.upper():
                    return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE
                if "CONFLICT DETECTED" in raw_text.upper():
                    return raw_text, ResponseStatus.CONFLICT_DETECTED

                return raw_text, ResponseStatus.ANSWERED
        except Exception as e:
            logger.error(f"Gemini call failed with exception: {e}")
            return (
                f"GENERATION UNAVAILABLE: Error contacting provider: {e}",
                ResponseStatus.GENERATION_UNAVAILABLE
            )


class OpenAICompatibleGenerator(BaseGenerator):
    """OpenAI-compatible generator supporting xAI Grok and Groq Cloud."""

    CANONICAL_REFUSAL = (
        "INSUFFICIENT EVIDENCE: The available knowledge base does not contain "
        "enough information to answer this question reliably."
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.x.ai/v1/chat/completions",
        model_name: str = "grok-beta",
        provider_name: str = "xAI Grok",
        temperature: float = 0.0,
        max_tokens: int = 512
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.provider_name = provider_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def check_availability(self) -> Tuple[bool, str]:
        if not self.api_key or "your_" in self.api_key:
            return False, f"API key for {self.provider_name} is missing or placeholder."
        return True, f"{self.provider_name} configured with model {self.model_name}."

    def generate_answer(
        self,
        query: str,
        context: str,
        retrieved_chunks: List[RetrievedChunk],
        conflict: Optional[ConflictEvidence] = None
    ) -> Tuple[str, ResponseStatus]:
        if not self.api_key:
            logger.warning(f"{self.provider_name} API key missing; falling back to GENERATION_UNAVAILABLE.")
            return (
                f"GENERATION UNAVAILABLE: API key for {self.provider_name} is not set.",
                ResponseStatus.GENERATION_UNAVAILABLE
            )

        # 1. Conflict handling
        if conflict:
            items_text = [f"- [{i.document_id}:{i.chunk_id}]: {i.statement}" for i in conflict.items]
            answer = (
                f"CONFLICT DETECTED: Contradictory evidence exists in the knowledge base regarding '{conflict.topic}'.\n\n"
                f"{conflict.description}\n\n"
                "Documented contradictions:\n" + "\n".join(items_text)
            )
            return answer, ResponseStatus.CONFLICT_DETECTED

        # 2. Insufficient context check
        if not retrieved_chunks or not context.strip():
            return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE

        # Format system prompt and user prompt
        system_msg = (
            "You are the AegisCore Grounded Technical Assistant. "
            "Your mandate is to answer technical questions using ONLY the facts explicitly stated in the provided evidence passages. "
            "Do not extrapolate, infer unstated assumptions, or utilize external world knowledge. "
            "Every factual claim must cite its source chunk ID using the exact format [DOC-XXX:CHUNK_ID]. "
            f"If the context does not contain sufficient factual evidence to answer directly, reply strictly with: '{self.CANONICAL_REFUSAL}'\n"
            "If conflicting evidence is present between sources, state 'CONFLICT DETECTED' and outline the contradictory facts."
        )

        user_msg = (
            f"EVIDENCE CONTEXT:\n{context}\n\n"
            f"USER QUERY: {query}\n\n"
            "ANSWER:"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(self.base_url, headers=headers, json=payload)
                if res.status_code == 401:
                    logger.error(f"{self.provider_name} 401 Unauthorized: {res.text}")
                    return (
                        f"GENERATION UNAVAILABLE: 401 Unauthorized for {self.provider_name}. Please verify your API key.",
                        ResponseStatus.GENERATION_UNAVAILABLE
                    )
                elif res.status_code != 200:
                    logger.error(f"{self.provider_name} HTTP {res.status_code}: {res.text}")
                    return (
                        f"GENERATION UNAVAILABLE: {self.provider_name} returned error HTTP {res.status_code}.",
                        ResponseStatus.GENERATION_UNAVAILABLE
                    )

                data = res.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

                if "INSUFFICIENT EVIDENCE" in raw_text.upper():
                    return self.CANONICAL_REFUSAL, ResponseStatus.INSUFFICIENT_EVIDENCE
                if "CONFLICT DETECTED" in raw_text.upper():
                    return raw_text, ResponseStatus.CONFLICT_DETECTED

                return raw_text, ResponseStatus.ANSWERED
        except Exception as e:
            logger.error(f"{self.provider_name} call failed: {e}")
            return (
                f"GENERATION UNAVAILABLE: Error contacting {self.provider_name}: {e}",
                ResponseStatus.GENERATION_UNAVAILABLE
            )


class GrokGenerator(OpenAICompatibleGenerator):
    """xAI Grok generator with strict grounding and citation attribution."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "grok-beta",
        temperature: float = 0.0
    ):
        key = api_key or os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("XAI_API_KEY")
        # Auto-detect if key is a Groq Cloud key (starts with gsk_)
        if key and key.startswith("gsk_"):
            base_url = "https://api.groq.com/openai/v1/chat/completions"
            provider = "Groq Cloud"
            model = "llama-3.3-70b-versatile" if model_name == "grok-beta" else model_name
        else:
            base_url = "https://api.x.ai/v1/chat/completions"
            provider = "xAI Grok"
            model = model_name

        super().__init__(
            api_key=key,
            base_url=base_url,
            model_name=model,
            provider_name=provider,
            temperature=temperature
        )


class GroqGenerator(OpenAICompatibleGenerator):
    """Groq Cloud generator for high-speed inference (e.g. Llama-3.3-70b)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.0
    ):
        key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        # Auto-detect if key is an xAI Grok key (starts with xai-)
        if key and key.startswith("xai-"):
            base_url = "https://api.x.ai/v1/chat/completions"
            provider = "xAI Grok"
            model = "grok-beta" if model_name == "llama-3.3-70b-versatile" else model_name
        else:
            base_url = "https://api.groq.com/openai/v1/chat/completions"
            provider = "Groq Cloud"
            model = model_name

        super().__init__(
            api_key=key,
            base_url=base_url,
            model_name=model,
            provider_name=provider,
            temperature=temperature
        )


def create_generator(config: GenerationConfig) -> BaseGenerator:
    """Instantiate the configured generator."""
    mode = config.mode.lower()
    if mode in ("grok", "xai"):
        return GrokGenerator(
            model_name=config.grok_model,
            temperature=config.temperature
        )
    elif mode == "groq":
        return GroqGenerator(
            model_name=config.groq_model,
            temperature=config.temperature
        )
    elif mode == "gemini":
        return GeminiGenerator(
            model_name=config.gemini_model,
            temperature=config.temperature
        )
    elif mode in ("online", "auto"):
        # Auto-detect provider based on available keys
        groq_k = os.getenv("GROQ_API_KEY")
        grok_k = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        gemini_k = os.getenv("GEMINI_API_KEY")

        if groq_k or (grok_k and grok_k.startswith("gsk_")):
            return GroqGenerator(model_name=config.groq_model, temperature=config.temperature)
        elif grok_k:
            return GrokGenerator(model_name=config.grok_model, temperature=config.temperature)
        elif gemini_k:
            return GeminiGenerator(model_name=config.gemini_model, temperature=config.temperature)

    # Default is always deterministic offline mock generator
    return DeterministicMockGenerator()

