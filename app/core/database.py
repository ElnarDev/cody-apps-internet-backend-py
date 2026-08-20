from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# 1. Creamos el Motor (Engine) apuntando a la URL configurada (.env)
# connect_args={"check_same_thread": False} es necesario SOLO para SQLite
engine = create_engine(
    settings.DATABASE_URL, 
    # En producción conviene desactivar para reducir latencia y ruido en logs.
    echo=settings.SQL_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 2. Función para inicializar las tablas vacías si no existen
def create_db_and_tables():
    # Detecta todos los modelos clase heredados de SQLModel e invoca un CREATE TABLE interno
    SQLModel.metadata.create_all(engine)

# 3. Generador de Sesiones (Para ser inyectado por `Depends` en FastAPI)
def get_session():
    with Session(engine) as session:
        yield session
