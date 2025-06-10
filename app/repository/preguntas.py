from datetime import datetime
from typing import List, Optional, Dict
from app.models.preguntasrecuperacion import PreguntasSeguridadBase
from app.config.database import db
from pymongo.errors import DuplicateKeyError
from app.utils.password_utils import verify_password

# repositorio que maneja las preguntas de seguridad de los usuarios
class PreguntasSeguridadRepository:
    # nombre de la colección en mongodb para las preguntas
    COLLECTION_NAME = "preguntas_seguridad"

    # crea un nuevo registro de preguntas de seguridad
    @staticmethod
    async def create_preguntas(preguntas: PreguntasSeguridadBase) -> Dict:
        preguntas_dict = preguntas.model_dump()  # convertimos el modelo a diccionario
        preguntas_dict["fecha_creacion"] = datetime.utcnow()  # agregamos la fecha de creación
            
        await db[PreguntasSeguridadRepository.COLLECTION_NAME].insert_one(preguntas_dict)  # guardamos en la base de datos
            
        return {
            "success": True,
            "message": "Preguntas de seguridad creadas correctamente"
        }

    # actualiza las preguntas de seguridad de un usuario
    @staticmethod
    async def update_preguntas(usuario: str, preguntas: PreguntasSeguridadBase) -> Dict:
        preguntas_dict = preguntas.model_dump()  # convertimos el modelo a diccionario
        preguntas_dict["fecha_actualizacion"] = datetime.utcnow()  # agregamos la fecha de actualización
            
        result = await db[PreguntasSeguridadRepository.COLLECTION_NAME].update_one(  # actualizamos en la base de datos
            {"Usuario": usuario},
            {"$set": preguntas_dict}
        )
            
        if result.modified_count == 0:  # si no se encontró el usuario o no hubo cambios
            return {
                "success": False,
                "message": "No se encontró el usuario o no hubo cambios"
            }
                
        return {
            "success": True,
            "message": "Preguntas de seguridad actualizadas correctamente"
        }

    # obtiene las preguntas de seguridad de un usuario
    @staticmethod
    async def get_preguntas_by_user(usuario: str) -> Optional[Dict]:
        preguntas = await db[PreguntasSeguridadRepository.COLLECTION_NAME].find_one(  # buscamos en la base de datos
            {"Usuario": usuario}
        )    
        if preguntas:
            preguntas["_id"] = str(preguntas["_id"])  # convertimos el id a string
            return preguntas
        return None

    # verifica si las respuestas proporcionadas son correctas
    @staticmethod
    async def verify_respuestas(usuario: str, respuestas: List[str]) -> Dict:
        preguntas = await PreguntasSeguridadRepository.get_preguntas_by_user(usuario)  # obtenemos las preguntas del usuario
            
        if not preguntas:  # si no se encontró el usuario
            return {
                "success": False,
                "message": "Usuario no encontrado"
            }
                
        stored_answers = preguntas["respuestas"]  # obtenemos las respuestas almacenadas
        for i, (stored, provided) in enumerate(zip(stored_answers, respuestas)):  # comparamos cada respuesta
            if not verify_password(provided.lower().strip(), stored):  # verificamos si coinciden
                return {
                    "success": False,
                    "message": "Respuestas incorrectas"
                }
            
        return {
            "success": True,
            "message": "Respuestas correctas"
        }

    # actualiza el usuario asociado a las preguntas de seguridad
    @staticmethod
    async def update_usuario_preguntas(usuario_antiguo: str, usuario_nuevo: str) -> Dict:
        result = await db[PreguntasSeguridadRepository.COLLECTION_NAME].update_many(  # actualizamos todos los registros del usuario
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )

        if result.modified_count == 0:  # si no se encontró el usuario o no hubo cambios
            return {
                "success": False,
                "message": "No se encontró el usuario o no hubo cambios"
            }

        return {
            "success": True,
            "message": f"Se actualizaron {result.modified_count} documento(s)"  # retornamos cuántos documentos se actualizaron
        }
