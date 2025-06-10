from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

# modelo para registrar los carros en el sistema
class RegistroCarro(BaseModel):
    # matricula del carro, debe tener entre 8 y 20 caracteres
    Matricula: str = Field(..., min_length=8, max_length=20, description="Matricula del carro")
    # nombre de usuario que tiene asignado el carro
    Usuario: str = Field(..., min_length=4, max_length=20, description="Nombre de usuario para login")
    # indica si el carro está actualmente en uso
    EnUso: bool = Field(default=True, description="Si esta en uso o no")
    # notas adicionales sobre el carro, opcional
    Notas: Optional[str] = Field(None, max_length=500, description="Observaciones o notas adicionales")
    # año académico del registro, se usa el primer día del año
    Año: date = Field(..., description="Año académico (usar el primer día del año)")