"""
Main application module for OCR KTP API.

This module serves as the entry point for the FastAPI application.
It uses the Application Factory pattern for better testability
and configuration management.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.routers import ocr
from app.routers import pages


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def configure_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


# =============================================================================
# APPLICATION LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    
    Args:
        app: FastAPI application instance.
        
    Yields:
        None during application runtime.
    """
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("Starting OCR KTP API...")
    logger.info(f"API Version: {get_settings().api_version}")
    logger.info(f"UI available at: http://localhost:8000/")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OCR KTP API...")


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application(settings: Settings | None = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Uses the Application Factory pattern for better testability
    and flexibility in configuration.
    
    Args:
        settings: Application settings. Uses default if not provided.
        
    Returns:
        Configured FastAPI application instance.
    """
    if settings is None:
        settings = get_settings()
    
    # Configure logging
    configure_logging()
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Configure middleware
    configure_middleware(app)
    
    # Register routes
    register_routes(app, settings)
    
    return app


def configure_middleware(app: FastAPI) -> None:
    """
    Configure application middleware.
    
    Args:
        app: FastAPI application instance.
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routes(app: FastAPI, settings: Settings) -> None:
    """
    Register application routes.
    
    Args:
        app: FastAPI application instance.
        settings: Application settings.
    """
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    # Include routers
    app.include_router(pages.router)  # UI pages
    app.include_router(ocr.router)    # API endpoints
    
    # API info endpoint
    @app.get("/api", tags=["API Info"])
    async def api_info() -> dict:
        """
        API information endpoint.
        
        Returns:
            Dictionary with API metadata and useful links.
        """
        return {
            "name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            },
            "endpoints": {
                "health": "/api/v1/ocr/health",
                "extract_ktp": "/api/v1/ocr/ktp"
            }
        }
    
    # Global health endpoint
    @app.get("/health", tags=["Health"])
    async def global_health() -> dict:
        """
        Global health check endpoint.
        
        Returns:
            Health status of the application.
        """
        return {
            "status": "healthy",
            "version": settings.api_version
        }


# =============================================================================
# APPLICATION INSTANCE
# =============================================================================

# Create the application instance
app = create_application()


# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
