from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.repository.stream import StreamRepository

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para mostrar la página de visualización del stream
# muestra la interfaz donde se puede ver el stream en vivo
@router.get("/verstream", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    return templates.TemplateResponse(
        "VerStream.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )

# método get para verificar si un stream está activo
# recibe el id del stream y verifica su estado en la base de datos
@router.get("/verificar_stream/{stream_id}")
async def verificar_stream(stream_id: str):
    # buscamos el stream en la base de datos
    stream = await StreamRepository.obtener_stream_activo_por_id(stream_id)
    
    if not stream:
        return {"existe": False}
    
    return {"existe": True}