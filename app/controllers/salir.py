from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/salir")
async def logout_user(request: Request):
    """Endpoint para cerrar sesión"""
    response = RedirectResponse(url="/login", status_code=303)
    
    # Eliminar todas las cookies de sesión
    response.delete_cookie(key="current_user")
    response.delete_cookie(key="session_token")
    
    #Limpiar headers de autenticación
    response.headers["Cache-Control"] = "no-store"
    
    return response