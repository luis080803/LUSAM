from datetime import date
from pydantic import BaseModel, Field

class ImagenBase(BaseModel):
    Usuario: str = Field(..., min_length=4, max_length=20, description="Nombre de usuario para login")
    codigo_acceso: str = Field(..., min_length=6, max_length=30, description="Código de acceso al stream")
    Fecha: date = Field(default_factory=date.today, description="Fecha de creación")
    Ruta: str = Field(..., max_length=255, description="Ruta del archivo en el servidor")


