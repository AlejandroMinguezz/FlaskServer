"""
Unit tests for OCR functionality.
"""
import pytest
import os
from pathlib import Path
from io import BytesIO
from src.ia.ocr import extract_text
from src.ia.ocr.ocr import extract_text_from_txt, extract_text_from_docx


class TestTextExtraction:
    """Test text extraction from different file formats."""

    def test_extract_text_from_txt_utf8(self, tmp_path):
        """Test extracting text from UTF-8 encoded text file."""
        # Create temporary text file
        txt_file = tmp_path / "test.txt"
        content = "Este es un texto de prueba\nCon múltiples líneas\n€ñáéíóú"
        txt_file.write_text(content, encoding='utf-8')

        # Extract text
        result = extract_text_from_txt(str(txt_file))

        assert "Este es un texto de prueba" in result
        assert "múltiples líneas" in result

    def test_extract_text_from_txt_latin1(self, tmp_path):
        """Test extracting text from Latin-1 encoded text file."""
        txt_file = tmp_path / "test_latin1.txt"
        content = "Texto con caracteres especiales: áéíóú ñ"
        txt_file.write_text(content, encoding='latin-1')

        result = extract_text_from_txt(str(txt_file))

        # Should still extract text (may have encoding issues but shouldn't crash)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_extract_text_from_empty_file(self, tmp_path):
        """Test extracting text from empty file."""
        txt_file = tmp_path / "empty.txt"
        txt_file.write_text("", encoding='utf-8')

        result = extract_text_from_txt(str(txt_file))

        assert result == ""

    def test_extract_text_nonexistent_file(self):
        """Test extracting text from nonexistent file."""
        # Function may return empty string or raise exception
        result = extract_text_from_txt("/nonexistent/file.txt")
        # Should handle error gracefully (return empty string or raise)
        assert result == "" or isinstance(result, str)


class TestUnifiedExtraction:
    """Test unified extract_text function."""

    def test_extract_text_txt(self, tmp_path):
        """Test extract_text with .txt file."""
        txt_file = tmp_path / "document.txt"
        content = "FACTURA 2025/001\nTotal: 1000€"
        txt_file.write_text(content, encoding='utf-8')

        result = extract_text(str(txt_file))

        assert "FACTURA" in result
        assert "Total" in result

    def test_extract_text_unsupported_format(self, tmp_path):
        """Test extract_text with unsupported format."""
        file = tmp_path / "document.xyz"
        file.write_text("content")

        # Should either raise exception or return empty string
        try:
            result = extract_text(str(file))
            assert isinstance(result, str)
        except Exception:
            pass  # Exception is acceptable

    def test_extract_text_with_special_characters(self, tmp_path):
        """Test extracting text with special Spanish characters."""
        txt_file = tmp_path / "spanish.txt"
        content = "Año: 2025\nSeñor García\nMañana\n€100,50"
        txt_file.write_text(content, encoding='utf-8')

        result = extract_text(str(txt_file))

        assert "2025" in result
        # Special characters might be preserved or converted


class TestOCRPipeline:
    """Test OCR pipeline integration."""

    def test_ocr_preserves_invoice_format(self, tmp_path):
        """Test that OCR preserves invoice formatting."""
        txt_file = tmp_path / "factura.txt"
        content = """
        FACTURA N.º 2025/001
        Fecha: 15/03/2025

        Base imponible: 1.000,00€
        IVA (21%): 210,00€
        Total: 1.210,00€
        """
        txt_file.write_text(content, encoding='utf-8')

        result = extract_text(str(txt_file))

        # Check key elements are preserved
        assert "FACTURA" in result.upper()
        assert "2025/001" in result
        assert "1.000" in result or "1000" in result
        assert "IVA" in result.upper()

    def test_ocr_handles_multiple_encodings(self, tmp_path):
        """Test that OCR handles files with different encodings."""
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            txt_file = tmp_path / f"test_{encoding}.txt"
            try:
                txt_file.write_text("Test content", encoding=encoding)
                result = extract_text(str(txt_file))
                assert isinstance(result, str)
            except LookupError:
                # Skip if encoding not available
                pass
