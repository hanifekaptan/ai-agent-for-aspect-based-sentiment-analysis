"""
Unit tests for app/utils/sanitizer.py

Tests cover:
- sanitize_comment: overall sanitization pipeline
- Edge cases: long text, special characters, delimiters
"""
import pytest
from app.utils.sanitizer import sanitize_comment, _normalize_comment, _truncate_comment, _escape_delimiters


class TestSanitizeComment:
    """Test main sanitize_comment function."""

    def test_sanitize_basic_text(self):
        """Test basic text sanitization."""
        result = sanitize_comment("Hello world")
        assert result == "Hello world"

    def test_sanitize_extra_whitespace(self):
        """Test removal of extra whitespace."""
        result = sanitize_comment("Hello    world   test")
        assert "    " not in result
        assert result == "Hello world test"

    def test_sanitize_newlines(self):
        """Test newline normalization."""
        result = sanitize_comment("Line1\r\nLine2\nLine3")
        # Newlines should be replaced with spaces
        assert '\n' not in result
        assert 'Line1' in result and 'Line2' in result

    def test_sanitize_truncation(self):
        """Test text truncation at max_length."""
        long_text = "a" * 500
        result = sanitize_comment(long_text, max_length=100)
        assert len(result) <= 100

    def test_sanitize_delimiter_escape(self):
        """Test that L: delimiter is escaped."""
        result = sanitize_comment("L:test L:another")
        assert "L:" not in result
        assert "L\\:" in result

    def test_sanitize_unicode_normalization(self):
        """Test Unicode NFKC normalization."""
        text = "café"  # with combining accent
        result = sanitize_comment(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sanitize_empty_string(self):
        """Test empty string input."""
        result = sanitize_comment("")
        assert result == ""

    def test_sanitize_only_whitespace(self):
        """Test string with only whitespace."""
        result = sanitize_comment("   \t\n   ")
        assert result == ""


class TestNormalizeComment:
    """Test _normalize_comment helper."""

    def test_normalize_nfkc(self):
        """Test NFKC Unicode normalization."""
        result = _normalize_comment("test")
        assert isinstance(result, str)

    def test_normalize_multiple_newlines(self):
        """Test multiple consecutive newlines reduction."""
        result = _normalize_comment("Line1\n\n\nLine2")
        assert "\n\n\n" not in result

    def test_normalize_tabs_to_spaces(self):
        """Test tab conversion to spaces."""
        result = _normalize_comment("Hello\tworld")
        assert '\t' not in result
        assert ' ' in result

    def test_normalize_strips_ends(self):
        """Test leading/trailing whitespace removal."""
        result = _normalize_comment("  text  ")
        assert result == "text"


class TestTruncateComment:
    """Test _truncate_comment helper."""

    def test_truncate_short_text(self):
        """Test text shorter than max_length."""
        text = "Short text"
        result = _truncate_comment(text, max_length=100)
        assert result == text

    def test_truncate_at_word_boundary(self):
        """Test truncation at word boundary."""
        text = "This is a long text that needs truncation"
        result = _truncate_comment(text, max_length=20)
        assert len(result) <= 20
        # Should not end with partial word (soft cut)
        assert not result.endswith("lo")

    def test_truncate_hard_cut_no_space(self):
        """Test hard cut when no space before max_length."""
        text = "verylongtextwithoutspaces" * 10
        result = _truncate_comment(text, max_length=50)
        assert len(result) <= 50

    def test_truncate_exact_length(self):
        """Test text exactly at max_length."""
        text = "a" * 100
        result = _truncate_comment(text, max_length=100)
        assert len(result) == 100


class TestEscapeDelimiters:
    """Test _escape_delimiters helper."""

    def test_escape_l_colon(self):
        """Test L: escaping."""
        result = _escape_delimiters("L:test")
        assert "L\\:" in result
        assert "L:" not in result

    def test_escape_control_characters(self):
        """Test control character removal."""
        text = "Hello\x00\x01\x1fWorld"
        result = _escape_delimiters(text)
        assert '\x00' not in result
        assert '\x01' not in result
        assert 'Hello' in result

    def test_escape_newlines_to_spaces(self):
        """Test newline conversion to spaces."""
        result = _escape_delimiters("Line1\nLine2")
        assert '\n' not in result
        assert ' ' in result

    def test_escape_multiple_l_colons(self):
        """Test multiple L: occurrences."""
        result = _escape_delimiters("L:one L:two L:three")
        assert result.count("L\\:") == 3
        assert "L:" not in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_text_performance(self):
        """Test sanitization doesn't hang on very long text."""
        text = "word " * 10000
        result = sanitize_comment(text, max_length=500)
        assert len(result) <= 500

    def test_special_unicode_characters(self):
        """Test various Unicode characters."""
        text = "Emoji 😀 Turkish çğıöşü Arabic مرحبا"
        result = sanitize_comment(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mixed_line_endings(self):
        """Test mixed CR, LF, CRLF."""
        text = "Line1\rLine2\nLine3\r\nLine4"
        result = sanitize_comment(text)
        assert '\r' not in result
        assert '\n' not in result
