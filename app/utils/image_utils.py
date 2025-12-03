"""
Image utilities for OCR KTP application.

This module provides utilities for image validation, processing, and manipulation.
Follows Single Responsibility Principle with separate functions for each concern.
"""

import io
from dataclasses import dataclass
from typing import Optional

from PIL import Image

from app.config import Settings, get_settings
from app.constants import DEFAULT_MIME_TYPE, MAX_IMAGE_DIMENSION, MIME_TYPES
from app.exceptions import (
    FileTooLargeError,
    InvalidFilenameError,
    InvalidImageError,
    UnsupportedFileFormatError,
)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class ImageValidationResult:
    """
    Result of image validation process.
    
    Attributes:
        content: The validated image bytes.
        filename: Original filename.
        extension: File extension (lowercase).
        mime_type: MIME type of the image.
        size_bytes: Size of the image in bytes.
    """
    content: bytes
    filename: str
    extension: str
    mime_type: str
    size_bytes: int


@dataclass(frozen=True)
class ProcessedImage:
    """
    Result of image processing.
    
    Attributes:
        content: The processed image bytes.
        mime_type: MIME type of the processed image.
        was_resized: Whether the image was resized.
        original_dimensions: Original width and height.
        new_dimensions: New width and height (same as original if not resized).
    """
    content: bytes
    mime_type: str
    was_resized: bool
    original_dimensions: tuple[int, int]
    new_dimensions: tuple[int, int]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def extract_file_extension(filename: Optional[str]) -> str:
    """
    Extract and validate file extension from filename.
    
    Args:
        filename: The filename to extract extension from.
        
    Returns:
        Lowercase file extension without the dot.
        
    Raises:
        InvalidFilenameError: If filename is None, empty, or has no extension.
    """
    if not filename or not filename.strip():
        raise InvalidFilenameError("Nama file tidak valid atau kosong")
    
    parts = filename.lower().rsplit(".", 1)
    if len(parts) != 2 or not parts[1]:
        raise InvalidFilenameError(f"File '{filename}' tidak memiliki ekstensi yang valid")
    
    return parts[1]


def validate_file_extension(
    extension: str,
    allowed_extensions: tuple[str, ...]
) -> None:
    """
    Validate that file extension is in allowed list.
    
    Args:
        extension: File extension to validate (lowercase).
        allowed_extensions: Tuple of allowed extensions.
        
    Raises:
        UnsupportedFileFormatError: If extension is not allowed.
    """
    if extension not in allowed_extensions:
        raise UnsupportedFileFormatError(extension, allowed_extensions)


def validate_file_size(
    content: bytes,
    max_size_bytes: int,
    max_size_mb: int
) -> None:
    """
    Validate that file size is within limits.
    
    Args:
        content: File content in bytes.
        max_size_bytes: Maximum allowed size in bytes.
        max_size_mb: Maximum size in MB (for error message).
        
    Raises:
        FileTooLargeError: If file exceeds maximum size.
    """
    file_size = len(content)
    if file_size > max_size_bytes:
        file_size_mb = file_size / (1024 * 1024)
        raise FileTooLargeError(file_size_mb, max_size_mb)


def validate_image_integrity(content: bytes) -> None:
    """
    Validate that content is a valid image.
    
    Args:
        content: File content in bytes.
        
    Raises:
        InvalidImageError: If content is not a valid image.
    """
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except Exception as e:
        raise InvalidImageError(
            message="File bukan gambar yang valid",
            detail=str(e)
        )


