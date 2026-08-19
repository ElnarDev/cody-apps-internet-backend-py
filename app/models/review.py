from sqlmodel import Field, SQLModel


class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")


# Modelo principal para la Base de Datos
class Review(ReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ai_analysis: str | None = Field(default=None)  # Análisis de sentimiento generado por IA


# Schema Público para Lectura
class ReviewPublic(ReviewBase):
    id: int
    ai_analysis: str | None = None  # Visible para el admin en la respuesta


# Schema para Crear (el cliente solo envía rating y comment)
class ReviewCreate(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str
