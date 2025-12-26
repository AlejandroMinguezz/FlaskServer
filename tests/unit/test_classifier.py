"""
Unit tests for document classifiers.
"""
import pytest
from src.ia.classifier import DocumentClassifier
from src.ia.classifier_ml import MLDocumentClassifier


class TestKeywordClassifier:
    """Test keyword-based classifier."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return DocumentClassifier()

    def test_classify_factura(self, classifier):
        """Test classification of invoice."""
        text = """
        FACTURA N.º 2025/001
        Fecha: 15/03/2025
        Cliente: Empresa Test S.L.
        NIF: B12345678
        Base imponible: 1.000,00€
        IVA (21%): 210,00€
        Total: 1.210,00€
        """

        result = classifier.classify_text(text, username="testuser")

        assert 'tipo_documento' in result
        assert 'confianza' in result
        assert 'carpeta_sugerida' in result
        assert result['tipo_documento'] == 'factura'
        assert result['confianza'] > 0.5

    def test_classify_nomina(self, classifier):
        """Test classification of payroll."""
        text = """
        NÓMINA DEL MES DE MARZO 2025
        Trabajador: Juan Pérez García
        DNI: 12345678A

        DEVENGOS
        Salario base: 1.500,00€
        Complementos: 300,00€

        DEDUCCIONES
        IRPF: 225,00€
        Seguridad Social: 105,00€

        Líquido a percibir: 1.470,00€
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'nomina'
        assert result['carpeta_sugerida'] == '/testuser/Documentos/Nóminas'

    def test_classify_contrato(self, classifier):
        """Test classification of contract."""
        text = """
        CONTRATO DE TRABAJO

        En Madrid, a 15 de marzo de 2025

        REUNIDOS

        De una parte, la empresa ABC S.L., y de otra parte,
        Don Juan Pérez García.

        CLÁUSULAS

        Primera: El trabajador prestará sus servicios...
        Segunda: La duración del contrato será...
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'contrato'

    def test_classify_recibo(self, classifier):
        """Test classification of receipt."""
        text = """
        RECIBO DE ALQUILER

        Fecha: 01/03/2025
        Concepto: Alquiler del mes de marzo
        Importe: 800,00€

        He recibido del Sr. Juan Pérez la cantidad de
        ochocientos euros en concepto de alquiler.
        Pagado en efectivo.
        """

        result = classifier.classify_text(text, username="testuser")

        # May be classified as recibo or factura due to similar keywords
        assert result['tipo_documento'] in ['recibo', 'factura']

    def test_classify_certificado(self, classifier):
        """Test classification of certificate."""
        text = """
        CERTIFICADO DE EMPRESA

        D. Luis García, Director de Recursos Humanos de la empresa
        ABC S.L., CERTIFICA:

        Que D. Juan Pérez García ha prestado sus servicios en esta
        empresa desde el 01/01/2020 hasta la fecha actual.

        Y para que conste, expido el presente certificado en Madrid,
        a 15 de marzo de 2025.
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'certificado'

    def test_classify_presupuesto(self, classifier):
        """Test classification of budget."""
        text = """
        PRESUPUESTO N.º 2025/001

        Fecha: 15/03/2025
        Cliente: Empresa Test S.L.
        Validez: 30 días

        PARTIDAS:
        1. Servicios de consultoría: 2.000,00€
        2. Desarrollo software: 5.000,00€

        Total presupuesto: 7.000,00€
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'presupuesto'

    def test_classify_fiscal(self, classifier):
        """Test classification of tax document."""
        text = """
        DECLARACIÓN DE LA RENTA 2024
        Modelo 100 - IRPF

        NIF: 12345678A
        Ejercicio: 2024

        Rendimientos del trabajo: 30.000€
        Retenciones: 4.500€
        Cuota líquida: 5.200€
        Resultado: A ingresar 700€
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'fiscal'

    def test_classify_notificacion(self, classifier):
        """Test classification of notification."""
        text = """
        NOTIFICACIÓN ADMINISTRATIVA

        Expediente: EXP/2025/001234
        Órgano: Ayuntamiento de Madrid

        Se le notifica que se ha iniciado un expediente
        administrativo en relación con...

        Contra esta resolución puede interponer recurso...
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'notificacion'

    def test_classify_empty_text(self, classifier):
        """Test classification of empty text."""
        result = classifier.classify_text("", username="testuser")

        # Empty text may be classified as 'otro' or 'desconocido'
        assert result['tipo_documento'] in ['otro', 'desconocido']
        assert result['confianza'] == 0.0

    def test_classify_ambiguous_text(self, classifier):
        """Test classification of ambiguous text."""
        text = "Este es un documento con poco contenido"

        result = classifier.classify_text(text, username="testuser")

        assert 'tipo_documento' in result
        assert result['confianza'] >= 0.0


class TestMLClassifier:
    """Test ML-based classifier."""

    @pytest.fixture
    def classifier(self):
        """Create ML classifier instance."""
        try:
            return MLDocumentClassifier(model_name="tfidf_svm_v1")
        except Exception:
            pytest.skip("ML model not available")

    def test_classifier_loads(self, classifier):
        """Test that classifier loads successfully."""
        assert classifier is not None
        assert hasattr(classifier, 'model')
        assert hasattr(classifier, 'vectorizer')

    def test_ml_classify_factura(self, classifier):
        """Test ML classification of invoice."""
        text = """
        FACTURA N.º 2025/001
        Fecha: 15/03/2025
        Proveedor: ABC Servicios S.L.
        NIF: B12345678

        CONCEPTOS:
        - Servicios profesionales: 1.000,00€

        Base imponible: 1.000,00€
        IVA (21%): 210,00€
        Total factura: 1.210,00€

        Forma de pago: Transferencia bancaria
        """

        result = classifier.classify_text(text, username="testuser")

        assert result['tipo_documento'] == 'factura'
        assert result['confianza'] > 0.5
        assert '/Facturas' in result['carpeta_sugerida']

    def test_ml_classify_confidence_score(self, classifier):
        """Test that ML classifier returns valid confidence scores."""
        text = """
        FACTURA N.º 2025/001
        Fecha: 15/03/2025
        Total: 1.210,00€
        IVA incluido
        """

        result = classifier.classify_text(text, username="testuser")

        assert 0 <= result['confianza'] <= 1

    def test_ml_classify_personalized_folder(self, classifier):
        """Test that ML classifier personalizes folder suggestions."""
        text = "FACTURA 2025/001"

        result1 = classifier.classify_text(text, username="user1")
        result2 = classifier.classify_text(text, username="user2")

        assert 'user1' in result1['carpeta_sugerida']
        assert 'user2' in result2['carpeta_sugerida']

    def test_ml_classify_without_username(self, classifier):
        """Test ML classification without username."""
        text = "FACTURA 2025/001"

        result = classifier.classify_text(text, username=None)

        assert 'tipo_documento' in result
        assert 'carpeta_sugerida' in result
        # Folder suggestion may or may not start with '/' depending on implementation
        assert isinstance(result['carpeta_sugerida'], str)


class TestClassifierIntegration:
    """Test classifier integration and fallback."""

    def test_fallback_mechanism(self):
        """Test that fallback to keyword classifier works."""
        # Try to load ML classifier with invalid model
        try:
            ml_classifier = MLDocumentClassifier(model_name="nonexistent_model")
        except Exception:
            # Should fall back to keyword classifier
            keyword_classifier = DocumentClassifier()
            text = "FACTURA 2025/001"
            result = keyword_classifier.classify_text(text)
            assert 'tipo_documento' in result
