import os
import hmac
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Tuple


def hash_password(plain_text_password: str) -> str:
    """Hashes a password using bcrypt with 12 salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def is_bcrypt_hash(stored_value: str) -> bool:
    """Checks whether a stored string is a valid bcrypt hash format."""
    if not stored_value or not isinstance(stored_value, str):
        return False
    return (
        len(stored_value) == 60
        and (stored_value.startswith("$2a$") or stored_value.startswith("$2b$") or stored_value.startswith("$2y$"))
    )


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password strictly against a bcrypt hash.
    Does NOT allow plaintext comparisons or backdoors.
    """
    if not hashed_password or not plain_text_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_text_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def verify_and_check_upgrade(plain_text_password: str, stored_credential: str) -> Tuple[bool, bool]:
    """
    Safe verification process for both standard bcrypt accounts and legacy pre-hashing accounts.
    Returns:
        (is_valid: bool, needs_upgrade: bool)

    If the credential was stored as legacy plaintext, it is verified via constant-time compare
    and flagged with needs_upgrade=True so the caller can immediately rehash it with bcrypt.
    """
    if not stored_credential or not plain_text_password:
        return False, False

    # 1. Standard bcrypt hash check
    if is_bcrypt_hash(stored_credential):
        valid = verify_password(plain_text_password, stored_credential)
        return valid, False

    # 2. Legacy account fallback: constant-time comparison
    # Only triggered if the database contains a pre-migration legacy password
    is_match = hmac.compare_digest(plain_text_password, stored_credential)
    if is_match:
        return True, True  # Matched legacy, must be upgraded immediately

    return False, False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validates that a new password meets minimum security standards."""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password must not exceed 128 characters."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return False, "Password must contain at least one letter and one number."
    return True, ""


INSECURE_DEFAULT_SECRETS = {
    "neoyatra-production-super-secret-jwt-key-2026",
    "secret",
    "changeme",
    "your-secret-key",
    "jwt_secret",
    "default-secret",
    "admin123",
}


def get_jwt_secret() -> str:
    """
    Validates and retrieves the JWT signing secret.
    In production environments, rejects missing, default, or weak secrets (<32 characters).
    """
    secret = os.getenv("JWT_SECRET")
    env = os.getenv("ENVIRONMENT", "development").strip().lower()
    if env == "production":
        if not secret or secret in INSECURE_DEFAULT_SECRETS or len(secret) < 32:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: In production, JWT_SECRET must be set to a secure, "
                "cryptographically random secret at least 32 characters long."
            )
        return secret
    return secret or "neoyatra-development-secret-key-32-chars-min!!"


def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


def generate_secure_token() -> str:
    """Generates a cryptographically secure URL-safe token for password resets."""
    return secrets.token_urlsafe(32)


def create_access_token(data: dict) -> str:
    """Creates a signed JWT access token with an explicit expiration timestamp."""
    to_encode = data.copy()
    expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", 480))
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        get_jwt_secret(),
        algorithm=get_jwt_algorithm()
    )


def decode_token(token: str) -> dict:
    """Decodes and verifies a JWT token, returning its payload."""
    return jwt.decode(
        token,
        get_jwt_secret(),
        algorithms=[get_jwt_algorithm()]
    )
