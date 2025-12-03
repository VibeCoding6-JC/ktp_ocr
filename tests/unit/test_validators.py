"""
Unit tests for validators.

Tests cover:
- NIK validation
- Filename validation
- Extension validation
"""

import pytest

from app.utils.image_utils import extract_file_extension, validate_file_extension
from app.exceptions import InvalidFilenameError, UnsupportedFileFormatError


class TestNIKValidation:
    """Tests for NIK-related validations in KTPData model."""
    
    @pytest.mark.unit
    def test_valid_nik_16_digits(self, valid_ktp_data: dict):
        """Test valid 16-digit NIK."""
        from app.models.ktp import KTPData
        ktp = KTPData(**valid_ktp_data)
        # NIK should be stored correctly
        assert ktp.nik == "3201234567890001"
        assert len(ktp.nik) == 16
    
    @pytest.mark.unit
    def test_nik_can_be_none(self):
        """Test that NIK can be None (optional field)."""
        from app.models.ktp import KTPData
        ktp = KTPData(nik=None, nama="TEST")
        assert ktp.nik is None
    
    @pytest.mark.unit
    def test_short_nik_is_accepted(self):
        """Test that short NIK is accepted (model doesn't validate length)."""
        from app.models.ktp import KTPData
        # Model accepts any string, validation is done separately
        ktp = KTPData(nik="123", nama="TEST")
        assert ktp.nik == "123"


class TestFilenameValidation:
    """Tests for filename validation."""
    
    @pytest.mark.unit
    def test_valid_filename_with_jpg(self):
        """Test valid filename with JPG extension."""
        ext = extract_file_extension("photo.jpg")
        assert ext == "jpg"
    
    @pytest.mark.unit
    def test_valid_filename_with_png(self):
        """Test valid filename with PNG extension."""
        ext = extract_file_extension("image.png")
        assert ext == "png"
    
    @pytest.mark.unit
    def test_invalid_filename_no_extension(self):
        """Test invalid filename without extension."""
        with pytest.raises(InvalidFilenameError):
            extract_file_extension("noextension")
    
    @pytest.mark.unit
    def test_invalid_filename_empty(self):
        """Test invalid empty filename."""
        with pytest.raises(InvalidFilenameError):
            extract_file_extension("")
    
    @pytest.mark.unit
    def test_invalid_filename_none(self):
        """Test invalid None filename."""
        with pytest.raises(InvalidFilenameError):
            extract_file_extension(None)
    
    @pytest.mark.unit
    def test_filename_with_spaces(self):
        """Test filename with spaces."""
        ext = extract_file_extension("my photo.jpg")
        assert ext == "jpg"
    
    @pytest.mark.unit
    def test_filename_uppercase_extension(self):
        """Test filename with uppercase extension."""
        ext = extract_file_extension("PHOTO.JPG")
        assert ext == "jpg"


class TestExtensionValidation:
    """Tests for extension validation."""
    
    @pytest.mark.unit
    def test_valid_extensions(self):
        """Test validation of valid extensions."""
        allowed = ("jpg", "jpeg", "png", "webp")
        
        # These should not raise
        validate_file_extension("jpg", allowed)
        validate_file_extension("jpeg", allowed)
        validate_file_extension("png", allowed)
        validate_file_extension("webp", allowed)
    
    @pytest.mark.unit
    def test_invalid_gif_extension(self):
        """Test invalid GIF extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("gif", allowed)
    
    @pytest.mark.unit
    def test_invalid_pdf_extension(self):
        """Test invalid PDF extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("pdf", allowed)
    
    @pytest.mark.unit
    def test_invalid_bmp_extension(self):
        """Test invalid BMP extension."""
        allowed = ("jpg", "jpeg", "png", "webp")
        with pytest.raises(UnsupportedFileFormatError):
            validate_file_extension("bmp", allowed)
