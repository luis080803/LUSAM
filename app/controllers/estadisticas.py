from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.repository.estadisticas_rep import EstadisticasRepository  

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/estadisticas", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Visualizar estadísticas por usuario"""

    usuario = request.cookies.get("current_user")
    if not usuario:
        return templates.TemplateResponse(
            "Estadisticas.html",
            {
                "request": request,
                "title": "Panel de Manejo",
                "error": "Usuario no autenticado",
                "usuario": None,
                "fotos": 0,
                "obstaculos": 0
            }
        )

    # Obtener estadísticas desde el repositorio
    estadisticas = await EstadisticasRepository.obtener_estadisticas(usuario)

    return templates.TemplateResponse(
        "Estadisticas.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": usuario,
            "fotos": estadisticas["fotos"],
            "obstaculos": estadisticas["obstaculos"]
        }
    )
