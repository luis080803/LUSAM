from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from app.models.usuario import UsuarioBase
from app.repository.usuario_rep import UsuarioRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/registro", response_class=HTMLResponse)
async def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@router.post("/registro", response_class=HTMLResponse)
async def registrar_usuario(
    request: Request,
    nombre: str = Form(...),
    apellido_paterno: str = Form(...),
    apellido_materno: str = Form(None),
    fecha_nacimiento: date = Form(...),
    correo: str = Form(...),
    usuario: str = Form(...),
    password: str = Form(...),
):

    nuevo_usuario = UsuarioBase(
        Nombre=nombre,
        ApellidoPaterno=apellido_paterno,
        ApellidoMaterno=apellido_materno,
        Correo=correo,
        FechaNacimiento=fecha_nacimiento,
        Usuario=usuario,
        Password=password,  
        Status=True,
        Fecha_registro=date.today()
    )
 

    await UsuarioRepository.crear_usuario(nuevo_usuario)

    # Redirigir a preguntas de seguridad pasando el usuario como parámetro
    return RedirectResponse(
        url=f"/preguntasseguridad?usuario={usuario}",  # Pasa el usuario como query param
        status_code=303
    )