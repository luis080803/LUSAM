from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository
from app.repository.imagen_rep import ImagenRepository
from app.repository.stream import StreamRepository
from app.repository.preguntas import PreguntasSeguridadRepository
from app.repository.carrito_rep import RegistroCarroRepository
from datetime import datetime

# el router se encarga de manejar las rutas de la página 
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método get para mostrar la página de configuración
@router.get("/configuracion")
async def mostrar_configuracion(request: Request):
    current_user = request.cookies.get("current_user")
    if not current_user:
        return RedirectResponse(url="/login")
    
    usuario = await UsuarioRepository.obtener_usuario_por_usuario(current_user)
    if not usuario:
        return RedirectResponse(url="/login")
    
    if usuario.get("FechaNacimiento"): # si existe la fecha de nacimiento
        if isinstance(usuario["FechaNacimiento"], datetime): # si es una instancia de datetime
            usuario["FechaNacimiento"] = usuario["FechaNacimiento"].strftime("%Y-%m-%d") 
            # formateamos la fecha de nacimiento a YYYY-MM-DD
    
    # mostramos la página de configuración con los datos del usuario para que estén disponibles en edición
    return templates.TemplateResponse(
        "Configuracion.html",
        {"request": request, "usuario": usuario}
    )

# método post para actualizar el perfil del usuario
@router.post("/actualizar_perfil")  
# recibimos los datos del formulario de la página de configuración
async def actualizar_perfil( 
    request: Request, 
    Nombre: str = Form(...),
    ApellidoPaterno: str = Form(...),
    ApellidoMaterno: str = Form(None),
    Correo: str = Form(...),
    FechaNacimiento: str = Form(...),
    Usuario: str = Form(...),
    password: str = Form("")
):
    # obtenemos el usuario actual desde la cookie
    current_user = request.cookies.get("current_user")
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # si el nuevo usuario es diferente al actual, verificamos que no exista
    if Usuario != current_user:
        usuario_existente = await UsuarioRepository.obtener_usuario_por_usuario(Usuario)
        if usuario_existente:
            # si existe, mostramos el formulario de nuevo con mensaje de error
            usuario = await UsuarioRepository.obtener_usuario_por_usuario(current_user)
            if usuario.get("FechaNacimiento"):
                if isinstance(usuario["FechaNacimiento"], datetime):
                    usuario["FechaNacimiento"] = usuario["FechaNacimiento"].strftime("%Y-%m-%d")
            
            return templates.TemplateResponse(
                "Configuracion.html",
                {
                    "request": request,
                    "usuario": usuario,
                    "usuario_existente": True
                }
            )
    
    # preparamos los datos que vamos a actualizar
    datos_actualizados = {
        "Nombre": Nombre,
        "ApellidoPaterno": ApellidoPaterno,
        "ApellidoMaterno": ApellidoMaterno,
        "Correo": Correo,
        "FechaNacimiento": datetime.strptime(FechaNacimiento, "%Y-%m-%d"),
        "Usuario": Usuario
    }

    if password:
        datos_actualizados["Password"] = password
   
    # actualizamos el usuario en la base de datos
    actualizado = await UsuarioRepository.actualizar_usuario_por_nombre(
        nombre_usuario=current_user,
        datos_actualizados=datos_actualizados
    ) 

    # si el usuario se actualizó correctamente y el nuevo nombre de usuario es diferente al actual
    if actualizado and Usuario != current_user:
        await ImagenRepository.update_usuario_imagen(current_user, Usuario)
        await PreguntasSeguridadRepository.update_usuario_preguntas(current_user, Usuario)
        await StreamRepository.update_usuario_stream(current_user, Usuario)
        await RegistroCarroRepository.update_usuario_carro(current_user, Usuario)

        response = RedirectResponse(url="/login", status_code=303)
        response.set_cookie(key="current_user", value=Usuario)
        return response

    return RedirectResponse(url="/login", status_code=303)