from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/instrucciones", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Instrucciones de uso"""
    return templates.TemplateResponse(
        "Instrucciones.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )