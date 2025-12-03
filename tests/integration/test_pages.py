"""
Integration tests for Pages router (UI).

Tests cover:
- GET / main page
- Static files serving
- Template rendering
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestMainPage:
    """Integration tests for main page."""
    
    @pytest.mark.integration
    def test_main_page_returns_html(self, client: TestClient):
        """Test that main page returns HTML."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.integration
    def test_main_page_contains_title(self, client: TestClient):
        """Test that main page contains the app title."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "OCR KTP" in response.text
    
    @pytest.mark.integration
    def test_main_page_contains_upload_form(self, client: TestClient):
        """Test that main page contains upload form elements."""
        response = client.get("/")
        
        html = response.text
        
        # Check for upload-related elements
        assert "dropZone" in html or "drop" in html.lower()
        assert "file" in html.lower()
    
    @pytest.mark.integration
    def test_main_page_contains_javascript(self, client: TestClient):
        """Test that main page includes JavaScript."""
        response = client.get("/")
        
        assert "app.js" in response.text or "<script" in response.text
    
    @pytest.mark.integration
    def test_main_page_contains_tailwind(self, client: TestClient):
        """Test that main page includes TailwindCSS."""
        response = client.get("/")
        
        assert "tailwind" in response.text.lower() or "cdn" in response.text.lower()


class TestStaticFiles:
    """Integration tests for static files."""
    
    @pytest.mark.integration
    def test_javascript_file_accessible(self, client: TestClient):
        """Test that JavaScript file is accessible."""
        response = client.get("/static/js/app.js")
        
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"] or "text" in response.headers["content-type"]
    
    @pytest.mark.integration
    def test_css_file_accessible(self, client: TestClient):
        """Test that CSS file is accessible."""
        response = client.get("/static/css/style.css")
        
        assert response.status_code == 200
        assert "css" in response.headers["content-type"] or "text" in response.headers["content-type"]
    
    @pytest.mark.integration
    def test_nonexistent_static_file(self, client: TestClient):
        """Test 404 for non-existent static file."""
        response = client.get("/static/nonexistent.js")
        
        assert response.status_code == 404


class TestMainPageAsync:
    """Async integration tests for main page."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_main_page_async(self, async_client: AsyncClient):
        """Test main page with async client."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_static_js_async(self, async_client: AsyncClient):
        """Test static JS with async client."""
        response = await async_client.get("/static/js/app.js")
        
        assert response.status_code == 200
