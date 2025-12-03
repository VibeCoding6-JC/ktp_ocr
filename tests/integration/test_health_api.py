"""
Integration tests for Health API endpoint.

Tests cover:
- GET /api/v1/ocr/health endpoint
- GET /health global endpoint
- Health status responses
"""

import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


class TestHealthEndpoint:
    """Integration tests for health check endpoints."""
    
    @pytest.mark.integration
    def test_ocr_health_endpoint(self, client: TestClient):
        """Test OCR health endpoint returns healthy status."""
        response = client.get("/api/v1/ocr/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    @pytest.mark.integration
    def test_global_health_endpoint(self, client: TestClient):
        """Test global health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.integration
    def test_health_includes_version(self, client: TestClient):
        """Test that health response includes version."""
        response = client.get("/api/v1/ocr/health")
        
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @pytest.mark.integration
    def test_health_includes_gemini_status(self, client: TestClient):
        """Test that health response includes Gemini configuration status."""
        response = client.get("/api/v1/ocr/health")
        
        data = response.json()
        assert "gemini_configured" in data
        assert isinstance(data["gemini_configured"], bool)


class TestHealthEndpointAsync:
    """Async integration tests for health endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_async(self, async_client: AsyncClient):
        """Test health endpoint with async client."""
        response = await async_client.get("/api/v1/ocr/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_global_health_async(self, async_client: AsyncClient):
        """Test global health endpoint with async client."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    @pytest.mark.integration
    def test_swagger_docs_available(self, client: TestClient):
        """Test that Swagger UI is available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    @pytest.mark.integration
    def test_redoc_available(self, client: TestClient):
        """Test that ReDoc is available."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
    
    @pytest.mark.integration
    def test_openapi_json_available(self, client: TestClient):
        """Test that OpenAPI JSON is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestAPIInfo:
    """Tests for API info endpoint."""
    
    @pytest.mark.integration
    def test_api_info_endpoint(self, client: TestClient):
        """Test API info endpoint."""
        response = client.get("/api")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "description" in data
    
    @pytest.mark.integration
    def test_api_info_contains_endpoints(self, client: TestClient):
        """Test that API info contains endpoint documentation."""
        response = client.get("/api")
        
        data = response.json()
        
        assert "endpoints" in data or "documentation" in data
