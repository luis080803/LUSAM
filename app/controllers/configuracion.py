from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository
from app.repository.imagen_rep import ImagenRepository
from app.repository.stream import  StreamRepository
from app.repository.preguntas import PreguntasSeguridadRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/configuracion", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request):
    """Configuracion"""
    # Obtener el usuario actual desde la cookie
    current_user = request.cookies.get("current_user")
    if not current_user:
        return RedirectResponse(url="/login")
    
    # Obtener datos completos del usuario
    usuario = await UsuarioRepository.obtener_usuario_por_usuario(current_user)
    if not usuario:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse(
        "Configuracion.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": usuario
        }
    )

@router.get("/configuracion")
async def mostrar_configuracion(request: Request):
    # Obtener el usuario actual desde la cookie
    current_user = request.cookies.get("current_user")
    if not current_user:
        return RedirectResponse(url="/login")
    
    # Obtener datos del usuario
    usuario = await UsuarioRepository.obtener_usuario_por_usuario(current_user)
    if not usuario:
        return RedirectResponse(url="/login")
    
    # Renderizar la plantilla con los datos del usuario
    return templates.TemplateResponse(
        "Configuracion.html",
        {"request": request, "usuario": usuario}
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
    
    if actualizado and Usuario != current_user:
            # 2. Actualizar referencias del usuario en todas las colecciones relacionadas
            await ImagenRepository.update_usuario_imagen(current_user, Usuario)
            await PreguntasSeguridadRepository.update_usuario_preguntas(current_user, Usuario)
            await StreamRepository.update_usuario_stream(current_user, Usuario)

            # 3. Actualizar la cookie
            response = RedirectResponse(url="/login", status_code=303)
            response.set_cookie(key="current_user", value=Usuario)
            return response

    return RedirectResponse(url="/login", status_code=303)
