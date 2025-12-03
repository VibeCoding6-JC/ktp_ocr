"""
Pytest configuration and shared fixtures.

This module contains fixtures used across all tests.
"""

import io
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.config import Settings, get_settings
from app.main import app, create_application
from app.models.ktp import KTPData
from app.services.gemini_service import GeminiService


# =============================================================================
# SETTINGS FIXTURES
# =============================================================================

@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock API key."""
    return Settings(
        gemini_api_key="test-api-key-12345",
        max_file_size_mb=5,
        allowed_extensions_str="jpg,jpeg,png,webp"
    )


@pytest.fixture
def settings_without_api_key() -> Settings:
    """Create settings without API key."""
    return Settings(
        gemini_api_key="",
        max_file_size_mb=5,
        allowed_extensions_str="jpg,jpeg,png,webp"
    )


# =============================================================================
# CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# =============================================================================
# IMAGE FIXTURES
# =============================================================================

@pytest.fixture
def valid_image_bytes() -> bytes:
    """Create a valid test image as bytes."""
    img = Image.new('RGB', (800, 600), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def valid_png_bytes() -> bytes:
    """Create a valid PNG test image."""
    img = Image.new('RGB', (800, 600), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def large_image_bytes() -> bytes:
    """Create an image larger than max allowed size."""
    # Create a large image (approximately 6MB)
    img = Image.new('RGB', (4000, 4000), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=100)
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def oversized_dimension_image() -> bytes:
    """Create an image with dimensions larger than 2048px."""
    img = Image.new('RGB', (3000, 3000), color='green')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def invalid_file_bytes() -> bytes:
    """Create invalid file content (not an image)."""
    return b"This is not an image file content"


@pytest.fixture
def empty_file_bytes() -> bytes:
    """Create empty file."""
    return b""


# =============================================================================
# KTP DATA FIXTURES
# =============================================================================

@pytest.fixture
def valid_ktp_data() -> dict:
    """Create valid KTP data dictionary."""
    return {
        "nik": "3201234567890001",
        "nama": "JOHN DOE",
        "tempat_lahir": "JAKARTA",
        "tanggal_lahir": "01-01-1990",
        "jenis_kelamin": "LAKI-LAKI",
        "alamat": "JL. CONTOH NO. 123",
        "rt_rw": "001/002",
        "kelurahan_desa": "CONTOH",
        "kecamatan": "KECAMATAN CONTOH",
        "agama": "ISLAM",
        "status_perkawinan": "BELUM KAWIN",
        "pekerjaan": "KARYAWAN SWASTA",
        "kewarganegaraan": "WNI",
        "berlaku_hingga": "SEUMUR HIDUP"
    }


@pytest.fixture
def partial_ktp_data() -> dict:
    """Create partial KTP data with some null fields."""
    return {
        "nik": "3201234567890001",
        "nama": "JANE DOE",
        "tempat_lahir": "BANDUNG",
        "tanggal_lahir": None,
        "jenis_kelamin": "PEREMPUAN",
        "alamat": None,
        "rt_rw": None,
        "kelurahan_desa": None,
        "kecamatan": None,
        "agama": "KRISTEN",
        "status_perkawinan": None,
        "pekerjaan": None,
        "kewarganegaraan": "WNI",
        "berlaku_hingga": None
    }


@pytest.fixture
def invalid_nik_ktp_data() -> dict:
    """Create KTP data with invalid NIK."""
    return {
        "nik": "123",  # Invalid: not 16 digits
        "nama": "INVALID NIK",
        "tempat_lahir": "SURABAYA",
        "tanggal_lahir": "15-06-1985",
        "jenis_kelamin": "LAKI-LAKI",
        "alamat": "JL. TEST",
        "rt_rw": "001/001",
        "kelurahan_desa": "TEST",
        "kecamatan": "TEST",
        "agama": "ISLAM",
        "status_perkawinan": "KAWIN",
        "pekerjaan": "PNS",
        "kewarganegaraan": "WNI",
        "berlaku_hingga": "SEUMUR HIDUP"
    }


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_gemini_service(valid_ktp_data: dict) -> MagicMock:
    """Create a mock Gemini service."""
    mock = MagicMock(spec=GeminiService)
    mock.extract_ktp_data = AsyncMock(return_value=KTPData(**valid_ktp_data))
    mock.is_configured = True
    return mock


@pytest.fixture
def mock_gemini_service_error() -> MagicMock:
    """Create a mock Gemini service that raises errors."""
    from app.exceptions import GeminiServiceError
    
    mock = MagicMock(spec=GeminiService)
    mock.extract_ktp_data = AsyncMock(
        side_effect=GeminiServiceError("Gemini API error")
    )
    mock.is_configured = True
    return mock


@pytest.fixture
def mock_gemini_service_unconfigured() -> MagicMock:
    """Create a mock Gemini service that is not configured."""
    mock = MagicMock(spec=GeminiService)
    mock.is_configured = False
    return mock


# =============================================================================
# GEMINI RESPONSE FIXTURES
# =============================================================================

@pytest.fixture
def gemini_json_response(valid_ktp_data: dict) -> str:
    """Create a mock Gemini JSON response."""
    import json
    return json.dumps(valid_ktp_data)


@pytest.fixture
def gemini_json_response_with_markdown(valid_ktp_data: dict) -> str:
    """Create a mock Gemini response with markdown code blocks."""
    import json
    return f"```json\n{json.dumps(valid_ktp_data)}\n```"


@pytest.fixture
def gemini_invalid_json_response() -> str:
    """Create an invalid JSON response."""
    return "This is not valid JSON at all"
