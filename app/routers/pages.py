"""
Pages router for serving HTML templates.

This module contains routes for serving the web UI.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings


# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Create router
router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Serve the main page.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        HTMLResponse with rendered index template.
    """
    settings = get_settings()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": settings.api_title,
            "version": settings.api_version,
        }
    )
