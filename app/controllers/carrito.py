from fastapi import APIRouter, HTTPException
from app.repository.carrito_rep import RegistroCarroRepository # importamos nuestro repositorio que maneja la información de los carros

# el router se encarga de manejar las rutas de la página 
router = APIRouter(prefix="/carros")
from pydantic import BaseModel

# esta clase nos ayuda a validar los datos que recibimos para actualizar el estado del carrito
class EstadoCarroUpdate(BaseModel):
    matricula: str
    enUso: bool

# esta ruta se encarga de verificar el estado del carro
@router.get("/estado/{matricula}")
async def verificar_estado_carro(matricula: str):
    # buscamos el estado del carro usando su matrícula
    estado = await RegistroCarroRepository.get_estado_carro_by_matricula(matricula)
    # si no encontramos el carro, avisamos al usuario
    if estado is None:
        raise HTTPException(status_code=404, detail="Carro no encontrado")
    return {"enUso": estado}

# esta ruta se encarga de actualizar el estado del carro mediante un post de la matricula y el estado
@router.post("/actualizar-estado")
async def actualizar_estado_carro(data: EstadoCarroUpdate):
    # intentamos actualizar el estado del carro
    success = await RegistroCarroRepository.update_estado_carro(data.matricula, data.enUso)
    # si algo salió mal, le avisamos al usuario
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el estado")
    return {"message": "Estado actualizado correctamente"}  # si todo salió bien, le avisa al usuario