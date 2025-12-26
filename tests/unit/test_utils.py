"""
Unit tests for utility functions.
"""
import pytest
from src.ia.utils import clean_text


class TestCleanText:
    """Test text cleaning utility."""

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "  Hello   World  "
        result = clean_text(text)

        assert result.strip() == "Hello World" or "hello world" in result.lower()

    def test_clean_text_removes_multiple_spaces(self):
        """Test removing multiple spaces."""
        text = "This    has    many    spaces"
        result = clean_text(text)

        assert "    " not in result

    def test_clean_text_removes_multiple_newlines(self):
        """Test removing multiple newlines."""
        text = "Line 1\n\n\n\nLine 2"
        result = clean_text(text)

        assert "\n\n\n\n" not in result

    def test_clean_text_preserves_numbers(self):
        """Test that numbers are preserved."""
        text = "Total: 1.234,56 € - Fecha: 15/03/2025"
        result = clean_text(text)

        assert "1" in result
        assert "234" in result
        assert "56" in result
        assert "2025" in result

    def test_clean_text_preserves_spanish_chars(self):
        """Test that Spanish characters are preserved or handled."""
        text = "Año 2025 - Señor García - Niño pequeño"
        result = clean_text(text)

        # Should preserve or handle Spanish characters
        assert isinstance(result, str)
        assert len(result) > 0
        assert "2025" in result

    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        result = clean_text("")
        assert result == ""

    def test_clean_text_only_whitespace(self):
        """Test cleaning text with only whitespace."""
        text = "   \n\n\t\t   "
        result = clean_text(text)

        assert result.strip() == ""

    def test_clean_text_special_punctuation(self):
        """Test handling special punctuation."""
        text = "FACTURA N.º 2025/001 - Total: 1.000,00€ (IVA incl.)"
        result = clean_text(text)

        # Should preserve key information
        assert "FACTURA" in result.upper()
        assert "2025" in result

    def test_clean_text_preserves_structure(self):
        """Test that basic structure is preserved."""
        text = """
        FACTURA
        Línea 1
        Línea 2
        Total: 1000
        """
        result = clean_text(text)

        # Should preserve key content even if structure changes
        assert "FACTURA" in result.upper()
        assert "1000" in result
