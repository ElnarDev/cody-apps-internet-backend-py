from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Meta
    PROJECT_NAME: str = "Taller - API Enterprise"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad (JWT)
    SECRET_KEY: str = "CAMBIAR_ESTO_EN_PRODUCCION_O_ME_DESPIDEN_123!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 Días para comodidad de los alumnos
    
    # Base de Datos
    DATABASE_URL: str = "sqlite:///./fastapi.db"
    SQL_ECHO: bool = False

    # Seguridad de hashing (bcrypt). Menor valor = más rápido, menor costo criptográfico.
    BCRYPT_ROUNDS: int = 12

    # CORS (lista separada por comas). En producción agrega el dominio de Vercel.
    BACKEND_CORS_ORIGINS: str = (
        "http://localhost:4200,"
        "http://127.0.0.1:4200,"
        "http://localhost:8080,"
        "http://127.0.0.1:8080"
    )
    
    # Inteligencia Artificial
    GEMINI_API_KEY: str | None = None
    
    # Esta línea mágica le dice a Pydantic que lea automáticamente el archivo .env si existe
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte BACKEND_CORS_ORIGINS (CSV) a lista limpia para FastAPI."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

# Instanciamos la clase para importar `settings` en cualquier parte de la app
settings = Settings()
