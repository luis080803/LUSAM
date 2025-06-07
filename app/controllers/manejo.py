import socket
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.udp_listener import get_ultima_distancia

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# Configuración UDP
UDP_IP = "192.168.4.1"
UDP_PORT = 5000

@router.get("/manejo", response_class=HTMLResponse)
async def mostrar_pagina_manejo(request: Request):
    """Controlador que muestra la página de manejo"""
    return templates.TemplateResponse(
        "Manejo.html",
        {
            "request": request,
            "title": "Panel de Manejo",
            "usuario": request.cookies.get("current_user")
        }
    )


def ennviar_comando(command: str):
    """Envía un comando por UDP a la dirección configurada"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
        return None
# Nuevas rutas para manejar los comandos
@router.post("/manejo/command/w")
async def avanzar():
    ennviar_comando("W")
    return {"status": "OK", "command": "ADELANTE"}

@router.post("/manejo/command/s")
async def retroceder():
    ennviar_comando("S")
    return {"status": "OK", "command": "ATRAS"}

@router.post("/manejo/command/a")
async def izquierda():
    ennviar_comando("A")
    return {"status": "OK", "command": "IZQUIERDA"}

@router.post("/manejo/command/d")
async def derecha():
    ennviar_comando("D")
    return {"status": "OK", "command": "DERECHA"}

    
@router.get("/distancia_actual")
async def distancia_actual():
    distancia = get_ultima_distancia()
    if distancia:
        return {"status": "OK", "distancia": distancia}
    else:
        return {"status": "WAITING", "message": "Aún no se ha recibido distancia"}