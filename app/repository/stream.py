from datetime import datetime, date
from typing import Optional, List
from app.models.stream import StreamBase
from app.config.database import db
from bson import ObjectId


class StreamRepository:
    COLLECTION_NAME = "streams"

    @staticmethod
    async def crear_stream(
        usuario: str,
        titulo: str,
        matricula: str = "UVCARRITO"
    ) -> dict:
        stream_data = {
            "Usuario": usuario,
            "Matricula": matricula,
            "titulo": titulo,
            "inicio": datetime.now(),
            "fin": None,
            "activo": True 
        }

        result = await db[StreamRepository.COLLECTION_NAME].insert_one(stream_data)
        nuevo_stream = await db[StreamRepository.COLLECTION_NAME].find_one(
            {"_id": result.inserted_id}
        )
        nuevo_stream["_id"] = str(nuevo_stream["_id"])
        return nuevo_stream

    @staticmethod
    async def actualizar_fin_stream(stream_id: str) -> bool:
        result = await db[StreamRepository.COLLECTION_NAME].update_one(
            {"_id": ObjectId(stream_id)},
            {"$set": {
                "fin": datetime.now(),
                "activo": False  
            }}
        )
        return result.modified_count > 0

    @staticmethod
    async def obtener_stream_por_id(stream_id: str) -> Optional[dict]:
        stream = await db[StreamRepository.COLLECTION_NAME].find_one(
            {"_id": ObjectId(stream_id)}
        )
        if stream:
            stream["_id"] = str(stream["_id"])
        return stream

    @staticmethod
    async def obtener_streams_por_usuario(usuario: str) -> List[dict]:
        streams = await db[StreamRepository.COLLECTION_NAME].find(
            {"Usuario": usuario}
        ).to_list(1000)
        for stream in streams:
            stream["_id"] = str(stream["_id"])
        return streams

    @staticmethod
    async def obtener_todos_los_streams() -> List[dict]:
        streams = await db[StreamRepository.COLLECTION_NAME].find().to_list(1000)
        for stream in streams:
            stream["_id"] = str(stream["_id"])
        return streams

    @staticmethod
    async def eliminar_stream(stream_id: str) -> bool:
        result = await db[StreamRepository.COLLECTION_NAME].delete_one(
            {"_id": ObjectId(stream_id)}
        )
        return result.deleted_count > 0
        
    @staticmethod
    async def obtener_stream_activo_por_id(stream_id: str):
        return await db[StreamRepository.COLLECTION_NAME].find_one({
            "_id": ObjectId(stream_id),
            "activo": True
        })
    
    @staticmethod
    async def update_usuario_stream(usuario_antiguo: str, usuario_nuevo: str) -> dict:

        result = await db[StreamRepository.COLLECTION_NAME].update_many(
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