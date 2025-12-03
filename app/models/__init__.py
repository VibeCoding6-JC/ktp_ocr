"""
Models package for OCR KTP application.

This package contains Pydantic models for data validation
and serialization.
"""

from app.models.ktp import (
    ErrorResponse,
    HealthResponse,
    KTPData,
    OCRResponse,
)

__all__ = [
    "KTPData",
    "OCRResponse",
    "ErrorResponse",
    "HealthResponse",
]
