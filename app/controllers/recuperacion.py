# app/controllers/auth_controller.py
from fastapi import APIRouter, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse,  RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")


@router.get("/recuperacion", response_class=HTMLResponse)
async def mostrar_recuperacion(request: Request):
    return templates.TemplateResponse(
        "recuperacion.html",
        {"request": request, "title": "Recuperar Contraseña"}
    )


@router.get("/cambiocontrasena", response_class=HTMLResponse)
async def mostrar_cambio_contrasena(request: Request, usuario: str):
    return templates.TemplateResponse("Cambiocontrasena.html", {"request": request, "usuario": usuario})

@router.post("/recuperacioncontrasena", status_code=status.HTTP_302_FOUND)
async def cambiar_contrasena(
    usuario: str = Form(...),
    password: str = Form(...)
):
    actualizado = await UsuarioRepository.cambiar_contrasena_plana(
        nombre_usuario=usuario,
        nueva_contrasena=password
    )

    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Redirigir al login
    return RedirectResponse(url="/login", status_code=302)