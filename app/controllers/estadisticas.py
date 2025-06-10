from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.repository.carrito_rep import RegistroCarroRepository
from app.repository.imagen_rep import ImagenRepository
from app.repository.stream import StreamRepository

# el router se encarga de manejar las rutas de la página 
router = APIRouter()

templates = Jinja2Templates(directory="app/views/templates")

# endpoint para mostrar las estadísticas
@router.get("/estadisticas")
async def mostrar_estadisticas(request: Request):
    # obtenemos el nombre del usuario desde la cookie de sesión
    usuario = request.cookies.get("current_user")
    
    if not usuario:
        # si no hay usuario autenticado, redirigimos a la página de login
        return templates.TemplateResponse("Login.html", {
            "request": request,
            "mensaje": "Usuario no autenticado."
        })
    
    # obtenemos las estadísticas del usuario desde cada repositorio
    carros = await RegistroCarroRepository.get_carros_by_user(usuario)  # número de carros registrados
    imagenes = await ImagenRepository.get_images_by_user(usuario)       # número de imágenes capturadas
    streams = await StreamRepository.obtener_streams_por_usuario(usuario) # número de streams activos
    
    # renderizamos la página de estadísticas con los datos obtenidos
    return templates.TemplateResponse("Estadisticas.html", {
        "request": request,
        "carros_count": len(carros),      # contador de carros
        "imagenes_count": len(imagenes),  # contador de imágenes
        "streams_count": len(streams)     # contador de streams
    })