from datetime import date
from pydantic import BaseModel, Field

class RegistroDistanciaBase(BaseModel):
    codigo_acceso: str = Field(..., min_length=6, max_length=12, description="Código de acceso al stream")
    Distancia: float = Field(..., gt=0, le=1000, description="Distancia en kilómetros (0-1000 km)")
    Fecha: date = Field(..., description="Fecha del registro (YYYY-MM-DD)")