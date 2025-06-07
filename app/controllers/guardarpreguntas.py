from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.preguntas import PreguntasSeguridadRepository
from app.models.preguntasrecuperacion import PreguntasSeguridadBase

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/preguntasseguridad", response_class=HTMLResponse)
async def mostrar_pagina_verstream(request: Request, usuario: str = Query(...)):
    """Muestra la página de preguntas de seguridad con el usuario desde query param"""
    return templates.TemplateResponse(
        "Preguntas.html",
        {
            "request": request,
            "title": "Preguntas de recuperación",
            "usuario": usuario
        }
    )

@router.post("/guardar-preguntas-seguridad", response_class=HTMLResponse)
async def guardar_preguntas_seguridad(
    request: Request,
    pregunta1: str = Form(...),
    respuesta1: str = Form(...),
    pregunta2: str = Form(...),
    respuesta2: str = Form(...),
    usuario: str = Form(...)
):
    """Guarda o actualiza las preguntas de seguridad del usuario"""
    preguntas_data = PreguntasSeguridadBase(
        Usuario=usuario,
        preguntas=[pregunta1, pregunta2],
        respuestas=[respuesta1, respuesta2]
    )

    result = await PreguntasSeguridadRepository.create_preguntas(preguntas_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Error al guardar las preguntas")
        )
    
    # Redirigir a la página de login
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
