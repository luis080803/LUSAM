from pydantic import BaseModel, Field, validator
from typing import List

class PreguntasSeguridadBase(BaseModel):
    Usuario: str = Field(..., min_length=4, max_length=20, description="Usuario")
    preguntas: List[str] = Field(..., min_items=2, max_items=2, description="Lista de 3 preguntas de seguridad")
    respuestas: List[str] = Field(..., min_items=2, max_items=2, description="Lista de 3 respuestas correspondientes")
