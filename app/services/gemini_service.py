"""
Gemini service for OCR KTP application.

This module provides the integration with Google Gemini Flash API
for extracting data from KTP images using OCR.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol

import google.generativeai as genai

from app.config import Settings, get_settings
from app.constants import (
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MODEL_NAME,
    GEMINI_TEMPERATURE,
    KTP_EXTRACTION_PROMPT,
    KTP_TOTAL_FIELDS,
    NIK_LENGTH,
)
from app.exceptions import APIKeyNotFoundError, JSONParsingError, OCRExtractionError
from app.models.ktp import KTPData


# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class OCRResult:
    """
    Result of OCR extraction process.
    
    Attributes:
        data: Extracted KTP data (None if extraction failed).
        confidence: Confidence score between 0 and 1.
        raw_response: Raw response from Gemini API.
        is_successful: Whether extraction was successful.
    """
    data: Optional[KTPData]
    confidence: float
    raw_response: str
    is_successful: bool
    
    @classmethod
    def success(
        cls,
        data: KTPData,
        confidence: float,
        raw_response: str
    ) -> "OCRResult":
        """Create successful OCR result."""
        return cls(
            data=data,
            confidence=confidence,
            raw_response=raw_response,
            is_successful=True
        )
    
    @classmethod
    def failure(cls, raw_response: str = "") -> "OCRResult":
        """Create failed OCR result."""
        return cls(
            data=None,
            confidence=0.0,
            raw_response=raw_response,
            is_successful=False
        )


# =============================================================================
# INTERFACES (PROTOCOLS)
# =============================================================================

class OCRServiceProtocol(Protocol):
    """Protocol defining the interface for OCR services."""
    
    async def extract_ktp_data(
        self,
        image_bytes: bytes,
        mime_type: str
    ) -> OCRResult:
        """Extract KTP data from image."""
        ...


class NIKValidatorProtocol(Protocol):
    """Protocol defining the interface for NIK validation."""
    
    def validate(self, nik: Optional[str]) -> bool:
        """Validate NIK format."""
        ...


# =============================================================================
# VALIDATORS
# =============================================================================

class NIKValidator:
    """
    Validator for Indonesian NIK (Nomor Induk Kependudukan).
    
    NIK is a 16-digit number with specific format rules.
    """
    
    @staticmethod
    def validate(nik: Optional[str]) -> bool:
        """
        Validate NIK format.
        
        Args:
            nik: NIK string to validate.
            
        Returns:
            True if NIK is valid, False otherwise.
        """
        if not nik:
            return False
        
        # Remove any whitespace
        nik = nik.strip()
        
        # Check length and digits
        if not nik.isdigit() or len(nik) != NIK_LENGTH:
            return False
        
        return True
    
    @staticmethod
    def validate_with_details(nik: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Validate NIK with detailed error message.
        
        Args:
            nik: NIK string to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        if not nik:
            return False, "NIK tidak boleh kosong"
        
        nik = nik.strip()
        
        if not nik.isdigit():
            return False, "NIK harus berupa angka"
        
        if len(nik) != NIK_LENGTH:
            return False, f"NIK harus {NIK_LENGTH} digit, ditemukan {len(nik)} digit"
        
        return True, None


# =============================================================================
# RESPONSE PARSER
# =============================================================================

class GeminiResponseParser:
    """Parser for Gemini API responses."""
    
    @staticmethod
    def clean_response(response_text: str) -> str:
        """
        Clean Gemini response by removing markdown code blocks.
        
        Args:
            response_text: Raw response from Gemini.
            
        Returns:
            Cleaned JSON string.
        """
        text = response_text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Filter out lines that are just code block markers
            cleaned_lines = [
                line for line in lines
                if not line.strip().startswith("```")
            ]
            text = "\n".join(cleaned_lines).strip()
        
        return text
    
    @staticmethod
    def parse_to_ktp_data(response_text: str) -> KTPData:
        """
        Parse Gemini response to KTPData.
        
        Args:
            response_text: Cleaned response text.
            
        Returns:
            KTPData instance.
            
        Raises:
            JSONParsingError: If response cannot be parsed.
        """
        cleaned_text = GeminiResponseParser.clean_response(response_text)
        
        try:
            ktp_dict = json.loads(cleaned_text)
            return KTPData(**ktp_dict)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Raw response: {response_text}")
            raise JSONParsingError(response_text)
        except Exception as e:
            logger.error(f"KTPData creation failed: {e}")
            raise JSONParsingError(response_text)


# =============================================================================
# CONFIDENCE CALCULATOR
# =============================================================================

class ConfidenceCalculator:
    """Calculator for OCR confidence scores."""
    
    @staticmethod
    def calculate(ktp_data: KTPData) -> float:
        """
        Calculate confidence score based on filled fields.
        
        Args:
            ktp_data: Extracted KTP data.
            
        Returns:
            Confidence score between 0 and 1.
        """
        filled_fields = ktp_data.get_filled_fields_count()
        return filled_fields / KTP_TOTAL_FIELDS


# =============================================================================
# GEMINI SERVICE
# =============================================================================

class GeminiService:
    """
    Service for interacting with Google Gemini Flash API.
    
    This service handles the communication with Gemini API
    for KTP OCR extraction.
    
    Attributes:
        model: Gemini generative model instance.
        parser: Response parser instance.
        confidence_calculator: Confidence calculator instance.
        nik_validator: NIK validator instance.
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        parser: Optional[GeminiResponseParser] = None,
        confidence_calculator: Optional[ConfidenceCalculator] = None,
        nik_validator: Optional[NIKValidator] = None
    ):
        """
        Initialize Gemini service.
        
        Args:
            settings: Application settings (uses default if not provided).
            parser: Response parser (uses default if not provided).
            confidence_calculator: Confidence calculator (uses default if not provided).
            nik_validator: NIK validator (uses default if not provided).
            
        Raises:
            APIKeyNotFoundError: If Gemini API key is not configured.
        """
        self._settings = settings or get_settings()
        self._parser = parser or GeminiResponseParser()
        self._confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self._nik_validator = nik_validator or NIKValidator()
        
        self._validate_api_key()
        self._configure_genai()
        self._model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    def _validate_api_key(self) -> None:
        """Validate that API key is configured."""
        if not self._settings.is_gemini_configured:
            raise APIKeyNotFoundError()
    
    def _configure_genai(self) -> None:
        """Configure the Gemini API client."""
        genai.configure(api_key=self._settings.gemini_api_key)
    
    async def extract_ktp_data(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> OCRResult:
        """
        Extract data from KTP image using Gemini Flash.
        
        Args:
            image_bytes: Image content in bytes.
            mime_type: MIME type of the image.
            
        Returns:
            OCRResult containing extracted data or failure info.
        """
        try:
            # Prepare image for Gemini
            image_part = self._create_image_part(image_bytes, mime_type)
            
            # Generate content
            response = self._model.generate_content(
                [KTP_EXTRACTION_PROMPT, image_part],
                generation_config=self._get_generation_config()
            )
            
            raw_response = response.text.strip()
            
            # Parse response
            ktp_data = self._parser.parse_to_ktp_data(raw_response)
            
            # Calculate confidence
            confidence = self._confidence_calculator.calculate(ktp_data)
            
            return OCRResult.success(
                data=ktp_data,
                confidence=confidence,
                raw_response=raw_response
            )
            
        except JSONParsingError as e:
            logger.warning(f"Failed to parse Gemini response: {e.message}")
            return OCRResult.failure(raw_response=e.raw_response)
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return OCRResult.failure()
    
    def _create_image_part(self, image_bytes: bytes, mime_type: str) -> dict:
        """Create image part for Gemini API."""
        return {
            "mime_type": mime_type,
            "data": image_bytes
        }
    
    def _get_generation_config(self) -> dict:
        """Get generation configuration for Gemini."""
        return {
            "temperature": GEMINI_TEMPERATURE,
            "max_output_tokens": GEMINI_MAX_OUTPUT_TOKENS,
        }
    
    def validate_nik(self, nik: Optional[str]) -> bool:
        """
        Validate NIK format.
        
        Args:
            nik: NIK string to validate.
            
        Returns:
            True if NIK is valid.
        """
        return self._nik_validator.validate(nik)


# =============================================================================
# SERVICE FACTORY
# =============================================================================

_gemini_service_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    Get singleton instance of GeminiService.
    
    Uses lazy initialization to create service only when needed.
    
    Returns:
        GeminiService singleton instance.
    """
    global _gemini_service_instance
    
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    
    return _gemini_service_instance


def reset_gemini_service() -> None:
    """
    Reset the Gemini service singleton.
    
    Useful for testing or when settings change.
    """
    global _gemini_service_instance
    _gemini_service_instance = None
