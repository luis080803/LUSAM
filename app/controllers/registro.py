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
    existente = await UsuarioRepository.obtener_usuario_por_usuario(usuario)
    if existente:
        # Pasa los datos ingresados para que se mantengan en el formulario
        return templates.TemplateResponse("registro.html", {
            "request": request,
            "usuario_existente": True,
        "form_data": {
            "nombre": nombre,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "fecha_nacimiento": fecha_nacimiento.isoformat(),  # formato ISO para <input type="date">
            "correo": correo,
            "usuario": usuario
        }

        })

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

    return RedirectResponse(
        url=f"/preguntasseguridad?usuario={usuario}",
        status_code=303
    )
