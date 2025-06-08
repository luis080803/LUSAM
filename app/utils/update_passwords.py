import asyncio
from app.config.database import db
from app.utils.password_utils import hash_password

async def update_existing_passwords():
    """
    Actualiza todas las contraseñas existentes en la base de datos a formato hasheado.
    Este script debe ejecutarse una sola vez después de implementar el sistema de hash.
    """
    # Obtener todos los usuarios
    usuarios = await db["usuarios"].find().to_list(None)
    
    # Contador para seguimiento
    actualizados = 0
    errores = 0
    
    for usuario in usuarios:
        try:
            # Verificar si la contraseña ya está hasheada
            password = usuario.get("Password", "")
            if not password.startswith("$2b$"):  # Los hashes de bcrypt empiezan con $2b$
                # Hashear la contraseña existente
                hashed_password = hash_password(password)
                
                # Actualizar en la base de datos
                await db["usuarios"].update_one(
                    {"_id": usuario["_id"]},
                    {"$set": {"Password": hashed_password}}
                )
                actualizados += 1
                print(f"Contraseña actualizada para usuario: {usuario.get('Usuario', 'Desconocido')}")
        except Exception as e:
            errores += 1
            print(f"Error al actualizar usuario {usuario.get('Usuario', 'Desconocido')}: {str(e)}")
    
    print(f"\nResumen:")
    print(f"Contraseñas actualizadas: {actualizados}")
    print(f"Errores: {errores}")

if __name__ == "__main__":
    asyncio.run(update_existing_passwords()) 