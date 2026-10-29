from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os

# Ensure the backend directory is on the path so `security` can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import security

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Decode and validate the Bearer JWT token, returning the payload."""
    try:
        payload = security.decode_token(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires the caller to be an admin."""
    if user.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def require_parent(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires the caller to be a parent."""
    if user.get("user_type") != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent access required"
        )
    return user


def require_driver(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires the caller to be a driver."""
    if user.get("user_type") != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver access required"
        )
    return user
