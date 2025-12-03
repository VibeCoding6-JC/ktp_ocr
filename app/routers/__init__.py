"""
Routers package for OCR KTP application.

This package contains FastAPI routers for handling
HTTP endpoints.
"""

from app.routers import ocr
from app.routers import pages

__all__ = ["ocr", "pages"]
