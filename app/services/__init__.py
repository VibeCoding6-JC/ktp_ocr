"""
Services package for OCR KTP application.

This package contains business logic services including
the Gemini integration for OCR processing.
"""

from app.services.gemini_service import (
    ConfidenceCalculator,
    GeminiResponseParser,
    GeminiService,
    NIKValidator,
    OCRResult,
    get_gemini_service,
    reset_gemini_service,
)

__all__ = [
    "GeminiService",
    "get_gemini_service",
    "reset_gemini_service",
    "OCRResult",
    "NIKValidator",
    "GeminiResponseParser",
    "ConfidenceCalculator",
]
