from datetime import datetime
from typing import List, Optional
from app.models.imagenes import ImagenBase
from app.config.database import db
from bson import ObjectId

# repositorio que maneja todas las operaciones de la base de datos 
# relacionadas con las imágenes
class ImagenRepository:
    # nombre de la colección en mongodb donde se almacenan las imágenes
    COLLECTION_NAME = "capturas"

    # obtiene todas las imágenes asociadas a un usuario específico
    @staticmethod
    async def get_images_by_user(usuario: str) -> List[dict]:
        imagenes = await db[ImagenRepository.COLLECTION_NAME].find(
            {"Usuario": usuario}
        ).to_list(1000)
        for imagen in imagenes:
            imagen["_id"] = str(imagen["_id"])
        return imagenes

    # crea un nuevo registro de imagen en la base de datos
    # combina la fecha con la hora mínima para almacenamiento consistente
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

    # elimina una imagen específica de la base de datos usando su id
    @staticmethod
    async def delete_image(image_id: str) -> bool:
        result = await db[ImagenRepository.COLLECTION_NAME].delete_one(
            {"_id": ObjectId(image_id)}
        )
        return result.deleted_count > 0
    
    # actualiza el usuario asociado a una o varias imágenes
    # lo ocupamos cuando se necesita cambiar el propietario de las imágenes
    @staticmethod
    async def update_usuario_imagen(usuario_antiguo: str, usuario_nuevo: str) -> int:
        result = await db[ImagenRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )
        return result.modified_count

    # busca y retorna una imagen específica usando su id
    @staticmethod
    async def get_image_by_id(image_id: str) -> Optional[dict]:
        imagen = await db[ImagenRepository.COLLECTION_NAME].find_one(
            {"_id": ObjectId(image_id)}
        )
        if imagen:
            imagen["_id"] = str(imagen["_id"])
        return imagen
    