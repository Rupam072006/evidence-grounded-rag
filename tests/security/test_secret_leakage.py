"""Security tests for secret masking in logs and environment isolation."""
import logging
import pytest
from evidence_rag.logging_config import SecretMaskingFilter


def test_secret_masking_filter_scrubs_api_keys():
    filter_obj = SecretMaskingFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Connecting with key AIzaSyD84kd93kd938slkd93kdls03kd9slkd8s and Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        args=(),
        exc_info=None
    )

    filter_obj.filter(record)
    assert "AIzaSy" not in record.msg
    assert "[REDACTED_API_KEY]" in record.msg
    assert "Bearer [REDACTED_TOKEN]" in record.msg
