from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    Nombre: str = Field(..., min_length=2, max_length=50, description="Nombre(s) del usuario")
    Password: str = Field(..., min_length=8, max_length=50, description="Contraseña")
    ApellidoPaterno: str = Field(..., min_length=2, max_length=50, description="Apellido paterno")
    ApellidoMaterno: Optional[str] = Field(None, max_length=50, description="Apellido materno (opcional)")
    Correo: EmailStr = Field(..., description="Correo electrónico")
    FechaNacimiento: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    Usuario: str = Field(..., min_length=2, max_length=20, description="Nombre de usuario para login")
    Status: bool = Field(default=True, description="Estado activo/inactivo")
    Fecha_registro: date = Field(default_factory=date.today, description="Fecha de registro automática")

