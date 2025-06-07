from datetime import datetime
from typing import List, Optional, Dict
from app.models.preguntasrecuperacion import PreguntasSeguridadBase
from app.config.database import db
from pymongo.errors import DuplicateKeyError

class PreguntasSeguridadRepository:
    # Definimos el nombre de la colección como constante de clase
    COLLECTION_NAME = "preguntas_seguridad"

    @staticmethod
    async def create_preguntas(preguntas: PreguntasSeguridadBase) -> Dict:
        try:
            preguntas_dict = preguntas.dict()
            preguntas_dict["fecha_creacion"] = datetime.utcnow()
            
            await db[PreguntasSeguridadRepository.COLLECTION_NAME].insert_one(preguntas_dict)
            
            return {
                "success": True,
                "message": "Preguntas de seguridad creadas correctamente"
            }
        except DuplicateKeyError:
            return {
                "success": False,
                "message": "El usuario ya tiene preguntas de seguridad registradas"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear preguntas: {str(e)}"
            }

    @staticmethod
    async def update_preguntas(usuario: str, preguntas: PreguntasSeguridadBase) -> Dict:
        try:
            preguntas_dict = preguntas.dict()
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
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar preguntas: {str(e)}"
            }

    @staticmethod
    async def get_preguntas_by_user(usuario: str) -> Optional[Dict]:
        try:
            preguntas = await db[PreguntasSeguridadRepository.COLLECTION_NAME].find_one(
                {"Usuario": usuario}
            )
            
            if preguntas:
                preguntas["_id"] = str(preguntas["_id"])
                return preguntas
            return None
        except Exception as e:
            print(f"Error al obtener preguntas: {str(e)}")
            return None

    @staticmethod
    async def verify_respuestas(usuario: str, respuestas: List[str]) -> Dict:

        try:
            preguntas = await PreguntasSeguridadRepository.get_preguntas_by_user(usuario)
            
            if not preguntas:
                return {
                    "success": False,
                    "message": "Usuario no encontrado"
                }
                
            # Comparamos las respuestas (case insensitive)
            stored_answers = [a.lower().strip() for a in preguntas["respuestas"]]
            provided_answers = [a.lower().strip() for a in respuestas]
            
            if stored_answers == provided_answers:
                return {
                    "success": True,
                    "message": "Respuestas correctas"
                }
            return {
                "success": False,
                "message": "Respuestas incorrectas"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al verificar respuestas: {str(e)}"
            }

