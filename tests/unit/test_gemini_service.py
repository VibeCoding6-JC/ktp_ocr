"""
Unit tests for Gemini service.

Tests cover:
- Service initialization
- KTP data extraction
- JSON parsing
- Error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.gemini_service import GeminiService, get_gemini_service
from app.models.ktp import KTPData
from app.exceptions import GeminiServiceError, JSONParsingError
from app.config import Settings


class TestGeminiServiceInitialization:
    """Tests for GeminiService initialization."""
    
    @pytest.mark.unit
    def test_service_init_with_api_key(self, test_settings: Settings):
        """Test service initialization with valid API key."""
        service = GeminiService(test_settings)
        
        assert service.is_configured is True
    
    @pytest.mark.unit
    def test_service_init_without_api_key(self, settings_without_api_key: Settings):
        """Test service initialization without API key."""
        service = GeminiService(settings_without_api_key)
        
        assert service.is_configured is False


class TestGeminiServiceExtraction:
    """Tests for GeminiService KTP extraction."""
    
    @pytest.mark.unit
    async def test_extract_ktp_data_success(
        self, 
        test_settings: Settings,
        valid_image_bytes: bytes,
        valid_ktp_data: dict
    ):
        """Test successful KTP data extraction."""
        service = GeminiService(test_settings)
        
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = json.dumps(valid_ktp_data)
        
        with patch.object(
            service, 
            '_generate_content', 
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.extract_ktp_data(valid_image_bytes)
        
            assert isinstance(result, KTPData)
            assert result.nik == "3201234567890001"
            assert result.nama == "JOHN DOE"
    
    @pytest.mark.unit
    async def test_extract_ktp_data_with_markdown_wrapper(
        self, 
        test_settings: Settings,
        valid_image_bytes: bytes,
        gemini_json_response_with_markdown: str
    ):
        """Test extraction with markdown-wrapped JSON response."""
        service = GeminiService(test_settings)
        
        mock_response = MagicMock()
        mock_response.text = gemini_json_response_with_markdown
        
        with patch.object(
            service, 
            '_generate_content', 
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.extract_ktp_data(valid_image_bytes)
        
            assert isinstance(result, KTPData)
            assert result.nik == "3201234567890001"
    
    @pytest.mark.unit
    async def test_extract_ktp_data_partial_response(
        self, 
        test_settings: Settings,
        valid_image_bytes: bytes,
        partial_ktp_data: dict
    ):
        """Test extraction with partial data response."""
        service = GeminiService(test_settings)
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(partial_ktp_data)
        
        with patch.object(
            service, 
            '_generate_content', 
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.extract_ktp_data(valid_image_bytes)
        
            assert isinstance(result, KTPData)
            assert result.nik == "3201234567890001"
            assert result.tanggal_lahir is None
    
    @pytest.mark.unit
    async def test_extract_ktp_data_not_configured(
        self, 
        settings_without_api_key: Settings,
        valid_image_bytes: bytes
    ):
        """Test extraction when service is not configured."""
        service = GeminiService(settings_without_api_key)
        
        with pytest.raises(GeminiServiceError) as exc_info:
            await service.extract_ktp_data(valid_image_bytes)
        
        assert "tidak dikonfigurasi" in str(exc_info.value).lower() or "not configured" in str(exc_info.value).lower()


class TestGeminiServiceJsonParsing:
    """Tests for JSON parsing in GeminiService."""
    
    @pytest.mark.unit
    def test_parse_valid_json(self, test_settings: Settings, valid_ktp_data: dict):
        """Test parsing valid JSON response."""
        service = GeminiService(test_settings)
        json_str = json.dumps(valid_ktp_data)
        
        result = service._parse_json_response(json_str)
        
        assert result["nik"] == "3201234567890001"
        assert result["nama"] == "JOHN DOE"
    
    @pytest.mark.unit
    def test_parse_json_with_markdown_code_block(
        self, 
        test_settings: Settings, 
        valid_ktp_data: dict
    ):
        """Test parsing JSON wrapped in markdown code block."""
        service = GeminiService(test_settings)
        json_str = f"```json\n{json.dumps(valid_ktp_data)}\n```"
        
        result = service._parse_json_response(json_str)
        
        assert result["nik"] == "3201234567890001"
    
    @pytest.mark.unit
    def test_parse_json_with_plain_code_block(
        self, 
        test_settings: Settings, 
        valid_ktp_data: dict
    ):
        """Test parsing JSON wrapped in plain code block."""
        service = GeminiService(test_settings)
        json_str = f"```\n{json.dumps(valid_ktp_data)}\n```"
        
        result = service._parse_json_response(json_str)
        
        assert result["nik"] == "3201234567890001"
    
    @pytest.mark.unit
    def test_parse_invalid_json(self, test_settings: Settings):
        """Test parsing invalid JSON raises error."""
        service = GeminiService(test_settings)
        invalid_json = "This is not valid JSON"
        
        with pytest.raises((JSONParsingError, GeminiServiceError, json.JSONDecodeError)):
            service._parse_json_response(invalid_json)


class TestGeminiServiceConfidence:
    """Tests for confidence calculation."""
    
    @pytest.mark.unit
    def test_calculate_confidence_all_fields(
        self, 
        test_settings: Settings,
        valid_ktp_data: dict
    ):
        """Test confidence calculation with all fields filled."""
        service = GeminiService(test_settings)
        ktp = KTPData(**valid_ktp_data)
        
        confidence = service._calculate_confidence(ktp)
        
        # All 14 fields filled should give high confidence
        assert confidence >= 0.9
        assert confidence <= 1.0
    
    @pytest.mark.unit
    def test_calculate_confidence_partial_fields(
        self, 
        test_settings: Settings,
        partial_ktp_data: dict
    ):
        """Test confidence calculation with partial fields."""
        service = GeminiService(test_settings)
        ktp = KTPData(**partial_ktp_data)
        
        confidence = service._calculate_confidence(ktp)
        
        # Some fields are None, confidence should be lower
        assert confidence < 1.0
        assert confidence > 0.0
    
    @pytest.mark.unit
    def test_calculate_confidence_no_fields(self, test_settings: Settings):
        """Test confidence calculation with no fields filled."""
        service = GeminiService(test_settings)
        ktp = KTPData(
            nik=None, nama=None, tempat_lahir=None, tanggal_lahir=None,
            jenis_kelamin=None, alamat=None, rt_rw=None, kelurahan_desa=None,
            kecamatan=None, agama=None, status_perkawinan=None, pekerjaan=None,
            kewarganegaraan=None, berlaku_hingga=None
        )
        
        confidence = service._calculate_confidence(ktp)
        
        assert confidence == 0.0


class TestGetGeminiService:
    """Tests for get_gemini_service function."""
    
    @pytest.mark.unit
    def test_get_gemini_service_returns_instance(self):
        """Test that get_gemini_service returns GeminiService instance."""
        with patch.dict('os.environ', {"GEMINI_API_KEY": "test-key"}):
            service = get_gemini_service()
            assert isinstance(service, GeminiService)
