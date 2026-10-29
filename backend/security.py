import bcrypt
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta


def hash_password(plain_text_password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a hashed password."""
    try:
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    """Creates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", 480)))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        os.getenv("JWT_SECRET", "secret"),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )


def decode_token(token: str) -> dict:
    """Decodes and verifies a JWT token, returning its payload."""
    return jwt.decode(
        token,
        os.getenv("JWT_SECRET", "secret"),
        algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
    )
