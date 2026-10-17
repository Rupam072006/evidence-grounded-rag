"""Unit tests for text cleaning, sanitization, and PII redaction."""
import pytest
from evidence_rag.cleaning import TextCleaner, clean_text
from evidence_rag.config import CleaningConfig


def test_clean_text_normalizes_unicode():
    # NFKC converts ligatures (e.g. \ufb01 -> fi)
    text = "The o\ufb03ce speci\ufb01cation."
    cleaned = clean_text(text)
    assert "office" in cleaned
    assert "specification" in cleaned


def test_clean_text_strips_control_characters():
    # Control character ASCII 07 (bell), 00 (null), 1b (esc)
    text = "Valid text\x00 with bell\x07 and esc\x1b."
    cleaned = clean_text(text)
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "\x1b" not in cleaned
    assert "Valid text with bell and esc." == cleaned


def test_clean_text_preserves_tabs_and_newlines():
    text = "Header Line\n\nParagraph with\ttab."
    cleaned = clean_text(text)
    assert "Header Line\n\nParagraph with tab." == cleaned or "Header Line\n\nParagraph with\ttab." == cleaned


def test_clean_text_strips_html_and_script_tags():
    text = (
        "Document title <h1>Header</h1>"
        "<script>alert('malicious injection');</script>"
        "<p>Sanitized paragraph.</p>"
    )
    cleaned = clean_text(text)
    assert "<script>" not in cleaned
    assert "alert('malicious injection')" not in cleaned
    assert "<h1>" not in cleaned
    assert "<p>" not in cleaned
    assert "Document title Header Sanitized paragraph." in cleaned


def test_clean_text_redacts_pii_and_keys():
    text = (
        "Contact engineer at alice.smith@company.org regarding key "
        "AIzaSyD84kd93kd938slkd93kdls03kd9slkd8s."
    )
    cleaned = clean_text(text)
    assert "alice.smith@company.org" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "AIzaSy" not in cleaned
    assert "[REDACTED_KEY]" in cleaned


def test_clean_text_empty_and_whitespace():
    assert clean_text("") == ""
    assert clean_text("   \n\t  ") == ""
    assert clean_text(None) == ""
