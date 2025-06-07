from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.imagenes import ImagenBase
from app.repository.imagen_rep import ImagenRepository
from datetime import date
import shutil
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# Configuración para guardar imágenes
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/vergaleria", response_class=HTMLResponse)
async def mostrar_galeria(request: Request):
    """Mostrar galería de imágenes"""
    try:
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        imagenes = await ImagenRepository.get_images_by_user(usuario)
        
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
    etiqueta: str = Form(...),
    file: UploadFile = File(...)
):
    """Subir nueva imagen a la galería"""
    try:
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        # Guardar el archivo en el sistema
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro en la base de datos
        imagen_data = ImagenBase(
            Usuario=usuario,
            codigo_acceso="default",  # Puedes modificarlo según tu lógica
            Etiqueta=etiqueta,
            Fecha=date.today(),
            Ruta=f"/{UPLOAD_DIR}/{file.filename}"
        )
        
        await ImagenRepository.create_image(imagen_data)
        
        return RedirectResponse(url="/vergaleria", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delete-image/{image_id}")
async def delete_image(request: Request, image_id: str):
    """Eliminar una imagen de la galería"""
    try:
        usuario = request.cookies.get("current_user")
        if not usuario:
            return RedirectResponse(url="/login")
        
        # Verificar que la imagen pertenece al usuario
        imagen = await ImagenRepository.get_image_by_id(image_id)
        if not imagen or imagen["Usuario"] != usuario:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        
        # Eliminar archivo físico
        if os.path.exists(imagen["Ruta"].lstrip('/')):
            os.remove(imagen["Ruta"].lstrip('/'))
        
        # Eliminar registro de la base de datos
        await ImagenRepository.delete_image(image_id)
        
        return RedirectResponse(url="/vergaleria", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))