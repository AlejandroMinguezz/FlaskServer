"""
Test configuration and fixtures for DirectIA tests.
"""
import pytest
import os
import sys
from io import BytesIO
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import create_app
from src.config import Config


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application."""
    # Override config for testing
    class TestConfig(Config):
        TESTING = True
        DEBUG = False
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        MONGO_URI = "mongodb://localhost:27017/directia_test"
        STORAGE_PATH = "./tests/test_data"
        SECRET_KEY = "test-secret-key"

    app = create_app()
    app.config.from_object(TestConfig)

    yield app


@pytest.fixture(scope='session')
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers with valid JWT token."""
    # Register a test user
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!@#'
    })

    # Login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'Test123!@#'
    })

    if response.status_code == 200:
        token = response.json.get('access_token')
        return {'Authorization': f'Bearer {token}'}

    return {}


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    # Simple PDF-like bytes (not a real PDF, just for testing file handling)
    pdf_content = b'%PDF-1.4\nSample PDF content for testing'
    return BytesIO(pdf_content)


@pytest.fixture
def sample_txt():
    """Create a sample text file for testing."""
    txt_content = """
    FACTURA N.º 2025/001

    Fecha: 15/03/2025
    Cliente: Empresa Test S.L.
    NIF: B12345678

    Concepto: Servicios de consultoría
    Base imponible: 1.000,00€
    IVA (21%): 210,00€
    Total: 1.210,00€
    """
    return BytesIO(txt_content.encode('utf-8'))


@pytest.fixture
def sample_docx():
    """Create a sample DOCX file for testing."""
    # Minimal DOCX structure (simplified)
    docx_content = b'PK\x03\x04' + b'\x00' * 100  # Minimal ZIP header
    return BytesIO(docx_content)


@pytest.fixture
def cleanup_test_files():
    """Cleanup test files after tests."""
    yield
    # Cleanup logic
    test_data_dir = Path("./tests/test_data")
    if test_data_dir.exists():
        for file in test_data_dir.glob("*"):
            if file.is_file():
                file.unlink()
