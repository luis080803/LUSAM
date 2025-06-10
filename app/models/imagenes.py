from datetime import date
from pydantic import BaseModel, Field

# modelo base para las imágenes del sistema
class ImagenBase(BaseModel):
    # nombre de usuario que subió la imagen
    Usuario: str = Field(..., min_length=4, max_length=20, description="Nombre de usuario para login")
    # código de acceso para ver el stream de la imagen
    codigo_acceso: str = Field(..., min_length=6, max_length=30, description="Código de acceso al stream")
    # fecha en que se subió la imagen, por defecto es hoy
    Fecha: date = Field(default_factory=date.today, description="Fecha de creación")
    # ubicación del archivo en el servidor
    Ruta: str = Field(..., max_length=255, description="Ruta del archivo en el servidor")


