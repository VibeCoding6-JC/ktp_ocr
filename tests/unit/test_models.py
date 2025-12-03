"""
Unit tests for Pydantic models.

Tests cover:
- KTPData validation
- OCRResponse structure
- ErrorResponse structure
- HealthResponse structure
- Field validators
"""

import pytest
from pydantic import ValidationError

from app.models.ktp import (
    ErrorResponse,
    HealthResponse,
    KTPData,
    OCRResponse,
)


class TestKTPData:
    """Tests for KTPData model."""
    
    @pytest.mark.unit
    def test_create_ktp_data_with_all_fields(self, valid_ktp_data: dict):
        """Test creating KTPData with all fields populated."""
        ktp = KTPData(**valid_ktp_data)
        
        assert ktp.nik == "3201234567890001"
        assert ktp.nama == "JOHN DOE"
        assert ktp.tempat_lahir == "JAKARTA"
        assert ktp.tanggal_lahir == "01-01-1990"
        assert ktp.jenis_kelamin == "LAKI-LAKI"
        assert ktp.alamat == "JL. CONTOH NO. 123"
        assert ktp.rt_rw == "001/002"
        assert ktp.kelurahan_desa == "CONTOH"
        assert ktp.kecamatan == "KECAMATAN CONTOH"
        assert ktp.agama == "ISLAM"
        assert ktp.status_perkawinan == "BELUM KAWIN"
        assert ktp.pekerjaan == "KARYAWAN SWASTA"
        assert ktp.kewarganegaraan == "WNI"
        assert ktp.berlaku_hingga == "SEUMUR HIDUP"
    
    @pytest.mark.unit
    def test_create_ktp_data_with_optional_fields_none(self):
        """Test creating KTPData with optional fields as None."""
        ktp = KTPData(
            nik=None,
            nama=None,
            tempat_lahir=None,
            tanggal_lahir=None,
            jenis_kelamin=None,
            alamat=None,
            rt_rw=None,
            kelurahan_desa=None,
            kecamatan=None,
            agama=None,
            status_perkawinan=None,
            pekerjaan=None,
            kewarganegaraan=None,
            berlaku_hingga=None
        )
        
        assert ktp.nik is None
        assert ktp.nama is None
        assert ktp.tempat_lahir is None
    
    @pytest.mark.unit
    def test_ktp_data_partial_fields(self, partial_ktp_data: dict):
        """Test creating KTPData with partial fields."""
        ktp = KTPData(**partial_ktp_data)
        
        assert ktp.nik == "3201234567890001"
        assert ktp.nama == "JANE DOE"
        assert ktp.tanggal_lahir is None
        assert ktp.alamat is None
    
    @pytest.mark.unit
    def test_ktp_data_to_dict(self, valid_ktp_data: dict):
        """Test converting KTPData to dictionary."""
        ktp = KTPData(**valid_ktp_data)
        result = ktp.model_dump()
        
        assert isinstance(result, dict)
        assert result["nik"] == "3201234567890001"
        assert result["nama"] == "JOHN DOE"
    
    @pytest.mark.unit
    def test_ktp_data_json_serialization(self, valid_ktp_data: dict):
        """Test JSON serialization of KTPData."""
        ktp = KTPData(**valid_ktp_data)
        json_str = ktp.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "3201234567890001" in json_str
        assert "JOHN DOE" in json_str


class TestOCRResponse:
    """Tests for OCRResponse model."""
    
    @pytest.mark.unit
    def test_ocr_response_success(self, valid_ktp_data: dict):
        """Test creating successful OCRResponse."""
        ktp = KTPData(**valid_ktp_data)
        response = OCRResponse(
            success=True,
            message="Data berhasil diekstrak",
            data=ktp,
            confidence=0.95
        )
        
        assert response.success is True
        assert response.message == "Data berhasil diekstrak"
        assert response.data.nik == "3201234567890001"
        assert response.confidence == 0.95
    
    @pytest.mark.unit
    def test_ocr_response_failure(self):
        """Test creating failed OCRResponse."""
        response = OCRResponse(
            success=False,
            message="Gagal memproses gambar",
            data=None,
            confidence=0.0
        )
        
        assert response.success is False
        assert response.data is None
        assert response.confidence == 0.0
    
    @pytest.mark.unit
    def test_ocr_response_confidence_bounds(self, valid_ktp_data: dict):
        """Test OCRResponse with various confidence values."""
        ktp = KTPData(**valid_ktp_data)
        
        # Minimum confidence
        response_min = OCRResponse(success=True, data=ktp, confidence=0.0)
        assert response_min.confidence == 0.0
        
        # Maximum confidence
        response_max = OCRResponse(success=True, data=ktp, confidence=1.0)
        assert response_max.confidence == 1.0
        
        # Middle confidence
        response_mid = OCRResponse(success=True, data=ktp, confidence=0.5)
        assert response_mid.confidence == 0.5


class TestErrorResponse:
    """Tests for ErrorResponse model."""
    
    @pytest.mark.unit
    def test_error_response_creation(self):
        """Test creating ErrorResponse."""
        response = ErrorResponse(
            success=False,
            message="File tidak valid"
        )
        
        assert response.success is False
        assert response.message == "File tidak valid"
    
    @pytest.mark.unit
    def test_error_response_with_detail(self):
        """Test ErrorResponse with detailed message."""
        response = ErrorResponse(
            success=False,
            message="Format file tidak didukung. Gunakan JPG, PNG, atau WEBP."
        )
        
        assert "Format file tidak didukung" in response.message


class TestHealthResponse:
    """Tests for HealthResponse model."""
    
    @pytest.mark.unit
    def test_health_response_healthy(self):
        """Test healthy status response."""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            gemini_configured=True
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.gemini_configured is True
    
    @pytest.mark.unit
    def test_health_response_unhealthy(self):
        """Test unhealthy status response."""
        response = HealthResponse(
            status="unhealthy",
            version="1.0.0",
            gemini_configured=False
        )
        
        assert response.status == "unhealthy"
        assert response.gemini_configured is False
