"""Text cleaning, Unicode normalization, markup sanitization, and PII redaction."""
import re
import unicodedata
from evidence_rag.config import CleaningConfig


class TextCleaner:
    """Sanitizes text by stripping control characters, normalizing Unicode, and removing markup."""

    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
    SCRIPT_TAG_PATTERN = re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL)
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    API_KEY_PATTERN = re.compile(r"\b(sk-[A-Za-z0-9]{20,}|AIzaSy[A-Za-z0-9_-]{33})\b")

    def __init__(self, config: CleaningConfig = None):
        self.config = config or CleaningConfig()

    def clean(self, text: str) -> str:
        """Execute full cleaning pipeline on input text."""
        if not text or not isinstance(text, str):
            return ""

        result = text

        # 1. Unicode Normalization (NFKC)
        if self.config.normalize_unicode:
            result = unicodedata.normalize("NFKC", result)

        # 2. Strip Script and HTML Tags
        if self.config.strip_external_tags:
            result = self.SCRIPT_TAG_PATTERN.sub(" ", result)
            result = self.HTML_TAG_PATTERN.sub(" ", result)

        # 3. Remove Control Characters (keep \t, \n, \r)
        if self.config.remove_control_characters:
            result = "".join(
                ch for ch in result
                if unicodedata.category(ch)[0] != "C" or ch in ("\t", "\n", "\r")
            )

        # 4. Redact PII / Secrets
        result = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", result)
        result = self.API_KEY_PATTERN.sub("[REDACTED_KEY]", result)

        # 5. Whitespace Consolidation
        if self.config.collapse_whitespace:
            # Standardize line endings to \n
            result = result.replace("\r\n", "\n").replace("\r", "\n")
            # Collapse multiple spaces or tabs on a single line
            result = re.sub(r"[ \t]+", " ", result)
            # Standardize paragraph breaks: max 2 consecutive newlines
            result = re.sub(r"\n{3,}", "\n\n", result)
            result = result.strip()

        return result


def clean_text(text: str, config: CleaningConfig = None) -> str:
    """Convenience helper to clean text using default or custom config."""
    cleaner = TextCleaner(config)
    return cleaner.clean(text)
