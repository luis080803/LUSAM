from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# modelo base para los usuarios del sistema
class UsuarioBase(BaseModel):
    # nombre o nombres de la persona
    Nombre: str = Field(..., min_length=2, max_length=50, description="Nombre(s) del usuario")
    # contraseña de acceso al sistema
    Password: str = Field(..., min_length=8, max_length=50, description="Contraseña")
    # apellido paterno del usuario
    ApellidoPaterno: str = Field(..., min_length=2, max_length=50, description="Apellido paterno")
    # apellido materno, es opcional
    ApellidoMaterno: Optional[str] = Field(None, max_length=50, description="Apellido materno (opcional)")
    # correo electrónico válido del usuario
    Correo: EmailStr = Field(..., description="Correo electrónico")
    # fecha de nacimiento en formato año-mes-día
    FechaNacimiento: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    # nombre de usuario para iniciar sesión
    Usuario: str = Field(..., min_length=2, max_length=20, description="Nombre de usuario para login")
    # indica si la cuenta está activa o no
    Status: bool = Field(default=True, description="Estado activo/inactivo")
    # fecha en que se registró el usuario, se genera automáticamente
    Fecha_registro: date = Field(default_factory=date.today, description="Fecha de registro automática")

