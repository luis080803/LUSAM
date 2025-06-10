from datetime import datetime, date
from typing import Optional, List
from app.models.stream import StreamBase
from app.config.database import db
from bson import ObjectId

# repositorio que maneja los streams de video
class StreamRepository:
    COLLECTION_NAME = "streams"  # nombre de la colección en mongodb

    @staticmethod
    async def crear_stream(
        usuario: str,
        titulo: str,
        matricula: str = "UVCARRITO"
    ) -> dict:
        stream_data = {  # preparamos los datos del nuevo stream
            "Usuario": usuario,
            "Matricula": matricula,
            "titulo": titulo,
            "inicio": datetime.now(),  # registramos la hora de inicio
            "fin": None,  # el fin será null hasta que se termine
            "activo": True  # marcamos como activo al crear
        }

        result = await db[StreamRepository.COLLECTION_NAME].insert_one(stream_data)  # guardamos en la base de datos
        nuevo_stream = await db[StreamRepository.COLLECTION_NAME].find_one(  # obtenemos el stream creado
            {"_id": result.inserted_id}
        )
        nuevo_stream["_id"] = str(nuevo_stream["_id"])  # convertimos el id a string
        return nuevo_stream

    @staticmethod
    async def actualizar_fin_stream(stream_id: str) -> bool:
        result = await db[StreamRepository.COLLECTION_NAME].update_one(  # actualizamos el stream
            {"_id": ObjectId(stream_id)},
            {"$set": {
                "fin": datetime.now(),  # registramos la hora de fin
                "activo": False  # marcamos como inactivo
            }}
        )
        return result.modified_count > 0  # retornamos true si se actualizó

    @staticmethod
    async def obtener_stream_por_id(stream_id: str) -> Optional[dict]:
        stream = await db[StreamRepository.COLLECTION_NAME].find_one(  # buscamos el stream por id
            {"_id": ObjectId(stream_id)}
        )
        if stream:
            stream["_id"] = str(stream["_id"])  # convertimos el id a string
        return stream

    @staticmethod
    async def obtener_streams_por_usuario(usuario: str) -> List[dict]:
        streams = await db[StreamRepository.COLLECTION_NAME].find(  # buscamos todos los streams del usuario
            {"Usuario": usuario}
        ).to_list(1000)
        for stream in streams:
            stream["_id"] = str(stream["_id"])  # convertimos los ids a string
        return streams

    @staticmethod
    async def obtener_todos_los_streams() -> List[dict]:
        streams = await db[StreamRepository.COLLECTION_NAME].find().to_list(1000)  # obtenemos todos los streams
        for stream in streams:
            stream["_id"] = str(stream["_id"])  # convertimos los ids a string
        return streams

    @staticmethod
    async def eliminar_stream(stream_id: str) -> bool:
        result = await db[StreamRepository.COLLECTION_NAME].delete_one(  # eliminamos el stream
            {"_id": ObjectId(stream_id)}
        )
        return result.deleted_count > 0  # retornamos true si se eliminó
        
    @staticmethod
    async def obtener_stream_activo_por_id(stream_id: str):
        return await db[StreamRepository.COLLECTION_NAME].find_one({  # buscamos un stream activo por id
            "_id": ObjectId(stream_id),
            "activo": True  # solo streams activos
        })
    
    @staticmethod
    async def update_usuario_stream(usuario_antiguo: str, usuario_nuevo: str) -> dict:
        result = await db[StreamRepository.COLLECTION_NAME].update_many(  # actualizamos todos los streams del usuario
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
            "message": f"Se actualizaron {result.modified_count} documento(s)"  # retornamos cuántos se actualizaron
        }