# app/controllers/auth_controller.py
from fastapi import APIRouter, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse,  RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para mostrar la página de recuperación de contraseña
@router.get("/recuperacion", response_class=HTMLResponse)
async def mostrar_recuperacion(request: Request):
    return templates.TemplateResponse(
        "recuperacion.html",
        {"request": request, "title": "Recuperar Contraseña"}
    )

# método get para mostrar la página de cambio de contraseña
@router.get("/cambiocontrasena", response_class=HTMLResponse)
async def mostrar_cambio_contrasena(request: Request, usuario: str):
    return templates.TemplateResponse("Cambiocontrasena.html", {"request": request, "usuario": usuario})

# método post para procesar el cambio de contraseña
@router.post("/recuperacioncontrasena", status_code=status.HTTP_302_FOUND)
async def cambiar_contrasena(
    usuario: str = Form(...),
    password: str = Form(...)
):
    # actualizamos la contraseña del usuario en la base de datos
    actualizado = await UsuarioRepository.cambiar_contrasena_plana(
        nombre_usuario=usuario,
        nueva_contrasena=password
    )

    if not actualizado: # si no se pudo actualizar, lanzamos una excepción http
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # redirigimos al usuario a la página de login
    return RedirectResponse(url="/login", status_code=302)