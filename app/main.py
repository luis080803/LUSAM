"""
PROYECTO: LUSAM SELF - DRIVING
Integrantes:   García Velandia Samuel Obed S21002413
               Bravo Ibañez Luis Fernando S21002428
Colaboradores: Contreras Matla Luis Fernando S21020225
               Quintero Ortíz Miguel Isaac S21002439

Para las materias: 
Diseño de Aplicaciones Web 
Bases de Datos Distribuidas y en la Nube
"""

# importaciones necesarias para la aplicación
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

# importaciones de la base de datos y utilidades
from app.config.database import verify_connection
from app.utils.udp_listener import iniciar_listener_udp

# importación de todos los controladores de la aplicación
# estos manejarán toda la lógica de la interacción entre el usuario y la aplicación, siendo una especie de 
# servlet, pero integrado en un controlador completo. 
from app.controllers import (
    login, manejo, salir, registro, recuperacion, verstream, galeria,
    estadisticas, configuracion, menu, acerca, instrucciones, deteccion,
    stream, guardarpreguntas, verificarpreguntas, carrito
)

# gestor del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # verifica la conexión a mongodb al iniciar
        await verify_connection()
        print("Conexión a MongoDB verificada.")
    except Exception as e:
        print("Error al conectar a MongoDB:", e)
    # inicia el listener udp para comunicación en tiempo real
    iniciar_listener_udp()
    yield

# creación de la aplicación fastapi
app = FastAPI(lifespan=lifespan)

# middleware para manejar la autenticación de usuarios, verifica cada petición antes de que llegue a los controladores
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # lista de rutas que no requieren autenticación
        rutas_publicas = [
            "/login",
            "/registro",
            "/recuperacion",
            "/static",
            "/favicon.ico",
            "/preguntas"
        ]

        # si la ruta es pública, permite el acceso sin autenticación
        if any(request.url.path.startswith(r) for r in rutas_publicas):
            return await call_next(request)

        # verifica si existe la cookie de usuario, si no, redirige a la página de login
        if not request.cookies.get("current_user"):
            return RedirectResponse(url="/login")

        return await call_next(request)

# se agrega el middleware de autenticación a la aplicación, para que se aplique en todas las peticiones http
app.add_middleware(AuthMiddleware)

# se incluyen todos los routers de la aplicación, que son los conjuntos de rutas
# se registran todos los controladores en un solo lugar para que la aplicación sepa qué rutas manejar
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

# configuran el servido de los archivos estáticos 
app.mount("/static/css", StaticFiles(directory="app/views/templates/css"), name="css") # sirve los archivos css de app/views/templates/css
app.mount("/static", StaticFiles(directory="app/views/static"), name="static") # sirve los archivos estáticos de app/views/static
