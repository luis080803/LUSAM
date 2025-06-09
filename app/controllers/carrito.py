from fastapi import APIRouter, HTTPException
from app.repository.carrito_rep import RegistroCarroRepository
router = APIRouter(prefix="/carros")
from pydantic import BaseModel

class EstadoCarroUpdate(BaseModel):
    matricula: str
    enUso: bool

@router.get("/estado/{matricula}")
async def verificar_estado_carro(matricula: str):
    estado = await RegistroCarroRepository.get_estado_carro_by_matricula(matricula)
    if estado is None:
        raise HTTPException(status_code=404, detail="Carro no encontrado")
    return {"enUso": estado}

@router.post("/actualizar-estado")
async def actualizar_estado_carro(data: EstadoCarroUpdate):
    success = await RegistroCarroRepository.update_estado_carro(data.matricula, data.enUso)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el estado")
    return {"message": "Estado actualizado correctamente"} 