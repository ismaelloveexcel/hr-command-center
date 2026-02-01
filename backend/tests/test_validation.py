"""Tests for input validation utilities."""

from app.core.validation import (
    sanitize_html,
    sanitize_text,
    validate_reference_format,
    validate_email
)


class TestSanitization:
    """Tests for HTML and text sanitization."""
    
    def test_sanitize_html_removes_script_tags(self):
        """Test that script tags are removed."""
        text = "<script>alert('xss')</script>Hello"
        result = sanitize_html(text)
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_html_removes_all_tags(self):
        """Test that all HTML tags are removed."""
        text = "<b>Bold</b> <i>italic</i> <a href='link'>link</a>"
        result = sanitize_html(text)
        assert "<b>" not in result
        assert "<i>" not in result
        assert "<a" not in result
        assert "Bold italic link" in result
    
    def test_sanitize_html_handles_none(self):
        """Test that None input returns None."""
        assert sanitize_html(None) is None
    
    def test_sanitize_text_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        text = "  Hello World  "
        result = sanitize_text(text)
        assert result == "Hello World"
    
    def test_sanitize_text_enforces_max_length(self):
        """Test that max length is enforced."""
        text = "a" * 100
        result = sanitize_text(text, max_length=50)
        assert len(result) == 50
    
    def test_sanitize_text_removes_html(self):
        """Test that HTML is removed from text."""
        text = "<div>Hello</div>"
        result = sanitize_text(text)
        assert "<div>" not in result
        assert "Hello" in result


class TestReferenceValidation:
    """Tests for reference format validation."""
    
    def test_valid_reference(self):
        """Test valid reference format."""
        assert validate_reference_format("REF-2024-001") is True
        assert validate_reference_format("REF-2026-999") is True
    
    def test_invalid_reference_format(self):
        """Test invalid reference formats."""
        assert validate_reference_format("REF-24-001") is False  # Wrong year format
        assert validate_reference_format("REF-2024-1") is False  # Wrong number format
        assert validate_reference_format("REF20240001") is False  # No dashes
        assert validate_reference_format("ref-2024-001") is False  # Lowercase
        assert validate_reference_format("XYZ-2024-001") is False  # Wrong prefix


class TestEmailValidation:
    """Tests for email validation."""
    
    def test_valid_emails(self):
        """Test valid email formats."""
        assert validate_email("user@example.com") is True
        assert validate_email("john.doe@company.ae") is True
        assert validate_email("test+tag@domain.co.uk") is True
    
    def test_invalid_emails(self):
        """Test invalid email formats."""
        assert validate_email("notanemail") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user @example.com") is False  # Space
        assert validate_email("user@example") is False  # No TLD
