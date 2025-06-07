from fastapi import APIRouter, Request, Cookie, HTTPException, Form
from app.repository.stream import StreamRepository
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.post("/start_stream")
async def start_stream(
    request: Request,
    titulo: str = Form(...),  
    usuario: str = Cookie(None, alias="current_user"),
    matricula: str = "UVCARRITO"
):
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no autenticado")

    try:
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
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/stop_stream/{stream_id}")
async def stop_stream(stream_id: str):
    try:
        updated = await StreamRepository.actualizar_fin_stream(stream_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Stream no encontrado")
        
        return {"message": "Stream detenido correctamente"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al detener el stream: {str(e)}")
    
 