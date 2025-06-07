from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse(
        "Login.html",
        {"request": request, "title": "Inicio de Sesión"}
    )

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    nombre_usuario: str = Form(...),
    contrasena: str = Form(...)
):
    usuario = await UsuarioRepository.verificar_credenciales(nombre_usuario, contrasena)

    if usuario:
        # Configurar la cookie de autenticación
        response = RedirectResponse(url="/menu", status_code=302)
        
        # Establecer cookie con el nombre de usuario
        response.set_cookie(
            key="current_user",
            value=usuario["Usuario"],
            max_age=3600,  # 1 hora de duración
            httponly=True,  # Protección contra XSS
            secure=True,    # Solo enviar sobre HTTPS (en producción)
            samesite="lax"  # Protección contra CSRF
        )
        
        # Opcional: Cookie adicional con nombre para mostrar en la UI
        response.set_cookie(
            key="user_display_name",
            value=usuario.get("Nombre", ""),
            max_age=3600
        )
        
        return response
    else:
        # Redirigir con parámetro de error
        return RedirectResponse(
            url="/login?error=invalid_credentials",
            status_code=303
<<<<<<< HEAD
        )
=======
        )
>>>>>>> 7e1abb382317b6841cbfaa312d2ba0efc525307d
