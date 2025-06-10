from datetime import datetime
from typing import List, Optional, Dict
from app.models.preguntasrecuperacion import PreguntasSeguridadBase
from app.config.database import db
from pymongo.errors import DuplicateKeyError
from app.utils.password_utils import verify_password

class PreguntasSeguridadRepository:
    # Definimos el nombre de la colección como constante de clase
    COLLECTION_NAME = "preguntas_seguridad"

    @staticmethod
    async def create_preguntas(preguntas: PreguntasSeguridadBase) -> Dict:
        preguntas_dict = preguntas.model_dump()
        preguntas_dict["fecha_creacion"] = datetime.utcnow()
            
        await db[PreguntasSeguridadRepository.COLLECTION_NAME].insert_one(preguntas_dict)
            
        return {
            "success": True,
            "message": "Preguntas de seguridad creadas correctamente"
        }


    @staticmethod
    async def update_preguntas(usuario: str, preguntas: PreguntasSeguridadBase) -> Dict:

        preguntas_dict = preguntas.model_dump()
        preguntas_dict["fecha_actualizacion"] = datetime.utcnow()
            
        result = await db[PreguntasSeguridadRepository.COLLECTION_NAME].update_one(
            {"Usuario": usuario},
            {"$set": preguntas_dict}
        )
            
        if result.modified_count == 0:
            return {
                "success": False,
                "message": "No se encontró el usuario o no hubo cambios"
            }
                
        return {
            "success": True,
            "message": "Preguntas de seguridad actualizadas correctamente"
        }


    @staticmethod
    async def get_preguntas_by_user(usuario: str) -> Optional[Dict]:
        preguntas = await db[PreguntasSeguridadRepository.COLLECTION_NAME].find_one(
            {"Usuario": usuario}
        )    
        if preguntas:
            preguntas["_id"] = str(preguntas["_id"])
            return preguntas
        return None


    @staticmethod
    async def verify_respuestas(usuario: str, respuestas: List[str]) -> Dict:
        preguntas = await PreguntasSeguridadRepository.get_preguntas_by_user(usuario)
            
        if not preguntas:
            return {
                "success": False,
                "message": "Usuario no encontrado"
            }
                
        # Verificar cada respuesta hasheada
        stored_answers = preguntas["respuestas"]
        for i, (stored, provided) in enumerate(zip(stored_answers, respuestas)):
            if not verify_password(provided.lower().strip(), stored):
                return {
                    "success": False,
                    "message": "Respuestas incorrectas"
                }
            
        return {
            "success": True,
            "message": "Respuestas correctas"
        }


    @staticmethod
    async def update_usuario_preguntas(usuario_antiguo: str, usuario_nuevo: str) -> Dict:

        result = await db[PreguntasSeguridadRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )

        if result.modified_count == 0:
            return {
                "success": False,
                "message": "No se encontró el usuario o no hubo cambios"
            }

        return {
            "success": True,
            "message": f"Se actualizaron {result.modified_count} documento(s)"
        }
