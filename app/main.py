from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from app.config.database import verify_connection
from app.utils.udp_listener import iniciar_listener_udp

# Importa routers
from app.controllers import (
    login, manejo, salir, registro, recuperacion, verstream, galeria,
    estadisticas, configuracion, menu, acerca, instrucciones, deteccion,
    stream, guardarpreguntas, verificarpreguntas, carrito
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await verify_connection()
        print("✅ Conexión a MongoDB verificada.")
    except Exception as e:
        print("❌ Error al conectar a MongoDB:", e)
    iniciar_listener_udp()
    yield

app = FastAPI(lifespan=lifespan)

# 🔒 Middleware de autenticación
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rutas_publicas = [
            "/login",
            "/registro",
            "/recuperacion",
            "/static",
            "/favicon.ico",
            "/preguntas"  # ← ✅ AÑADE ESTO
        ]

        # Permitir rutas públicas sin autenticación
        if any(request.url.path.startswith(r) for r in rutas_publicas):
            return await call_next(request)

        # Verificar la cookie 'current_user'
        if not request.cookies.get("current_user"):
            return RedirectResponse(url="/login")

        return await call_next(request)

# Agregar middleware a la app
app.add_middleware(AuthMiddleware)

# Incluir routers
app.include_router(manejo.router)
app.include_router(salir.router)
app.include_router(registro.router)
app.include_router(recuperacion.router)
app.include_router(verstream.router)
app.include_router(galeria.router)
app.include_router(estadisticas.router)
app.include_router(configuracion.router)
app.include_router(menu.router)
app.include_router(acerca.router)
app.include_router(instrucciones.router)
app.include_router(deteccion.router)
app.include_router(stream.router)
app.include_router(guardarpreguntas.router)
app.include_router(verificarpreguntas.router)
app.include_router(carrito.router)
app.include_router(login.router)

# Montaje de archivos estáticos
app.mount("/static", StaticFiles(directory="app/views/templates/css"), name="static")
app.mount("/static", StaticFiles(directory="app/views/static"), name="static")
