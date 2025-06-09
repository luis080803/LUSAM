from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.repository.carrito_rep import RegistroCarroRepository
from app.repository.imagen_rep import ImagenRepository
from app.repository.stream import StreamRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")


@router.get("/estadisticas")
async def mostrar_estadisticas(request: Request):
    # Obtener el nombre del usuario desde la cookie
    usuario = request.cookies.get("current_user")
    
    if not usuario:
        # Redirigir o lanzar error si no hay cookie de usuario
        return templates.TemplateResponse("Login.html", {
            "request": request,
            "mensaje": "Usuario no autenticado."
        })
    
    # Obtener los datos de cada repositorio
    carros = await RegistroCarroRepository.get_carros_by_user(usuario)
    imagenes = await ImagenRepository.get_images_by_user(usuario)
    streams = await StreamRepository.obtener_streams_por_usuario(usuario)
    
    return templates.TemplateResponse("Estadisticas.html", {
        "request": request,
        "carros_count": len(carros),
        "imagenes_count": len(imagenes),
        "streams_count": len(streams)
    })