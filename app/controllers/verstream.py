from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.repository.stream import StreamRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/verstream", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Visualiza el Stream"""
    return templates.TemplateResponse(
        "VerStream.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )


@router.get("/verificar_stream/{stream_id}")
async def verificar_stream(stream_id: str):
    # Usa tu repositorio para verificar si el stream existe y está activo
    stream = await StreamRepository.obtener_stream_activo_por_id(stream_id)
    
    if not stream:
        return {"existe": False}
    
    return {"existe": True}