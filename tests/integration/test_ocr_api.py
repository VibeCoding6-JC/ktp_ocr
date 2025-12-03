"""
Integration tests for OCR API endpoints.

Tests cover:
- POST /api/v1/ocr/ktp endpoint
- File upload validation
- OCR processing with mocked Gemini
- Error responses
"""

import io
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.ktp import KTPData
from app.services.gemini_service import GeminiService


class TestOCRKTPEndpoint:
    """Integration tests for POST /api/v1/ocr/ktp endpoint."""
    
    @pytest.mark.integration
    def test_ocr_ktp_success(
        self, 
        client: TestClient, 
        valid_image_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test successful OCR extraction."""
        # Mock Gemini service
        mock_ktp = KTPData(**valid_ktp_data)
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(return_value=mock_ktp)
            mock_service.is_configured = True
            mock_service._calculate_confidence = MagicMock(return_value=0.95)
            mock_get_service.return_value = mock_service
            
            response = client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["nik"] == "3201234567890001"
        assert data["data"]["nama"] == "JOHN DOE"
    
    @pytest.mark.integration
    def test_ocr_ktp_invalid_file_format(
        self, 
        client: TestClient, 
        valid_image_bytes: bytes
    ):
        """Test OCR with invalid file format."""
        response = client.post(
            "/api/v1/ocr/ktp",
            files={"file": ("test.gif", valid_image_bytes, "image/gif")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Format file tidak didukung" in data["detail"] or "tidak didukung" in data["detail"].lower()
    
    @pytest.mark.integration
    def test_ocr_ktp_no_file(self, client: TestClient):
        """Test OCR without file upload."""
        response = client.post("/api/v1/ocr/ktp")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    def test_ocr_ktp_empty_file(
        self, 
        client: TestClient, 
        empty_file_bytes: bytes
    ):
        """Test OCR with empty file."""
        response = client.post(
            "/api/v1/ocr/ktp",
            files={"file": ("empty.jpg", empty_file_bytes, "image/jpeg")}
        )
        
        # Should return error for empty/invalid file
        assert response.status_code in [400, 422, 500]
    
    @pytest.mark.integration
    def test_ocr_ktp_invalid_image_content(
        self, 
        client: TestClient, 
        invalid_file_bytes: bytes
    ):
        """Test OCR with invalid image content."""
        response = client.post(
            "/api/v1/ocr/ktp",
            files={"file": ("fake.jpg", invalid_file_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "tidak dapat dibaca" in data["detail"].lower() or "rusak" in data["detail"].lower() or "invalid" in data["detail"].lower()
    
    @pytest.mark.integration
    def test_ocr_ktp_png_format(
        self, 
        client: TestClient, 
        valid_png_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test OCR with PNG format."""
        mock_ktp = KTPData(**valid_ktp_data)
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(return_value=mock_ktp)
            mock_service.is_configured = True
            mock_service._calculate_confidence = MagicMock(return_value=0.90)
            mock_get_service.return_value = mock_service
            
            response = client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.png", valid_png_bytes, "image/png")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.integration
    def test_ocr_ktp_gemini_error(
        self, 
        client: TestClient, 
        valid_image_bytes: bytes
    ):
        """Test OCR when Gemini service fails."""
        from app.exceptions import GeminiServiceError
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(
                side_effect=GeminiServiceError("API Error")
            )
            mock_service.is_configured = True
            mock_get_service.return_value = mock_service
            
            response = client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")}
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "success" in data or "detail" in data


class TestOCRKTPEndpointAsync:
    """Async integration tests for OCR endpoint."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_ocr_ktp_async_success(
        self, 
        async_client: AsyncClient, 
        valid_image_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test successful OCR extraction with async client."""
        mock_ktp = KTPData(**valid_ktp_data)
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(return_value=mock_ktp)
            mock_service.is_configured = True
            mock_service._calculate_confidence = MagicMock(return_value=0.95)
            mock_get_service.return_value = mock_service
            
            response = await async_client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestOCRResponseFormat:
    """Tests for OCR response format."""
    
    @pytest.mark.integration
    def test_response_contains_all_fields(
        self, 
        client: TestClient, 
        valid_image_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test that response contains all expected fields."""
        mock_ktp = KTPData(**valid_ktp_data)
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(return_value=mock_ktp)
            mock_service.is_configured = True
            mock_service._calculate_confidence = MagicMock(return_value=0.95)
            mock_get_service.return_value = mock_service
            
            response = client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")}
            )
        
        data = response.json()
        
        # Check response structure
        assert "success" in data
        assert "data" in data
        assert "confidence" in data
        
        # Check KTP data fields
        ktp_data = data["data"]
        expected_fields = [
            "nik", "nama", "tempat_lahir", "tanggal_lahir",
            "jenis_kelamin", "alamat", "rt_rw", "kelurahan_desa",
            "kecamatan", "agama", "status_perkawinan", "pekerjaan",
            "kewarganegaraan", "berlaku_hingga"
        ]
        
        for field in expected_fields:
            assert field in ktp_data, f"Missing field: {field}"
    
    @pytest.mark.integration
    def test_confidence_is_float(
        self, 
        client: TestClient, 
        valid_image_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test that confidence is a float between 0 and 1."""
        mock_ktp = KTPData(**valid_ktp_data)
        
        with patch(
            'app.routers.ocr.get_gemini_service_dependency'
        ) as mock_get_service:
            mock_service = MagicMock(spec=GeminiService)
            mock_service.extract_ktp_data = AsyncMock(return_value=mock_ktp)
            mock_service.is_configured = True
            mock_service._calculate_confidence = MagicMock(return_value=0.85)
            mock_get_service.return_value = mock_service
            
            response = client.post(
                "/api/v1/ocr/ktp",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")}
            )
        
        data = response.json()
        confidence = data["confidence"]
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
