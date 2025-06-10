from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para mostrar la página de inicio de sesión
@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    """Controlador que muestra la página de inicio de sesión"""
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        "Login.html",
        {
            "request": request,
            "title": "Inicio de Sesión",
            "error": error
        }
    )

# método post para procesar el inicio de sesión
@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    nombre_usuario: str = Form(...),
    contrasena: str = Form(...)
):
    """Controlador que procesa el inicio de sesión y establece las cookies de sesión"""
    # verificamos las credenciales del usuario en la base de datos
    usuario = await UsuarioRepository.verificar_credenciales(nombre_usuario, contrasena)

    if usuario:
        # si las credenciales son correctas, preparamos la redirección al menú
        response = RedirectResponse(url="/menu", status_code=302)
        
        # guardamos el nombre de usuario en una cookie segura para mantener la sesión
        response.set_cookie(
            key="current_user",
            value=usuario["Usuario"],
            max_age=3600,  # la cookie expira en 1 hora
            httponly=True,
            secure=False,   # cambiar a true cuando se use https en producción
            samesite="lax"
        )

        # guardamos el nombre para mostrar en una cookie para uso en la interfaz
        response.set_cookie(
            key="user_display_name",
            value=usuario.get("Nombre", ""),
            max_age=3600
        )

        return response
    else:
        # si las credenciales son incorrectas, redirigimos a la página de login con mensaje de error
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)
