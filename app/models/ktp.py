"""
KTP data models for OCR KTP application.

This module contains Pydantic models for representing KTP data
and API responses with proper validation and documentation.
"""

from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator

from app.constants import NIK_LENGTH


# =============================================================================
# KTP DATA MODEL
# =============================================================================

class KTPData(BaseModel):
    """
    Model representing extracted data from Indonesian KTP (ID Card).
    
    All fields are optional since OCR may not be able to read all fields
    depending on image quality.
    """
    
    nik: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=NIK_LENGTH,
            max_length=NIK_LENGTH,
            pattern=r"^\d{16}$",
            description="Nomor Induk Kependudukan (16 digit)",
            examples=["3201234567890001"]
        )
    ]
    
    nama: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=1,
            max_length=100,
            description="Nama lengkap sesuai KTP",
            examples=["JOHN DOE"]
        )
    ]
    
    tempat_lahir: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Tempat lahir",
            examples=["JAKARTA"]
        )
    ]
    
    tanggal_lahir: Annotated[
        Optional[str],
        Field(
            default=None,
            pattern=r"^\d{2}-\d{2}-\d{4}$",
            description="Tanggal lahir (format: DD-MM-YYYY)",
            examples=["01-01-1990"]
        )
    ]
    
    jenis_kelamin: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Jenis kelamin",
            examples=["LAKI-LAKI", "PEREMPUAN"]
        )
    ]
    
    alamat: Annotated[
        Optional[str],
        Field(
            default=None,
            max_length=500,
            description="Alamat lengkap",
            examples=["JL. CONTOH NO. 123"]
        )
    ]
    
    rt_rw: Annotated[
        Optional[str],
        Field(
            default=None,
            pattern=r"^\d{3}/\d{3}$",
            description="RT/RW (format: XXX/XXX)",
            examples=["001/002"]
        )
    ]
    
    kelurahan_desa: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Nama kelurahan atau desa",
            examples=["CONTOH"]
        )
    ]
    
    kecamatan: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Nama kecamatan",
            examples=["CONTOH"]
        )
    ]
    
    agama: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Agama",
            examples=["ISLAM", "KRISTEN", "KATOLIK", "HINDU", "BUDDHA", "KONGHUCU"]
        )
    ]
    
    status_perkawinan: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Status perkawinan",
            examples=["BELUM KAWIN", "KAWIN", "CERAI HIDUP", "CERAI MATI"]
        )
    ]
    
    pekerjaan: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Pekerjaan",
            examples=["KARYAWAN SWASTA", "PEGAWAI NEGERI SIPIL", "WIRASWASTA"]
        )
    ]
    
    kewarganegaraan: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Kewarganegaraan",
            examples=["WNI", "WNA"]
        )
    ]
    
    berlaku_hingga: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Masa berlaku KTP",
            examples=["SEUMUR HIDUP", "01-01-2025"]
        )
    ]
    
    @field_validator("nik", mode="before")
    @classmethod
    def clean_nik(cls, value: Optional[str]) -> Optional[str]:
        """Remove any spaces or non-digit characters from NIK."""
        if value is None:
            return None
        cleaned = "".join(filter(str.isdigit, str(value)))
        return cleaned if len(cleaned) == NIK_LENGTH else None
    
    @field_validator("nama", "tempat_lahir", "alamat", "kelurahan_desa", 
                     "kecamatan", "agama", "pekerjaan", mode="before")
    @classmethod
    def uppercase_string(cls, value: Optional[str]) -> Optional[str]:
        """Convert string fields to uppercase."""
        if value is None:
            return None
        return str(value).strip().upper()
    
    def get_filled_fields_count(self) -> int:
        """Count the number of non-null fields."""
        return sum(1 for value in self.model_dump().values() if value is not None)
    
    def is_nik_valid(self) -> bool:
        """Check if NIK is present and has valid format."""
        return self.nik is not None and len(self.nik) == NIK_LENGTH


# =============================================================================
# API RESPONSE MODELS
# =============================================================================

class OCRResponse(BaseModel):
    """
    Standard API response model for successful OCR operations.
    
    Attributes:
        success: Indicates if the operation was successful.
        data: Extracted KTP data (None if extraction failed).
        confidence: Confidence score between 0 and 1.
        message: Human-readable status message.
    """
    
    success: Annotated[
        bool,
        Field(description="Status keberhasilan proses OCR")
    ]
    
    data: Annotated[
        Optional[KTPData],
        Field(default=None, description="Data KTP yang berhasil diekstrak")
    ]
    
    confidence: Annotated[
        Optional[float],
        Field(
            default=None,
            ge=0.0,
            le=1.0,
            description="Tingkat kepercayaan hasil OCR (0-1)"
        )
    ]
    
    message: Annotated[
        Optional[str],
        Field(default=None, description="Pesan tambahan")
    ]
    
    @classmethod
    def success_response(
        cls,
        data: KTPData,
        confidence: float,
        message: str
    ) -> "OCRResponse":
        """Factory method for creating success response."""
        return cls(
            success=True,
            data=data,
            confidence=confidence,
            message=message
        )
    
    @classmethod
    def failure_response(cls, message: str) -> "OCRResponse":
        """Factory method for creating failure response."""
        return cls(
            success=False,
            data=None,
            confidence=0.0,
            message=message
        )


class ErrorResponse(BaseModel):
    """
    Standard API response model for error cases.
    
    Attributes:
        success: Always False for error responses.
        error: Main error message.
        detail: Optional detailed error information.
    """
    
    success: Annotated[
        bool,
        Field(default=False, description="Selalu False untuk error response")
    ]
    
    error: Annotated[
        str,
        Field(description="Pesan error utama")
    ]
    
    detail: Annotated[
        Optional[str],
        Field(default=None, description="Detail error tambahan")
    ]
    
    @classmethod
    def from_exception(cls, error: str, detail: Optional[str] = None) -> "ErrorResponse":
        """Factory method for creating error response from exception."""
        return cls(success=False, error=error, detail=detail)


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: Annotated[str, Field(description="Status kesehatan service")]
    service: Annotated[str, Field(description="Nama service")]
    version: Annotated[Optional[str], Field(default=None, description="Versi API")]
