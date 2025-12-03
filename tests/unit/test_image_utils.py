"""
Unit tests for image utilities.

Tests cover:
- File extension validation
- File size validation
- Image readability validation
- Image resizing
- MIME type detection
"""

import io
import pytest
from PIL import Image
from unittest.mock import MagicMock, patch

from app.utils.image_utils import (
    extract_file_extension,
    validate_file_extension,
    validate_file_size,
    validate_uploaded_image,
    resize_image,
    get_mime_type_for_extension,
    validate_image_integrity,
)
from app.exceptions import (
    InvalidFilenameError,
    UnsupportedFileFormatError,
    FileTooLargeError,
    InvalidImageError,
)
from app.config import Settings


class TestExtractFileExtension:
    """Tests for extract_file_extension function."""
    
    @pytest.mark.unit
    def test_get_extension_jpg(self):
        """Test getting JPG extension."""
        assert extract_file_extension("photo.jpg") == "jpg"
    
    @pytest.mark.unit
    def test_get_extension_jpeg(self):
        """Test getting JPEG extension."""
        assert extract_file_extension("photo.jpeg") == "jpeg"
    
    @pytest.mark.unit
    def test_get_extension_png(self):
        """Test getting PNG extension."""
        assert extract_file_extension("image.png") == "png"
    
    @pytest.mark.unit
    def test_get_extension_webp(self):
        """Test getting WEBP extension."""
        assert extract_file_extension("image.webp") == "webp"
    
    @pytest.mark.unit
    def test_get_extension_uppercase(self):
        """Test getting extension from uppercase filename."""
        assert extract_file_extension("PHOTO.JPG") == "jpg"
    
    @pytest.mark.unit
    def test_get_extension_mixed_case(self):
        """Test getting extension from mixed case filename."""
        assert extract_file_extension("Photo.JpG") == "jpg"
    
    @pytest.mark.unit
    def test_get_extension_with_path(self):
        """Test getting extension from full path."""
        assert extract_file_extension("/path/to/photo.png") == "png"
    
    @pytest.mark.unit
    def test_get_extension_no_extension(self):
        """Test filename without extension raises error."""
        with pytest.raises(InvalidFilenameError):
            extract_file_extension("noextension")
    
    @pytest.mark.unit
    def test_get_extension_empty_string(self):
        """Test empty filename raises error."""
        with pytest.raises(InvalidFilenameError):
            extract_file_extension("")
    
    @pytest.mark.unit
    def test_get_extension_multiple_dots(self):
        """Test filename with multiple dots."""
        assert extract_file_extension("my.photo.backup.jpg") == "jpg"


