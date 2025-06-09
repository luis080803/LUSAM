from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        "Login.html",
        {
            "request": request,
            "title": "Inicio de Sesión",
            "error": error
        }
    )

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    nombre_usuario: str = Form(...),
    contrasena: str = Form(...)
):
    usuario = await UsuarioRepository.verificar_credenciales(nombre_usuario, contrasena)

    if usuario:
        # Usuario válido: establecer cookies y redirigir
        response = RedirectResponse(url="/menu", status_code=302)
        
        response.set_cookie(
            key="current_user",
            value=usuario["Usuario"],
            max_age=3600,  # 1 hora
            httponly=True,
            secure=False,   # Cambia a True en producción con HTTPS
            samesite="lax"
        )

        response.set_cookie(
            key="user_display_name",
            value=usuario.get("Nombre", ""),
            max_age=3600
        )

        return response
    else:
        # Usuario inválido: redirigir con error
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)
