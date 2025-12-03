"""
Unit tests for configuration and settings.

Tests cover:
- Settings loading from environment
- Default values
- Validation
"""

import pytest
from unittest.mock import patch
import os

from app.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""
    
    @pytest.mark.unit
    def test_settings_with_api_key(self):
        """Test settings creation with API key."""
        settings = Settings(
            gemini_api_key="test-key-123",
            max_file_size_mb=5,
            allowed_extensions_str="jpg,jpeg,png,webp"
        )
        
        assert settings.gemini_api_key == "test-key-123"
        assert settings.max_file_size_mb == 5
    
    @pytest.mark.unit
    def test_settings_allowed_extensions_list(self):
        """Test that allowed_extensions_str is parsed correctly."""
        settings = Settings(
            gemini_api_key="test-key",
            max_file_size_mb=5,
            allowed_extensions_str="jpg,jpeg,png,webp"
        )
        
        extensions = settings.allowed_extensions
        assert "jpg" in extensions
        assert "jpeg" in extensions
        assert "png" in extensions
        assert "webp" in extensions
    
    @pytest.mark.unit
    def test_settings_max_file_size_bytes(self):
        """Test max file size in bytes calculation."""
        settings = Settings(
            gemini_api_key="test-key",
            max_file_size_mb=5,
            allowed_extensions_str="jpg,png"
        )
        
        expected_bytes = 5 * 1024 * 1024
        assert settings.max_file_size_bytes == expected_bytes
    
    @pytest.mark.unit
    def test_settings_default_values(self):
        """Test default setting values."""
        settings = Settings(
            gemini_api_key="test-key"
        )
        
        # Check defaults are applied
        assert settings.max_file_size_mb >= 1
        assert len(settings.allowed_extensions) > 0
    
    @pytest.mark.unit
    def test_settings_api_title(self):
        """Test API title is set correctly."""
        settings = Settings(gemini_api_key="test")
        
        assert settings.api_title == "OCR KTP API"
    
    @pytest.mark.unit
    def test_settings_api_version(self):
        """Test API version is set correctly."""
        settings = Settings(gemini_api_key="test")
        
        assert settings.api_version == "1.0.0"


class TestGetSettings:
    """Tests for get_settings function."""
    
    @pytest.mark.unit
    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns Settings instance."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-env"}):
            settings = get_settings()
            assert isinstance(settings, Settings)
    
    @pytest.mark.unit
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-env"}):
            # Clear cache first
            get_settings.cache_clear()
            
            settings1 = get_settings()
            settings2 = get_settings()
            
            # Should be the same instance (cached)
            assert settings1 is settings2
