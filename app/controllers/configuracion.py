from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.repository.usuario_rep import UsuarioRepository
from app.repository.imagen_rep import ImagenRepository
from app.repository.stream import  StreamRepository
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
        return RedirectResponse(url="/login", status_code=303) # si no hay usuario, redirigimos a la página de login
    
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
        datos_actualizados["Password"] = password # si el usuario puso una nueva contraseña, la incluimos
   
    # actualizamos el usuario en la base de datos
    actualizado = await UsuarioRepository.actualizar_usuario_por_nombre( # actualizamos el usuario en la base de datos
        nombre_usuario=current_user,    # nombre del usuario actual
        datos_actualizados=datos_actualizados # datos actualizados del usuario
    ) 
    # si el usuario se actualizó correctamente y el nuevo nombre de usuario es diferente al actual
    # hacemos un update a las referencias de usuario en las otras colecciones
    if actualizado and Usuario != current_user:
        await ImagenRepository.update_usuario_imagen(current_user, Usuario)
        await PreguntasSeguridadRepository.update_usuario_preguntas(current_user, Usuario)
        await StreamRepository.update_usuario_stream(current_user, Usuario)
        await RegistroCarroRepository.update_usuario_carro(current_user, Usuario)

        response = RedirectResponse(url="/login", status_code=303) # redirigimos a la página de login
        response.set_cookie(key="current_user", value=Usuario) # actualizamos la cookie con el nuevo nombre de usuario
        return response

    return RedirectResponse(url="/login", status_code=303) # si no se actualizó el usuario, redirigimos a la página de login