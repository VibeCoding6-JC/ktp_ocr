"""
OCR router for KTP extraction endpoints.

This module contains the API endpoints for OCR KTP functionality.
Follows clean architecture principles with dependency injection.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.constants import (
    API_VERSION,
    HEALTH_ENDPOINT,
    OCR_KTP_ENDPOINT,
    OCR_ROUTE_PREFIX,
    SuccessMessages,
)
from app.exceptions import (
    FileValidationError,
    GeminiServiceError,
    OCRKTPBaseException,
)
from app.models.ktp import ErrorResponse, HealthResponse, OCRResponse
from app.services.gemini_service import GeminiService, get_gemini_service
from app.utils.image_utils import resize_image, validate_uploaded_image


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix=f"/api/v1{OCR_ROUTE_PREFIX}",
    tags=["OCR"]
)


# =============================================================================
# DEPENDENCIES
# =============================================================================

async def get_settings_dependency() -> Settings:
    """Dependency for getting application settings."""
    return get_settings()


async def get_gemini_service_dependency() -> GeminiService:
    """Dependency for getting Gemini service."""
    return get_gemini_service()


# Type aliases for cleaner annotations
SettingsDep = Annotated[Settings, Depends(get_settings_dependency)]
GeminiServiceDep = Annotated[GeminiService, Depends(get_gemini_service_dependency)]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_success_message(is_nik_valid: bool) -> str:
    """Create appropriate success message based on NIK validity."""
    if is_nik_valid:
        return SuccessMessages.DATA_EXTRACTED
    return SuccessMessages.DATA_EXTRACTED_NIK_WARNING


def handle_extraction_error(error: Exception) -> HTTPException:
    """
    Convert application exceptions to HTTP exceptions.
    
    Args:
        error: The caught exception.
        
    Returns:
        HTTPException with appropriate status code and detail.
    """
    if isinstance(error, FileValidationError):
        return HTTPException(status_code=400, detail=error.message)
    
    if isinstance(error, GeminiServiceError):
        return HTTPException(status_code=500, detail=error.message)
    
    if isinstance(error, OCRKTPBaseException):
        return HTTPException(status_code=500, detail=error.message)
    
    logger.error(f"Unexpected error: {error}")
    return HTTPException(
        status_code=500,
        detail=f"Terjadi kesalahan yang tidak terduga: {str(error)}"
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    OCR_KTP_ENDPOINT,
    response_model=OCRResponse,
    responses={
        200: {
            "description": "Berhasil mengekstrak data KTP",
            "model": OCRResponse
        },
        400: {
            "description": "Request tidak valid (file tidak valid)",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse
        },
    },
    summary="Ekstrak Data KTP",
    description="""
    Upload gambar KTP untuk mengekstrak data menggunakan OCR Gemini Flash.
    
    **Format yang didukung:** JPG, JPEG, PNG, WEBP
    
    **Ukuran maksimum:** 5MB
    
    **Data yang diekstrak:**
    - NIK (Nomor Induk Kependudukan)
    - Nama lengkap
    - Tempat dan tanggal lahir
    - Jenis kelamin
    - Alamat lengkap (termasuk RT/RW, Kelurahan, Kecamatan)
    - Agama
    - Status perkawinan
    - Pekerjaan
    - Kewarganegaraan
    - Masa berlaku
    """
)
async def extract_ktp(
    file: Annotated[
        UploadFile,
        File(description="File gambar KTP (JPG, PNG, atau WEBP)")
    ],
    settings: SettingsDep,
    gemini_service: GeminiServiceDep
) -> OCRResponse:
    """
    Extract data from KTP image.
    
    This endpoint accepts an image file of Indonesian KTP (ID Card)
    and returns the extracted data in structured JSON format.
    
    Args:
        file: Uploaded KTP image file.
        settings: Application settings (injected).
        gemini_service: Gemini service instance (injected).
        
    Returns:
        OCRResponse with extracted KTP data.
        
    Raises:
        HTTPException: For validation or processing errors.
    """
    try:
        # Step 1: Read file content
        file_content = await file.read()
        
        # Step 2: Validate uploaded image
        validation_result = await validate_uploaded_image(
            file_content=file_content,
            filename=file.filename,
            settings=settings
        )
        
        logger.info(
            f"Image validated: {validation_result.filename} "
            f"({validation_result.size_bytes} bytes)"
        )
        
        # Step 3: Resize image if needed
        processed_image = resize_image(validation_result.content)
        
        if processed_image.was_resized:
            logger.info(
                f"Image resized from {processed_image.original_dimensions} "
                f"to {processed_image.new_dimensions}"
            )
        
        # Step 4: Extract KTP data using Gemini
        ocr_result = await gemini_service.extract_ktp_data(
            image_bytes=processed_image.content,
            mime_type=processed_image.mime_type
        )
        
        # Step 5: Handle extraction result
        if not ocr_result.is_successful or ocr_result.data is None:
            logger.warning("OCR extraction failed or returned no data")
            return OCRResponse.failure_response(
                message="Gagal mengekstrak data dari gambar. "
                        "Pastikan gambar KTP jelas dan tidak buram."
            )
        
        # Step 6: Validate NIK and create response
        is_nik_valid = gemini_service.validate_nik(ocr_result.data.nik)
        success_message = create_success_message(is_nik_valid)
        
        logger.info(
            f"OCR extraction successful. "
            f"Confidence: {ocr_result.confidence:.2%}, "
            f"NIK valid: {is_nik_valid}"
        )
        
        return OCRResponse.success_response(
            data=ocr_result.data,
            confidence=ocr_result.confidence,
            message=success_message
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except OCRKTPBaseException as e:
        logger.warning(f"Application error: {e.message}")
        raise handle_extraction_error(e)
        
    except Exception as e:
        logger.exception(f"Unexpected error during OCR extraction: {e}")
        raise handle_extraction_error(e)


@router.get(
    HEALTH_ENDPOINT,
    response_model=HealthResponse,
    summary="Health Check",
    description="Cek status API OCR untuk monitoring dan load balancing."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the current health status of the OCR service.
    Useful for container orchestration and load balancers.
    
    Returns:
        HealthResponse with service status.
    """
    return HealthResponse(
        status="healthy",
        service="OCR KTP API",
        version=API_VERSION
    )
