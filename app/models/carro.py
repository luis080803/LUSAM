from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class RegistroCarro(BaseModel):
    Matricula: str = Field(..., min_length=8, max_length=20, description="Matricula del carro")
    Usuario: str = Field(..., min_length=4, max_length=20, description="Nombre de usuario para login")
    EnUso: bool = Field(default=True, description="Si esta en uso o no")
    Notas: Optional[str] = Field(None, max_length=500, description="Observaciones o notas adicionales")
    Año: date = Field(..., description="Año académico (usar el primer día del año)")