from fastapi import APIRouter, Request, Cookie, HTTPException, Form
from app.repository.stream import StreamRepository
from fastapi.templating import Jinja2Templates

# el router se encarga de manejar las rutas de la página
router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

# método post para iniciar un nuevo stream
# recibe el título del stream y verifica que el usuario esté autenticado
@router.post("/start_stream")
async def start_stream(
    request: Request,
    titulo: str = Form(...),  
    usuario: str = Cookie(None, alias="current_user"),
    matricula: str = "UVCARRITO"
):
    # verificamos que el usuario esté autenticado
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no autenticado")

    try:
        # creamos un nuevo stream en la base de datos
        stream = await StreamRepository.crear_stream(
            usuario=usuario,
            titulo=titulo,
            matricula=matricula
        )
        return {
            "message": "Stream iniciado correctamente",
            "stream_id": stream["_id"],
            "titulo": stream["titulo"]
        }
    except Exception as e:
        # si hay algún error, lanzamos un http exception
        raise HTTPException(status_code=500, detail=str(e))
    

# método post para detener un stream existente
# recibe el id del stream y actualiza su estado
@router.post("/stop_stream/{stream_id}")
async def stop_stream(stream_id: str):
    try:
        # actualizamos el estado del stream en la base de datos
        updated = await StreamRepository.actualizar_fin_stream(stream_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Stream no encontrado")
        
        return {"message": "Stream detenido correctamente"}
    
    except Exception as e:
        # si hay algún error se lanza una excepción
        raise HTTPException(status_code=500, detail=f"Error al detener el stream: {str(e)}")
    
 