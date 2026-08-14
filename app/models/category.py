from typing import Optional
from sqlmodel import Field, SQLModel


# Esquema base
class CategoryBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


# Modelo de Base de Datos
class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Esquemas para la API (Pydantic)
class CategoryCreate(CategoryBase):
    pass


class CategoryPublic(CategoryBase):
    id: int


class CategoryUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