class TestValidateFileExtension:
    """Tests for validate_file_extension function."""
    
    @pytest.mark.unit
    def test_valid_jpg_extension(self):
        """Test valid JPG extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        # Should not raise
        validate_file_extension("jpg", allowed)
    
    @pytest.mark.unit
    def test_valid_jpeg_extension(self):
        """Test valid JPEG extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        validate_file_extension("jpeg", allowed)
    
    @pytest.mark.unit
    def test_valid_png_extension(self):
        """Test valid PNG extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        validate_file_extension("png", allowed)
    
    @pytest.mark.unit
    def test_valid_webp_extension(self):
        """Test valid WEBP extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        validate_file_extension("webp", allowed)
    
    @pytest.mark.unit
    def test_invalid_gif_extension(self):
        """Test invalid GIF extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("gif", allowed)
    
    @pytest.mark.unit
    def test_invalid_bmp_extension(self):
        """Test invalid BMP extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("bmp", allowed)
    
    @pytest.mark.unit
    def test_invalid_pdf_extension(self):
        """Test invalid PDF extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("pdf", allowed)


class TestValidateFileSize:
    """Tests for validate_file_size function."""
    
    @pytest.mark.unit
    def test_valid_small_file(self):
        """Test valid small file size."""
        # 1 MB
        content = b"x" * (1 * 1024 * 1024)
        max_bytes = 5 * 1024 * 1024
        # Should not raise
        validate_file_size(content, max_bytes, 5)
    
    @pytest.mark.unit
    def test_valid_at_limit(self):
        """Test file exactly at size limit."""
        # 5 MB (exactly at limit)
        content = b"x" * (5 * 1024 * 1024)
        max_bytes = 5 * 1024 * 1024
        validate_file_size(content, max_bytes, 5)
    
    @pytest.mark.unit
    def test_invalid_over_limit(self):
        """Test file over size limit."""
        # 6 MB (over 5MB limit)
        content = b"x" * (6 * 1024 * 1024)
        max_bytes = 5 * 1024 * 1024
        with pytest.raises(FileTooLargeError):
            validate_file_size(content, max_bytes, 5)
    
    @pytest.mark.unit
    def test_zero_size(self):
        """Test zero size file."""
        content = b""
        max_bytes = 5 * 1024 * 1024
        validate_file_size(content, max_bytes, 5)
    
    @pytest.mark.unit
    def test_tiny_file(self):
        """Test very small file."""
        content = b"x" * 100
        max_bytes = 5 * 1024 * 1024
        validate_file_size(content, max_bytes, 5)


class TestValidateUploadedImage:
    """Tests for validate_uploaded_image function."""
    
    @pytest.mark.unit
    async def test_validate_valid_jpeg(
        self, 
        valid_image_bytes: bytes, 
        test_settings: Settings
    ):
        """Test validation of valid JPEG image."""
        result = await validate_uploaded_image(
            file_content=valid_image_bytes,
            filename="test.jpg",
            settings=test_settings
        )
        
        assert result.extension == "jpg"
        assert result.mime_type == "image/jpeg"
    
    @pytest.mark.unit
    async def test_validate_valid_png(
        self, 
        valid_png_bytes: bytes, 
        test_settings: Settings
    ):
        """Test validation of valid PNG image."""
        result = await validate_uploaded_image(
            file_content=valid_png_bytes,
            filename="test.png",
            settings=test_settings
        )
        
        assert result.extension == "png"
    
    @pytest.mark.unit
    async def test_validate_invalid_extension(
        self, 
        valid_image_bytes: bytes, 
        test_settings: Settings
    ):
        """Test validation with invalid extension."""
        with pytest.raises(UnsupportedFileFormatError):
            await validate_uploaded_image(
                file_content=valid_image_bytes,
                filename="test.gif",
                settings=test_settings
            )
    
    @pytest.mark.unit
    async def test_validate_file_too_large(
        self, 
        test_settings: Settings
    ):
        """Test validation with file too large."""
        # Create content larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)
        
        with pytest.raises(FileTooLargeError):
            await validate_uploaded_image(
                file_content=large_content,
                filename="large.jpg",
                settings=test_settings
            )
    
    @pytest.mark.unit
    async def test_validate_invalid_image_content(
        self, 
        invalid_file_bytes: bytes, 
        test_settings: Settings
    ):
        """Test validation with invalid image content."""
        with pytest.raises(InvalidImageError):
            await validate_uploaded_image(
                file_content=invalid_file_bytes,
                filename="fake.jpg",
                settings=test_settings
            )


class TestResizeImage:
    """Tests for resize_image function."""
    
    @pytest.mark.unit
    def test_resize_large_image(self, oversized_dimension_image: bytes):
        """Test resizing image larger than max dimension."""
        result = resize_image(oversized_dimension_image, max_dimension=2048)
        
        # Verify the resized image
        img = Image.open(io.BytesIO(result.content))
        assert img.width <= 2048
        assert img.height <= 2048
        assert result.was_resized is True
    
    @pytest.mark.unit
    def test_no_resize_needed(self, valid_image_bytes: bytes):
        """Test that small images are not resized."""
        result = resize_image(valid_image_bytes, max_dimension=2048)
        
        assert result.was_resized is False
        assert result.original_dimensions == result.new_dimensions
    
    @pytest.mark.unit
    def test_resize_maintains_aspect_ratio(self, oversized_dimension_image: bytes):
        """Test that resizing maintains aspect ratio."""
        original_img = Image.open(io.BytesIO(oversized_dimension_image))
        original_ratio = original_img.width / original_img.height
        
        result = resize_image(oversized_dimension_image, max_dimension=1024)
        resized_img = Image.open(io.BytesIO(result.content))
        resized_ratio = resized_img.width / resized_img.height
        
        # Ratio should be approximately the same
        assert abs(original_ratio - resized_ratio) < 0.01


class TestGetMimeType:
    """Tests for get_mime_type_for_extension function."""
    
    @pytest.mark.unit
    def test_mime_type_jpg(self):
        """Test MIME type for JPG."""
        assert get_mime_type_for_extension("jpg") == "image/jpeg"
    
    @pytest.mark.unit
    def test_mime_type_jpeg(self):
        """Test MIME type for JPEG."""
        assert get_mime_type_for_extension("jpeg") == "image/jpeg"
    
    @pytest.mark.unit
    def test_mime_type_png(self):
        """Test MIME type for PNG."""
        assert get_mime_type_for_extension("png") == "image/png"
    
    @pytest.mark.unit
    def test_mime_type_webp(self):
        """Test MIME type for WEBP."""
        assert get_mime_type_for_extension("webp") == "image/webp"
    
    @pytest.mark.unit
    def test_mime_type_unknown(self):
        """Test MIME type for unknown extension."""
        result = get_mime_type_for_extension("xyz")
        # Should return default MIME type
        assert result == "application/octet-stream"


class TestValidateImageIntegrity:
    """Tests for validate_image_integrity function."""
    
    @pytest.mark.unit
    def test_valid_image(self, valid_image_bytes: bytes):
        """Test validation of valid image."""
        # Should not raise
        validate_image_integrity(valid_image_bytes)
    
    @pytest.mark.unit
    def test_invalid_image(self, invalid_file_bytes: bytes):
        """Test validation of invalid image."""
        with pytest.raises(InvalidImageError):
            validate_image_integrity(invalid_file_bytes)

