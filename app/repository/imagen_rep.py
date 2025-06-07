from datetime import datetime
from typing import List, Optional
from app.models.imagenes import ImagenBase
from app.config.database import db
from bson import ObjectId

class ImagenRepository:
    # Definimos el nombre de la colección como constante de clase
    COLLECTION_NAME = "capturas"

    @staticmethod
    async def get_images_by_user(usuario: str) -> List[dict]:
        imagenes = await db[ImagenRepository.COLLECTION_NAME].find(
            {"Usuario": usuario}
        ).to_list(1000)
        for imagen in imagenes:
            imagen["_id"] = str(imagen["_id"])
        return imagenes

    @staticmethod
    async def create_image(imagen: ImagenBase) -> dict:
        imagen_dict = imagen.dict()
        imagen_dict["Fecha"] = datetime.combine(imagen.Fecha, datetime.min.time())
        result = await db[ImagenRepository.COLLECTION_NAME].insert_one(imagen_dict)
        new_image = await db[ImagenRepository.COLLECTION_NAME].find_one(
            {"_id": result.inserted_id}
        )
        new_image["_id"] = str(new_image["_id"])
        return new_image

    @staticmethod
    async def delete_image(image_id: str) -> bool:
        result = await db[ImagenRepository.COLLECTION_NAME].delete_one(
            {"_id": ObjectId(image_id)}
        )
        return result.deleted_count > 0
    
    @staticmethod
    async def update_usuario_imagen(usuario_antiguo: str, usuario_nuevo: str) -> int:
        result = await db[ImagenRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )
        return result.modified_count
    