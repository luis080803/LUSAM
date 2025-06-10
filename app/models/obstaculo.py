from datetime import date
from pydantic import BaseModel, Field

# modelo base para registrar las distancias de los obstáculos
class RegistroDistanciaBase(BaseModel):
    # código de acceso para ver el stream del obstáculo
    codigo_acceso: str = Field(..., min_length=6, max_length=12, description="Código de acceso al stream")
    # distancia medida en kilómetros, debe estar entre 0 y 1000
    Distancia: float = Field(..., gt=0, le=1000, description="Distancia en kilómetros (0-1000 km)")
    # fecha en que se registró la medición
    Fecha: date = Field(..., description="Fecha del registro (YYYY-MM-DD)")