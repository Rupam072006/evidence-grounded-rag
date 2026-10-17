"""Structured, secret-free logging configuration for Evidence-Grounded RAG."""
import logging
import re
import os
from pathlib import Path
from typing import Optional


class SecretMaskingFilter(logging.Filter):
    """Filter to redact API keys, tokens, and secrets from all log records."""

    PATTERNS = [
        # Match potential Gemini / Google API keys: AIzaSy...
        (re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"), "[REDACTED_API_KEY]"),
        # Match Bearer tokens
        (re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{10,}", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
        # Match generic API key strings
        (re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{8,})['\"]?"), r"\1=[REDACTED]"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        if record.args:
            args_list = list(record.args) if isinstance(record.args, tuple) else record.args
            if isinstance(args_list, list):
                for idx, arg in enumerate(args_list):
                    if isinstance(arg, str):
                        for pattern, replacement in self.PATTERNS:
                            args_list[idx] = pattern.sub(replacement, arg)
                record.args = tuple(args_list)
        return True


def setup_logger(
    name: str = "evidence_rag",
    level: str = "INFO",
    log_file: Optional[str] = "logs/rag_system.log"
) -> logging.Logger:
    """Configure and return a structured, secret-safe logger."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    secret_filter = SecretMaskingFilter()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(secret_filter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(secret_filter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
