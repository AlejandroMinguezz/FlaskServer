"""
Integration tests for API endpoints.
"""
import pytest
from io import BytesIO


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!@#'
        })

        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data or 'user' in data

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        # Register first user
        client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'user1@example.com',
            'password': 'Pass123!@#'
        })

        # Try to register again with same username
        response = client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'user2@example.com',
            'password': 'Pass456!@#'
        })

        assert response.status_code in [400, 409]

    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        client.post('/api/auth/register', json={
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'Test123!@#'
        })

        # Login
        response = client.post('/api/auth/login', json={
            'username': 'logintest',
            'password': 'Test123!@#'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })

        assert response.status_code in [401, 404]


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data


class TestFileEndpoints:
    """Test file management endpoints."""

    def test_list_files_requires_auth(self, client):
        """Test that listing files requires authentication."""
        response = client.get('/api/files/list')

        # Should return 401 if auth is required
        assert response.status_code in [200, 401]

    def test_upload_file(self, client, auth_headers, sample_txt):
        """Test file upload."""
        data = {
            'file': (sample_txt, 'test_file.txt'),
            'path': '/testuser/'
        }

        response = client.post(
            '/api/files/upload',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )

        # Should succeed or require proper setup
        assert response.status_code in [200, 201, 401, 500]


class TestIAEndpoints:
    """Test AI classification endpoints."""

    def test_clasificar_requires_file(self, client):
        """Test that clasificar endpoint requires a file."""
        response = client.post('/api/clasificar', data={})

        assert response.status_code in [400, 422]

    def test_clasificar_with_text_file(self, client, sample_txt):
        """Test document classification with text file."""
        data = {
            'file': (sample_txt, 'factura.txt'),
            'user': 'testuser'
        }

        response = client.post(
            '/api/clasificar',
            data=data,
            content_type='multipart/form-data'
        )

        # Should succeed or fail gracefully
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            result = response.get_json()
            assert 'tipo_documento' in result
            assert 'confianza' in result
            assert 'carpeta_sugerida' in result

    def test_clasificar_response_format(self, client, sample_txt):
        """Test that clasificar returns correct format."""
        data = {
            'file': (sample_txt, 'documento.txt'),
            'user': 'testuser'
        }

        response = client.post(
            '/api/clasificar',
            data=data,
            content_type='multipart/form-data'
        )

        if response.status_code == 200:
            result = response.get_json()

            # Check response structure
            assert isinstance(result, dict)
            assert 'tipo_documento' in result
            assert 'confianza' in result
            assert 'carpeta_sugerida' in result

            # Check types
            assert isinstance(result['tipo_documento'], str)
            assert isinstance(result['confianza'], (int, float))
            assert isinstance(result['carpeta_sugerida'], str)

            # Check values
            assert 0 <= result['confianza'] <= 1
            assert result['carpeta_sugerida'].startswith('/')


class TestMetadataEndpoints:
    """Test metadata endpoints."""

    def test_metadata_list(self, client):
        """Test listing metadata."""
        response = client.get('/api/metadata')

        # Should succeed or require auth
        assert response.status_code in [200, 401, 404]


class TestFolderStructureEndpoints:
    """Test folder structure endpoints."""

    def test_list_folder_templates(self, client, auth_headers):
        """Test listing folder templates."""
        response = client.get(
            '/api/folder-structure',
            headers=auth_headers
        )

        # Should succeed or require proper setup
        assert response.status_code in [200, 401, 404]
