import bcrypt

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
