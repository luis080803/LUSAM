from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/acerca", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Acerca de"""
    return templates.TemplateResponse(
        "Acerca.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )