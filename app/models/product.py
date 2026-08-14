from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    price: float
    stock: int = Field(default=0)
    category_id: int = Field(foreign_key="category.id")

# Modelo principal para la Base de Datos
class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Schema Público para Lectura
class ProductPublic(ProductBase):
    id: int

# Schema para Crear
class ProductCreate(ProductBase):
    pass

# Schema para Actualizar (PATCH, campos opcionales)
class ProductUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category_id: int | None = None

