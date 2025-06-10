from pydantic import BaseModel, Field, validator
from typing import List
from app.utils.password_utils import hash_password

class PreguntasSeguridadBase(BaseModel):
    Usuario: str = Field(..., min_length=4, max_length=20, description="Usuario")
    preguntas: List[str] = Field(..., min_items=2, max_items=2, description="Lista de 2 preguntas de seguridad")
    respuestas: List[str] = Field(..., min_items=2, max_items=2, description="Lista de 2 respuestas correspondientes")

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Hashear las respuestas antes de guardar
        data['respuestas'] = [hash_password(resp) for resp in data['respuestas']]
        return data
