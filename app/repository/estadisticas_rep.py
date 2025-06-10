from typing import Dict
from app.config.database import db

# repositorio que maneja las estadísticas de los usuarios
# incluye conteos de fotos y obstáculos registrados
class EstadisticasRepository:
    # cuenta el total de fotos subidas por un usuario específico
    # busca en la colección 'imagenes' y retorna el número total
    @staticmethod
    async def contar_fotos_por_usuario(usuario: str) -> int:
        total = await db["imagenes"].count_documents({"Usuario": usuario})
        return total

    # cuenta el total de obstáculos registrados por un usuario específico
    # busca en la colección 'distancias' y retorna el número total
    @staticmethod
    async def contar_obstaculos_por_usuario(usuario: str) -> int:
        total = await db["distancias"].count_documents({"Usuario": usuario})
        return total

    # obtiene todas las estadísticas de un usuario en un solo diccionario
    # incluye el conteo de fotos y obstáculos
    # lo ocupamos para mostrar el resumen de actividad del usuario
    @staticmethod
    async def obtener_estadisticas(usuario: str) -> Dict[str, int]:
        fotos = await EstadisticasRepository.contar_fotos_por_usuario(usuario)
        obstaculos = await EstadisticasRepository.contar_obstaculos_por_usuario(usuario)
        return {
            "fotos": fotos,
            "obstaculos": obstaculos
        }
