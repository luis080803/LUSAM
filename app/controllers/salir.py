from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para cerrar la sesión del usuario
# elimina las cookies y redirige al login
@router.get("/salir")
async def logout_user(request: Request):
    # preparamos la redirección a la página de login
    response = RedirectResponse(url="/login", status_code=303)
    
    # eliminamos las cookies de sesión para cerrar la sesión
    response.delete_cookie(key="current_user")
    response.delete_cookie(key="session_token")
    
    # limpiamos los headers de caché para evitar que se mantenga la sesión
    response.headers["Cache-Control"] = "no-store"
    
    return response