from datetime import date
from typing import List, Optional
from app.models.carro import RegistroCarro
from app.config.database import db
from bson import ObjectId

class RegistroCarroRepository:
    # Definimos el nombre de la colección como constante de clase
    COLLECTION_NAME = "carros"

    @staticmethod
    async def get_carros_by_user(usuario: str) -> List[dict]:
        carros = await db[RegistroCarroRepository.COLLECTION_NAME].find(
            {"Usuario": usuario}
        ).to_list(1000)
        for carro in carros:
            carro["_id"] = str(carro["_id"])
        return carros

    @staticmethod
    async def create_carro(carro: RegistroCarro) -> dict:
        carro_dict = carro.dict()
        # Convertir la fecha a datetime (si es necesario para MongoDB)
        carro_dict["Año"] = carro_dict["Año"].isoformat()  # o puedes usar datetime.combine como en el ejemplo
        result = await db[RegistroCarroRepository.COLLECTION_NAME].insert_one(carro_dict)
        new_carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"_id": result.inserted_id}
        )
        new_carro["_id"] = str(new_carro["_id"])
        return new_carro

    @staticmethod
    async def delete_carro(carro_id: str) -> bool:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].delete_one(
            {"_id": ObjectId(carro_id)}
        )
        return result.deleted_count > 0
    
    @staticmethod
    async def update_carro_usuario(usuario_antiguo: str, usuario_nuevo: str) -> int:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_antiguo},
            {"$set": {"Usuario": usuario_nuevo}}
        )
        return result.modified_count

    @staticmethod
    async def get_carro_by_id(carro_id: str) -> Optional[dict]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"_id": ObjectId(carro_id)}
        )
        if carro:
            carro["_id"] = str(carro["_id"])
        return carro

    @staticmethod
    async def update_estado_carro(matricula: str, en_uso: bool) -> bool:
        await db[RegistroCarroRepository.COLLECTION_NAME].update_one(
            {"Matricula": matricula},
            {"$set": {"EnUso": en_uso}}
        )
        return True

    @staticmethod
    async def get_carro_by_matricula(matricula: str) -> Optional[dict]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Matricula": matricula}
        )
        if carro:
            carro["_id"] = str(carro["_id"])
        return carro

    @staticmethod
    async def update_notas_carro(matricula: str, notas: str) -> bool:
        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_one(
            {"Matricula": matricula},
            {"$set": {"Notas": notas}}
        )
        return result.modified_count > 0

    @staticmethod
    async def get_estado_carro_by_matricula(matricula: str) -> Optional[bool]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Matricula": matricula},
            {"_id": 0, "EnUso": 1}  # Solo devolvemos el campo EnUso, excluimos el _id
        )
        return carro.get("EnUso") if carro else None
    
    @staticmethod
    async def get_matricula_by_usuario(usuario: str) -> Optional[str]:
        carro = await db[RegistroCarroRepository.COLLECTION_NAME].find_one(
            {"Usuario": usuario},
            {"_id": 0, "Matricula": 1}  # Solo proyectamos la matrícula
        )
        return carro.get("Matricula") if carro else None
    
    @staticmethod
    async def update_usuario_carro(usuario_actual: str, usuario_nuevo: str) -> int:

        result = await db[RegistroCarroRepository.COLLECTION_NAME].update_many(
            {"Usuario": usuario_actual},  # Busca TODOS los carros del usuario actual
            {"$set": {"Usuario": usuario_nuevo}}  # Actualiza a nuevo usuario
        )
        return result.modified_count