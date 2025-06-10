from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from app.models.usuario import UsuarioBase
from app.repository.usuario_rep import UsuarioRepository

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para mostrar el formulario de registro
# muestra la página donde el usuario puede crear su cuenta
@router.get("/registro", response_class=HTMLResponse)
async def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

# método post para procesar el registro de un nuevo usuario
# recibe los datos del formulario y crea el usuario en la base de datos
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
    # convertimos el nombre de usuario a minúsculas para consistencia
    usuario = usuario.lower()
    
    # verificamos si el usuario ya existe en la base de datos
    existente = await UsuarioRepository.obtener_usuario_por_usuario(usuario)
    if existente:
        # si el usuario existe, mostramos el formulario de nuevo
        # y mantenemos los datos ingresados para que no se pierdan
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

    # creamos el objeto usuario con los datos del formulario
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
    
    # guardamos el nuevo usuario en la base de datos
    await UsuarioRepository.crear_usuario(nuevo_usuario)

    # redirigimos al usuario a la página de preguntas de seguridad
    return RedirectResponse(
        url=f"/preguntasseguridad?usuario={usuario}",
        status_code=303
    )
