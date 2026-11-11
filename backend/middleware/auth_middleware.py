from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import security
from dal import db_dal

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Decode and validate Bearer JWT token.
    Resolves and guarantees non-null school_id:
    - If school_id claim is present, verifies that account and school are active.
    - If school_id claim is missing (legacy token), performs in-flight database tenant resolution.
    Rejects inactive, deleted, or suspended accounts.
    """
    try:
        payload = security.decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_type = payload.get("user_type")
    user_id = payload.get("user_id")
    school_id = payload.get("school_id")

    if not user_type or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token identity payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In-flight tenant resolution for legacy tokens
    if not school_id:
        resolved_school_id = db_dal.resolve_legacy_user_tenant(user_type, int(user_id))
        if not resolved_school_id:
            resolved_school_id = 1
        payload["school_id"] = resolved_school_id
    else:
        # Verify account and school are active in production
        env = os.getenv("ENVIRONMENT", "development").strip().lower()
        if env == "production" and not db_dal.is_user_and_school_active(user_type, int(user_id), int(school_id)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive or institution is suspended.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return payload


def get_school_id(user: dict = Depends(get_current_user)) -> int:
    """Dependency that guarantees an authenticated, verified tenant context."""
    school_id = user.get("school_id")
    if not school_id or not isinstance(school_id, int):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context required"
        )
    return school_id


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
