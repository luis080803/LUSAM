from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# modelo base para los streams del sistema
class StreamBase(BaseModel):
    # nombre de usuario que maneja el stream
    Usuario: str = Field(..., min_length=4, max_length=20, description="Persona que lo maneja")
    # matrícula del carro asociado al stream
    Matricula: str = Field(..., min_length=8, max_length=20, description="Carro del stream")
    # título descriptivo del stream
    titulo: str = Field(..., min_length=5, max_length=100, description="Título del stream")
    # momento exacto en que comenzó el stream
    inicio: datetime = Field(..., description="Fecha y hora de inicio del stream")
    # momento en que terminó el stream, puede ser nulo si aún está activo
    fin: Optional[datetime] = Field(None, description="Fecha y hora de finalización del stream")
    # indica si el stream está actualmente en transmisión
    activo: bool = Field(True, description="Indica si el stream está activo o no")