from typing import Optional
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

# Modelo principal para la Base de Datos
class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ai_suggestion: Optional[str] = Field(default=None)
    
# Schema Público para Lectura
class TaskPublic(TaskBase):
    id: int
    ai_suggestion: Optional[str] = None

# Schema para Crear
class TaskCreate(TaskBase):
    pass

# Schema para Actualizar (PATCH, campos opcionales)
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Schema para el endpoint de IA
class TaskAiRequest(SQLModel):
    prompt: str
