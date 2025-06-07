from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository


router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/configuracion", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Configuracion"""
    return templates.TemplateResponse(
        "Configuracion.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )

@router.post("/actualizar_perfil")
async def actualizar_perfil(
    request: Request,
    Nombre: str = Form(...),
    ApellidoPaterno: str = Form(...),
    ApellidoMaterno: str = Form(None),
    Correo: str = Form(...),
    FechaNacimiento: str = Form(...),
    Usuario: str = Form(...),
    password: str = Form("")
):
    # Obtener el usuario actual desde la cookie
    current_user = request.cookies.get("current_user")
    if not current_user:
        return RedirectResponse(url="/login")
    
    # Preparar datos a actualizar
    datos_actualizados = {
        "Nombre": Nombre,
        "ApellidoPaterno": ApellidoPaterno,
        "ApellidoMaterno": ApellidoMaterno,
        "Correo": Correo,
        "FechaNacimiento": FechaNacimiento,
        "Usuario": Usuario
    }
    
    # Agregar contraseña solo si se proporcionó
    if password:
        datos_actualizados["Password"] = password
    
    # Actualizar usando el nombre de usuario (current_user)
    actualizado = await UsuarioRepository.actualizar_usuario_por_nombre(
        nombre_usuario=current_user,
        datos_actualizados=datos_actualizados
    )
    
    # Si cambió el nombre de usuario, actualizar la cookie
    if actualizado and Usuario != current_user:
        response = RedirectResponse(url="/login", status_code=303)
        response.set_cookie(key="current_user", value=Usuario)
        return response
    
    return RedirectResponse(url="/login", status_code=303)