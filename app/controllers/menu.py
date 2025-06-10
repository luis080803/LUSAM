from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/menu", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Controlador que muestra la página del menú principal"""
    return templates.TemplateResponse(
        "Menu.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )