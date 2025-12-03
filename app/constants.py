"""
Constants module for OCR KTP application.

This module contains all constant values used throughout the application.
Following the principle of keeping magic numbers and strings in one place.
"""

from typing import Final


# =============================================================================
# API CONFIGURATION
# =============================================================================

API_TITLE: Final[str] = "OCR KTP API"
API_DESCRIPTION: Final[str] = (
    "API untuk mengekstrak data dari foto KTP Indonesia menggunakan Gemini Flash"
)
API_VERSION: Final[str] = "1.0.0"

# API Routes
API_PREFIX: Final[str] = "/api/v1"
OCR_ROUTE_PREFIX: Final[str] = "/ocr"
OCR_KTP_ENDPOINT: Final[str] = "/ktp"
HEALTH_ENDPOINT: Final[str] = "/health"


# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================

DEFAULT_MAX_FILE_SIZE_MB: Final[int] = 5
DEFAULT_ALLOWED_EXTENSIONS: Final[tuple[str, ...]] = ("jpg", "jpeg", "png", "webp")
MAX_IMAGE_DIMENSION: Final[int] = 2048


# =============================================================================
# GEMINI CONFIGURATION
# =============================================================================

GEMINI_MODEL_NAME: Final[str] = "gemini-2.0-flash"
GEMINI_TEMPERATURE: Final[float] = 0.1
GEMINI_MAX_OUTPUT_TOKENS: Final[int] = 1024


# =============================================================================
# KTP FIELDS
# =============================================================================

KTP_TOTAL_FIELDS: Final[int] = 14
NIK_LENGTH: Final[int] = 16


# =============================================================================
# MIME TYPES
# =============================================================================

MIME_TYPES: Final[dict[str, str]] = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}

DEFAULT_MIME_TYPE: Final[str] = "image/jpeg"


# =============================================================================
# ERROR MESSAGES
# =============================================================================

class ErrorMessages:
    """Centralized error messages for consistent error handling."""
    
    # File validation errors
    INVALID_FILENAME: Final[str] = "Nama file tidak valid"
    UNSUPPORTED_FORMAT: Final[str] = "Format file tidak didukung. Gunakan: {extensions}"
    FILE_TOO_LARGE: Final[str] = "Ukuran file melebihi batas maksimum ({max_size}MB)"
    INVALID_IMAGE: Final[str] = "File bukan gambar yang valid"
    
    # API errors
    MISSING_API_KEY: Final[str] = "GEMINI_API_KEY tidak ditemukan di environment variables"
    OCR_EXTRACTION_FAILED: Final[str] = (
        "Gagal mengekstrak data dari gambar. "
        "Pastikan gambar KTP jelas dan tidak buram."
    )
    PROCESSING_ERROR: Final[str] = "Terjadi kesalahan saat memproses gambar: {error}"
    
    # Success messages
    EXTRACTION_SUCCESS: Final[str] = "Data berhasil diekstrak"
    EXTRACTION_SUCCESS_INVALID_NIK: Final[str] = (
        "Data diekstrak, namun format NIK mungkin tidak valid"
    )


# =============================================================================
# SUCCESS MESSAGES
# =============================================================================

class SuccessMessages:
    """Centralized success messages."""
    
    DATA_EXTRACTED: Final[str] = "Data berhasil diekstrak"
    DATA_EXTRACTED_NIK_WARNING: Final[str] = (
        "Data diekstrak, namun format NIK mungkin tidak valid"
    )


# =============================================================================
# PROMPTS
# =============================================================================

KTP_EXTRACTION_PROMPT: Final[str] = """Kamu adalah sistem OCR khusus untuk membaca KTP Indonesia.
Ekstrak semua informasi dari gambar KTP berikut dan kembalikan dalam format JSON.

Field yang harus diekstrak:
- nik (16 digit angka, tanpa spasi)
- nama (huruf kapital)
- tempat_lahir
- tanggal_lahir (format: DD-MM-YYYY)
- jenis_kelamin (LAKI-LAKI atau PEREMPUAN)
- alamat
- rt_rw (format: XXX/XXX)
- kelurahan_desa
- kecamatan
- agama
- status_perkawinan
- pekerjaan
- kewarganegaraan (WNI atau WNA)
- berlaku_hingga

PENTING:
1. Jika field tidak terbaca jelas, isi dengan null
2. Kembalikan HANYA JSON tanpa penjelasan tambahan
3. Pastikan NIK adalah 16 digit angka
4. Semua text dalam huruf KAPITAL

Contoh output format:
{
    "nik": "3201234567890001",
    "nama": "JOHN DOE",
    "tempat_lahir": "JAKARTA",
    "tanggal_lahir": "01-01-1990",
    "jenis_kelamin": "LAKI-LAKI",
    "alamat": "JL. CONTOH NO. 123",
    "rt_rw": "001/002",
    "kelurahan_desa": "CONTOH",
    "kecamatan": "CONTOH",
    "agama": "ISLAM",
    "status_perkawinan": "BELUM KAWIN",
    "pekerjaan": "KARYAWAN SWASTA",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP"
}
"""
