from typing import Dict
from app.config.database import db


class EstadisticasRepository:
    @staticmethod
    async def contar_fotos_por_usuario(usuario: str) -> int:
        total = await db["imagenes"].count_documents({"Usuario": usuario})
        return total

    @staticmethod
    async def contar_obstaculos_por_usuario(usuario: str) -> int:
        total = await db["distancias"].count_documents({"Usuario": usuario})
        return total

    @staticmethod
    async def obtener_estadisticas(usuario: str) -> Dict[str, int]:
        fotos = await EstadisticasRepository.contar_fotos_por_usuario(usuario)
        obstaculos = await EstadisticasRepository.contar_obstaculos_por_usuario(usuario)
        return {
            "fotos": fotos,
            "obstaculos": obstaculos
        }
