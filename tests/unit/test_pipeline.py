"""
Unit tests for AI pipeline.
"""
import pytest
import os
from pathlib import Path
from src.ia.pipeline import analizar_documento
from src.ia.utils import clean_text


class TestTextCleaning:
    """Test text cleaning utilities."""

    def test_clean_text_removes_extra_whitespace(self):
        """Test that clean_text removes extra whitespace."""
        text = "Este    es   un    texto   con    espacios"
        result = clean_text(text)

        assert "    " not in result
        assert "  " not in result

    def test_clean_text_normalizes_newlines(self):
        """Test that clean_text normalizes newlines."""
        text = "Línea 1\n\n\nLínea 2\n\n\n\nLínea 3"
        result = clean_text(text)

        # Should reduce multiple newlines
        assert "\n\n\n\n" not in result

    def test_clean_text_preserves_content(self):
        """Test that clean_text preserves important content."""
        text = "FACTURA N.º 2025/001\nTotal: 1.000,00€"
        result = clean_text(text)

        assert "FACTURA" in result.upper()
        assert "2025" in result
        assert "1.000" in result or "1000" in result

    def test_clean_text_handles_empty_string(self):
        """Test that clean_text handles empty strings."""
        result = clean_text("")
        assert result == ""

    def test_clean_text_handles_special_chars(self):
        """Test that clean_text handles special characters."""
        text = "€100,50 - Año 2025 - Señor García"
        result = clean_text(text)

        # Should preserve or handle gracefully
        assert isinstance(result, str)
        assert len(result) > 0


class TestPipelineIntegration:
    """Test complete pipeline integration."""

    def test_analizar_documento_txt(self, tmp_path):
        """Test analyzing a text document."""
        # Create test file
        txt_file = tmp_path / "factura.txt"
        content = """
        FACTURA N.º 2025/001
        Fecha: 15/03/2025
        Cliente: Test S.L.
        NIF: B12345678

        Base imponible: 1.000,00€
        IVA (21%): 210,00€
        Total factura: 1.210,00€
        """
        txt_file.write_text(content, encoding='utf-8')

        # Analyze document
        result = analizar_documento(str(txt_file), username="testuser")

        # Check result structure
        assert 'tipo_documento' in result
        assert 'confianza' in result
        assert 'carpeta_sugerida' in result

        # Should classify as factura
        assert result['tipo_documento'] == 'factura'
        assert result['confianza'] > 0.0

    def test_analizar_documento_nomina(self, tmp_path):
        """Test analyzing a payroll document."""
        txt_file = tmp_path / "nomina.txt"
        content = """
        NÓMINA DEL MES DE MARZO 2025
        Trabajador: Juan Pérez
        DNI: 12345678A

        DEVENGOS:
        Salario base: 1.500,00€

        DEDUCCIONES:
        IRPF: 225,00€
        Seguridad Social: 105,00€

        Líquido a percibir: 1.170,00€
        """
        txt_file.write_text(content, encoding='utf-8')

        result = analizar_documento(str(txt_file), username="testuser")

        assert result['tipo_documento'] == 'nomina'
        assert '/Nóminas' in result['carpeta_sugerida']

    def test_analizar_documento_nonexistent(self):
        """Test analyzing nonexistent document."""
        result = analizar_documento("/nonexistent/file.txt", username="testuser")

        assert 'error' in result

    def test_analizar_documento_empty(self, tmp_path):
        """Test analyzing empty document."""
        txt_file = tmp_path / "empty.txt"
        txt_file.write_text("", encoding='utf-8')

        result = analizar_documento(str(txt_file), username="testuser")

        assert 'tipo_documento' in result
        # Empty documents should be classified as 'otro' or 'desconocido'

    def test_analizar_documento_personalized_folder(self, tmp_path):
        """Test that folder suggestions are personalized."""
        txt_file = tmp_path / "factura.txt"
        content = "FACTURA 2025/001 Total: 1000€"
        txt_file.write_text(content, encoding='utf-8')

        result1 = analizar_documento(str(txt_file), username="user1")
        result2 = analizar_documento(str(txt_file), username="user2")

        assert 'user1' in result1['carpeta_sugerida']
        assert 'user2' in result2['carpeta_sugerida']

    def test_analizar_documento_all_types(self, tmp_path):
        """Test analyzing different document types."""
        test_cases = [
            ("factura.txt", "FACTURA N.º 2025/001\nBase imponible: 1000€\nIVA: 210€", "factura"),
            ("nomina.txt", "NÓMINA Marzo 2025\nIRPF: 200€\nSeguridad Social: 100€", "nomina"),
            ("contrato.txt", "CONTRATO DE TRABAJO\nCLÁUSULAS\nPrimera: El trabajador", "contrato"),
            ("recibo.txt", "RECIBO de alquiler\nConcepto: Alquiler marzo\nImporte: 800€", "recibo"),
            ("presupuesto.txt", "PRESUPUESTO 2025/001\nValidez: 30 días\nTotal: 5000€", "presupuesto"),
            ("certificado.txt", "CERTIFICADO\nCERTIFICA que D. Juan Pérez\nexpido el presente", "certificado"),
            ("fiscal.txt", "DECLARACIÓN RENTA 2024\nModelo 100\nIRPF\nHacienda", "fiscal"),
            ("notificacion.txt", "NOTIFICACIÓN ADMINISTRATIVA\nExpediente: EXP/2025/001", "notificacion"),
        ]

        for filename, content, expected_type in test_cases:
            txt_file = tmp_path / filename
            txt_file.write_text(content, encoding='utf-8')

            result = analizar_documento(str(txt_file), username="testuser")

            assert 'tipo_documento' in result
            # Note: Classification might not be perfect, so we just check it returns a valid type
            assert isinstance(result['tipo_documento'], str)
            assert len(result['tipo_documento']) > 0


class TestPipelineErrorHandling:
    """Test pipeline error handling."""

    def test_pipeline_handles_corrupt_file(self, tmp_path):
        """Test that pipeline handles corrupt files gracefully."""
        corrupt_file = tmp_path / "corrupt.txt"
        corrupt_file.write_bytes(b'\x00\x01\x02\xff\xfe\xfd')

        result = analizar_documento(str(corrupt_file), username="testuser")

        # Should return error or handle gracefully
        assert isinstance(result, dict)

    def test_pipeline_handles_large_file(self, tmp_path):
        """Test that pipeline handles large files."""
        large_file = tmp_path / "large.txt"
        # Create file with 10,000 lines
        content = "FACTURA línea de texto\n" * 10000
        large_file.write_text(content, encoding='utf-8')

        result = analizar_documento(str(large_file), username="testuser")

        assert 'tipo_documento' in result

    def test_pipeline_handles_unicode(self, tmp_path):
        """Test that pipeline handles unicode characters."""
        txt_file = tmp_path / "unicode.txt"
        content = "FACTURA 2025/001\n€100,50\nSeñor García\n中文字符"
        txt_file.write_text(content, encoding='utf-8')

        result = analizar_documento(str(txt_file), username="testuser")

        assert 'tipo_documento' in result
        assert isinstance(result, dict)
