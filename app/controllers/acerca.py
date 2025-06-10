from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


# el router se encarga de manejar las rutas de la página 
router = APIRouter()
# jinja2 que busca los archivos html en el directorio app/views/templates
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/acerca", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Acerca de"""
    # vamos a mostrar la página acerca.html con:
    # - la información de la petición
    # - el título que aparecerá en el navegador
    # - el nombre del usuario que está navegando (si hay uno)
    return templates.TemplateResponse(
        "Acerca.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )