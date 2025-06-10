from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.imagenes import ImagenBase
from app.repository.imagen_rep import ImagenRepository
from datetime import date
import shutil
import os

# creación del router para manejar las rutas
router = APIRouter()
# configuración de las plantillas html
templates = Jinja2Templates(directory="app/views/templates")

# configuración del directorio donde se guardarán las imágenes subidas
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # crea el directorio si no existe

@router.get("/vergaleria", response_class=HTMLResponse)
async def mostrar_galeria(request: Request):
    """Mostrar galería de imágenes"""
    try:
        # verificamos si el usuario está autenticado
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        # obtenemos todas las imágenes del usuario desde la base de datos
        imagenes = await ImagenRepository.get_images_by_user(usuario)
        
        # renderizamos la página de galería con las imágenes
        return templates.TemplateResponse(
            "Galeria.html",
            {
                "request": request,
                "title": "Galería de Capturas",
                "usuario": usuario,
                "imagenes": imagenes
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-image")
async def upload_image(
    request: Request,
    etiqueta: str = Form(...),  # etiqueta para la imagen
    file: UploadFile = File(...)  # archivo de imagen a subir
):
    """Subir nueva imagen a la galería"""
    try:
        # verificamos si el usuario está autenticado
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        # guardamos el archivo en el sistema de archivos
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # creamos el registro de la imagen en la base de datos
        imagen_data = ImagenBase(
            Usuario=usuario,
            codigo_acceso="default",  # código de acceso por defecto
            Etiqueta=etiqueta,        # etiqueta de la imagen
            Fecha=date.today(),       # fecha de subida
            Ruta=f"/{UPLOAD_DIR}/{file.filename}"  # ruta donde se guardó
        )
        
        # guardamos la imagen en la base de datos
        await ImagenRepository.create_image(imagen_data)
        
        # redirigimos a la galería después de subir
        return RedirectResponse(url="/vergaleria", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delete-image/{image_id}")
async def delete_image(request: Request, image_id: str):
    """Eliminar una imagen de la galería"""
    try:
        # verificamos si el usuario está autenticado
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        # verificamos que la imagen existe y pertenece al usuario
        imagen = await ImagenRepository.get_image_by_id(image_id)
        if not imagen or imagen["Usuario"] != usuario:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        
        # eliminamos el archivo físico del sistema
        if os.path.exists(imagen["Ruta"].lstrip('/')):
            os.remove(imagen["Ruta"].lstrip('/'))
        
        # eliminamos el registro de la base de datos
        await ImagenRepository.delete_image(image_id)
        
        # redirigimos a la galería después de eliminar
        return RedirectResponse(url="/vergaleria", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))