"""
Custom exceptions for OCR KTP application.

This module provides a hierarchy of custom exceptions for better error handling
and more descriptive error messages throughout the application.
"""

from typing import Optional


class OCRKTPBaseException(Exception):
    """Base exception for all OCR KTP application errors."""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


# =============================================================================
# FILE VALIDATION EXCEPTIONS
# =============================================================================

class FileValidationError(OCRKTPBaseException):
    """Base exception for file validation errors."""
    pass


class InvalidFilenameError(FileValidationError):
    """Raised when the uploaded file has an invalid filename."""
    pass


class UnsupportedFileFormatError(FileValidationError):
    """Raised when the uploaded file format is not supported."""
    
    def __init__(self, extension: str, allowed_extensions: tuple[str, ...]):
        self.extension = extension
        self.allowed_extensions = allowed_extensions
        message = f"Format file '{extension}' tidak didukung. Gunakan: {', '.join(allowed_extensions)}"
        super().__init__(message)


class FileTooLargeError(FileValidationError):
    """Raised when the uploaded file exceeds the maximum allowed size."""
    
    def __init__(self, file_size_mb: float, max_size_mb: int):
        self.file_size_mb = file_size_mb
        self.max_size_mb = max_size_mb
        message = f"Ukuran file ({file_size_mb:.2f}MB) melebihi batas maksimum ({max_size_mb}MB)"
        super().__init__(message)


class InvalidImageError(FileValidationError):
    """Raised when the uploaded file is not a valid image."""
    pass


# =============================================================================
# SERVICE EXCEPTIONS
# =============================================================================

class ServiceError(OCRKTPBaseException):
    """Base exception for service-related errors."""
    pass


class GeminiServiceError(ServiceError):
    """Raised when there's an error with the Gemini service."""
    pass


class APIKeyNotFoundError(GeminiServiceError):
    """Raised when the Gemini API key is not configured."""
    
    def __init__(self):
        super().__init__(
            message="GEMINI_API_KEY tidak ditemukan",
            detail="Pastikan GEMINI_API_KEY sudah diset di file .env"
        )


class OCRExtractionError(GeminiServiceError):
    """Raised when OCR extraction fails."""
    
    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            message="Gagal mengekstrak data dari gambar",
            detail=detail or "Pastikan gambar KTP jelas dan tidak buram"
        )


class JSONParsingError(GeminiServiceError):
    """Raised when the Gemini response cannot be parsed as JSON."""
    
    def __init__(self, raw_response: str):
        self.raw_response = raw_response
        super().__init__(
            message="Gagal memproses response dari Gemini",
            detail="Response tidak dalam format JSON yang valid"
        )


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationError(OCRKTPBaseException):
    """Base exception for data validation errors."""
    pass


class InvalidNIKError(ValidationError):
    """Raised when NIK format is invalid."""
    
    def __init__(self, nik: str):
        self.nik = nik
        super().__init__(
            message="Format NIK tidak valid",
            detail=f"NIK harus 16 digit angka, diterima: {nik}"
        )
