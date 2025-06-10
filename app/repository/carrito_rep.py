from datetime import date
from typing import List, Optional
from app.models.carro import RegistroCarro
from app.config.database import db
from bson import ObjectId

# repositorio que maneja todas las operaciones de la base de datos relacionadas con los carros
# incluye crear, leer, actualizar y eliminar registros de carros
class RegistroCarroRepository:
    # nombre de la colección en mongodb donde se almacenan los registros de carros
    COLLECTION_NAME = "carros"

    # obtiene todos los carros asociados a un usuario específico
    # retorna una lista de diccionarios con la información de cada carro
    # incluye la conversión del id de mongodb a string para mejor manejo
    @staticmethod
    async def get_carros_by_user(usuario: str) -> List[dict]:
        carros = await db[RegistroCarroRepository.COLLECTION_NAME].find(
            {"Usuario": usuario}
        ).to_list(1000)
        for carro in carros:
            carro["_id"] = str(carro["_id"])
        return carros

    # crea un nuevo registro de carro en la base de datos
    # convierte el modelo pydantic a diccionario y formatea la fecha
    # retorna el carro creado con su id convertido a string
    @staticmethod
    async def create_carro(carro: RegistroCarro) -> dict:
        carro_dict = carro.dict()
        # convertimos la fecha a formato iso para que mongodb pueda manejarla correctamente
        carro_dict["Año"] = carro_dict["Año"].isoformat()
        result = await db[RegistroCarroRepository.COLLECTION_NAME].insert_one(carro_dict)
        new_carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"_id": result.inserted_id}
        )
        new_carro["_id"] = str(new_carro["_id"])
        return new_carro

    # elimina un carro específico de la base de datos usando su id
    # retorna true si se eliminó correctamente, false si no se encontró
    @staticmethod
    async def delete_carro(carro_id: str) -> bool:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].delete_one(
            {"_id": ObjectId(carro_id)}
        )
        return result.deleted_count > 0
    
    # actualiza el usuario asociado a uno o varios carros
    # lo ocupamos cuando se necesita cambiar el propietario de los carros
    # retorna la cantidad de documentos actualizados
    @staticmethod
    async def update_carro_usuario(usuario_antiguo: str, usuario_nuevo: str) -> int:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )
        return result.modified_count

    # busca y retorna un carro específico usando su id
    # retorna none si no se encuentra el carro
    # convierte el id de mongodb a string para mejor manejo
    @staticmethod
    async def get_carro_by_id(carro_id: str) -> Optional[dict]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"_id": ObjectId(carro_id)}
        )
        if carro:
            carro["_id"] = str(carro["_id"])
        return carro

    # actualiza el estado de uso de un carro específico
    # en_uso: true si el carro está en uso, false si está disponible
    # retorna true si la actualización fue exitosa
    @staticmethod
    async def update_estado_carro(matricula: str, en_uso: bool) -> bool:
        await db[RegistroCarroRepository.COLLECTION_NAME].update_one(
            {"Matricula": matricula},
            {"$set": {"EnUso": en_uso}}
        )
        return True

    # busca un carro específico usando su matrícula
    # retorna none si no se encuentra el carro
    # convierte el id de mongodb a string para mejor manejo
    @staticmethod
    async def get_carro_by_matricula(matricula: str) -> Optional[dict]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Matricula": matricula}
        )
        if carro:
            carro["_id"] = str(carro["_id"])
        return carro

    # actualiza las notas o comentarios de un carro específico
    # retorna true si se actualizó correctamente, false si no se encontró el carro
    @staticmethod
    async def update_notas_carro(matricula: str, notas: str) -> bool:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_one(
            {"Matricula": matricula},
            {"$set": {"Notas": notas}}
        )
        return result.modified_count > 0

    # obtiene solo el estado de uso de un carro usando su matrícula
    # retorna none si no se encuentra el carro
    # solo proyecta el campo en uso para optimizar la consulta
    @staticmethod
    async def get_estado_carro_by_matricula(matricula: str) -> Optional[bool]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Matricula": matricula},
            {"_id": 0, "EnUso": 1}  # solo devolvemos el campo en uso para optimizar
        )
        return carro.get("EnUso") if carro else None
    
    # obtiene la matrícula de un carro usando el nombre de usuario
    # retorna none si el usuario no tiene carros asignados
    # solo proyecta la matrícula para optimizar la consulta
    @staticmethod
    async def get_matricula_by_usuario(usuario: str) -> Optional[str]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Usuario": usuario},
            {"_id": 0, "Matricula": 1}  # solo proyectamos la matrícula para optimizar
        )
        return carro.get("Matricula") if carro else None
    
    # actualiza el usuario de todos los carros asociados a un usuario específico
    # lo ocupamos cuando se necesita cambiar el propietario de múltiples carros
    # retorna la cantidad de documentos actualizados
    @staticmethod
    async def update_usuario_carro(usuario_actual: str, usuario_nuevo: str) -> int:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_actual},  # busca todos los carros del usuario actual
            {"$set": {"Usuario": usuario_nuevo}}  # actualiza a nuevo usuario
        )
        return result.modified_count