async def validate_uploaded_image(
    file_content: bytes,
    filename: Optional[str],
    settings: Optional[Settings] = None
) -> ImageValidationResult:
    """
    Perform complete validation of an uploaded image file.
    
    This is the main validation function that combines all validation steps.
    
    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename of the upload.
        settings: Application settings (uses default if not provided).
        
    Returns:
        ImageValidationResult with validated image data.
        
    Raises:
        InvalidFilenameError: If filename is invalid.
        UnsupportedFileFormatError: If file format is not supported.
        FileTooLargeError: If file is too large.
        InvalidImageError: If file is not a valid image.
    """
    if settings is None:
        settings = get_settings()
    
    # Step 1: Extract and validate extension
    extension = extract_file_extension(filename)
    validate_file_extension(extension, settings.allowed_extensions)
    
    # Step 2: Validate file size
    validate_file_size(
        file_content,
        settings.max_file_size_bytes,
        settings.max_file_size_mb
    )
    
    # Step 3: Validate image integrity
    validate_image_integrity(file_content)
    
    # Step 4: Get MIME type
    mime_type = get_mime_type_for_extension(extension)
    
    return ImageValidationResult(
        content=file_content,
        filename=filename or "unknown",
        extension=extension,
        mime_type=mime_type,
        size_bytes=len(file_content)
    )


# =============================================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================================

def get_mime_type_for_extension(extension: str) -> str:
    """
    Get MIME type for a file extension.
    
    Args:
        extension: File extension (lowercase, without dot).
        
    Returns:
        MIME type string.
    """
    return MIME_TYPES.get(extension, DEFAULT_MIME_TYPE)


def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """
    Get width and height of an image.
    
    Args:
        image_bytes: Image content in bytes.
        
    Returns:
        Tuple of (width, height).
    """
    with Image.open(io.BytesIO(image_bytes)) as image:
        return image.size


def calculate_resize_dimensions(
    original_width: int,
    original_height: int,
    max_dimension: int
) -> tuple[int, int]:
    """
    Calculate new dimensions while maintaining aspect ratio.
    
    Args:
        original_width: Original image width.
        original_height: Original image height.
        max_dimension: Maximum allowed dimension.
        
    Returns:
        Tuple of (new_width, new_height).
    """
    if original_width <= max_dimension and original_height <= max_dimension:
        return original_width, original_height
    
    ratio = min(max_dimension / original_width, max_dimension / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return new_width, new_height


def resize_image(
    image_bytes: bytes,
    max_dimension: int = MAX_IMAGE_DIMENSION
) -> ProcessedImage:
    """
    Resize image if dimensions exceed maximum.
    
    Maintains aspect ratio and uses high-quality resampling.
    
    Args:
        image_bytes: Original image bytes.
        max_dimension: Maximum allowed dimension for width or height.
        
    Returns:
        ProcessedImage with resized image data.
    """
    with Image.open(io.BytesIO(image_bytes)) as image:
        original_dimensions = image.size
        new_dimensions = calculate_resize_dimensions(
            original_dimensions[0],
            original_dimensions[1],
            max_dimension
        )
        
        # Check if resize is needed
        if original_dimensions == new_dimensions:
            return ProcessedImage(
                content=image_bytes,
                mime_type=_get_mime_type_from_image(image),
                was_resized=False,
                original_dimensions=original_dimensions,
                new_dimensions=new_dimensions
            )
        
        # Perform resize
        resized_image = image.resize(new_dimensions, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        output = io.BytesIO()
        output_format, mime_type = _determine_output_format(resized_image)
        
        if output_format == "JPEG":
            # Convert to RGB if necessary for JPEG
            if resized_image.mode in ("RGBA", "LA", "P"):
                resized_image = resized_image.convert("RGB")
            resized_image.save(output, format=output_format, quality=95)
        else:
            resized_image.save(output, format=output_format)
        
        return ProcessedImage(
            content=output.getvalue(),
            mime_type=mime_type,
            was_resized=True,
            original_dimensions=original_dimensions,
            new_dimensions=new_dimensions
        )


def _get_mime_type_from_image(image: Image.Image) -> str:
    """Get MIME type from PIL Image object."""
    format_to_mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }
    return format_to_mime.get(image.format or "JPEG", DEFAULT_MIME_TYPE)


def _determine_output_format(image: Image.Image) -> tuple[str, str]:
    """
    Determine the best output format for an image.
    
    Args:
        image: PIL Image object.
        
    Returns:
        Tuple of (format_name, mime_type).
    """
    if image.mode in ("RGBA", "LA", "P"):
        return "PNG", "image/png"
    return "JPEG", "image/jpeg"
