from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.repository.preguntas import PreguntasSeguridadRepository

# el router se encarga de manejar las rutas de la página
router = APIRouter()

# modelo para validar los datos de entrada al verificar respuestas
class VerificarRespuestasInput(BaseModel):
    usuario: str
    respuestas: List[str]

# método get para obtener las preguntas de seguridad de un usuario
# recibe el nombre de usuario y devuelve sus preguntas
@router.get("/preguntas/{usuario}") 
async def obtener_preguntas(usuario: str):
    # buscamos las preguntas del usuario en la base de datos
    preguntas = await PreguntasSeguridadRepository.get_preguntas_by_user(usuario)
    if preguntas and "preguntas" in preguntas:
        return {
            "success": True,
            "preguntas": preguntas["preguntas"]
        }
    # si no encontramos las preguntas, lanzamos una excepción
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# método post para verificar las respuestas del usuario
# recibe el usuario y sus respuestas, y verifica si son correctas
@router.post("/verificar_respuestas")
async def verificar_respuestas(data: VerificarRespuestasInput):
    # verificamos las respuestas en la base de datos
    resultado = await PreguntasSeguridadRepository.verify_respuestas(
        usuario=data.usuario,
        respuestas=data.respuestas
    )

    if resultado["success"]:
        return resultado
    # si las respuestas son incorrectas, lanzamos una excepción
    raise HTTPException(status_code=400, detail=resultado["message"])
