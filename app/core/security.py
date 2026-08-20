from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con la firma hasheada."""
    # bcrypt usa bytes y tiene un límite de 72 bytes
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    """Transforma una cadena plana en un hash seguro e irreversible."""
    password_bytes = password.encode('utf-8')[:72]
    # Ajustable por entorno para balancear seguridad y performance.
    rounds = max(4, min(settings.BCRYPT_ROUNDS, 16))
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

# 2. Configuración JWT (JSON Web Tokens)
ALGORITHM = "HS256"

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """
    Crea un pasaporte firmado. 
    'subject' (el sub en JWT) suele ser el ID o Username del usuario que se loggea.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Tiempo por defecto del .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Firmar el payload usando el Secret estricto del servidor
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
