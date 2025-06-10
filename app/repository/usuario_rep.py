from datetime import datetime,date
from typing import Optional, List
from app.models.usuario import UsuarioBase
from app.config.database import db
from bson import ObjectId
from app.utils.password_utils import hash_password, verify_password

# repositorio que maneja los usuarios del sistema
class UsuarioRepository:
    COLLECTION_NAME = "usuarios"  # nombre de la colección en mongodb

    @staticmethod
    async def crear_usuario(usuario: UsuarioBase) -> dict:
        usuario_dict = usuario.dict()  # convertimos el modelo a diccionario

        # convertimos las fechas a datetime para mongodb
        for campo in ['FechaNacimiento', 'Fecha_registro']:
            valor = usuario_dict.get(campo)
            if isinstance(valor, date) and not isinstance(valor, datetime):
                usuario_dict[campo] = datetime.combine(valor, datetime.min.time())

        usuario_dict['Password'] = hash_password(usuario_dict['Password'])  # hasheamos la contraseña

        result = await db[UsuarioRepository.COLLECTION_NAME].insert_one(usuario_dict)  # guardamos en la base de datos
        nuevo_usuario = await db[UsuarioRepository.COLLECTION_NAME].find_one(  # obtenemos el usuario creado
            {"_id": result.inserted_id}
        )
        nuevo_usuario["_id"] = str(nuevo_usuario["_id"])  # convertimos el id a string
        return nuevo_usuario

    @staticmethod
    async def actualizar_usuario_por_nombre(nombre_usuario: str, datos_actualizados: dict) -> bool:
        if 'Password' in datos_actualizados:  # si se está actualizando la contraseña
            datos_actualizados['Password'] = hash_password(datos_actualizados['Password'])  # la hasheamos

        result = await db[UsuarioRepository.COLLECTION_NAME].update_one(  # actualizamos en la base de datos
            {"Usuario": nombre_usuario},
            {"$set": datos_actualizados}
        )
        return result.modified_count > 0  # retornamos true si se actualizó

    @staticmethod
    async def obtener_usuario_por_usuario(nombre_usuario: str) -> Optional[dict]:
        usuario = await db[UsuarioRepository.COLLECTION_NAME].find_one(  # buscamos el usuario
            {"Usuario": nombre_usuario}
        )
        if usuario:
            usuario["_id"] = str(usuario["_id"])  # convertimos el id a string
        return usuario

    @staticmethod
    async def obtener_todos_los_usuarios() -> List[dict]:
        usuarios = await db[UsuarioRepository.COLLECTION_NAME].find().to_list(1000)  # obtenemos todos los usuarios
        for usuario in usuarios:
            usuario["_id"] = str(usuario["_id"])  # convertimos los ids a string
        return usuarios

    @staticmethod
    async def eliminar_usuario(usuario_id: str) -> bool:
        result = await db[UsuarioRepository.COLLECTION_NAME].delete_one(  # eliminamos el usuario
            {"_id": ObjectId(usuario_id)}
        )
        return result.deleted_count > 0  # retornamos true si se eliminó

    @staticmethod
    async def verificar_credenciales(nombre_usuario: str, contrasena: str) -> Optional[dict]:
        usuario = await db[UsuarioRepository.COLLECTION_NAME].find_one(  # buscamos el usuario
            {"Usuario": nombre_usuario}
        )
        if usuario and verify_password(contrasena, usuario["Password"]):  # verificamos la contraseña
            usuario["_id"] = str(usuario["_id"])  # convertimos el id a string
            return usuario
        return None
    
    @staticmethod
    async def cambiar_contrasena_plana(nombre_usuario: str, nueva_contrasena: str) -> bool:
        hashed_password = hash_password(nueva_contrasena)  # hasheamos la nueva contraseña
        result = await db[UsuarioRepository.COLLECTION_NAME].update_one(  # actualizamos en la base de datos
            {"Usuario": nombre_usuario},
            {"$set": {"Password": hashed_password}}
        )
        return True  # retornamos true si se actualizó