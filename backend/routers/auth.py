import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Optional, Literal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import security
from dal import db_dal
from middleware.auth_middleware import get_current_user, require_admin
from middleware.rate_limiter import check_rate_limit, record_failed_login, clear_rate_limit, check_account_lockout

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str
    school_code: Optional[str] = None
    user_type: Optional[Literal["admin", "parent", "driver"]] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int
    name: str
    school_id: Optional[int] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminResetPasswordRequest(BaseModel):
    user_type: Literal["admin", "parent", "driver"]
    user_id: int
    new_password: str


class ForgotPasswordRequest(BaseModel):
    username: str
    user_type: Optional[Literal["admin", "parent", "driver"]] = None


class ResetPasswordWithTokenRequest(BaseModel):
    username: str
    user_type: Literal["admin", "parent", "driver"]
    reset_token: str
    new_password: str


def _fetch_user(fetch_func, username: str, school_id: Optional[int]):
    try:
        return fetch_func(username, school_id=school_id)
    except TypeError:
        return fetch_func(username)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request):
    """
    Authenticate a user (admin, parent, or driver) and return a signed JWT access token.
    Uses strict bcrypt verification with transparent rehashing for any legacy unhashed accounts.
    Includes brute-force rate limiting and account lockout protection.
    """
    client_ip = request.client.host if request.client and request.client.host else "127.0.0.1"
    username = body.username.strip()
    password = body.password.strip()

    # 1. Check IP-level rate limiting
    check_rate_limit(f"ip_req:{client_ip}", max_requests=60, window_seconds=60, block_duration_seconds=120)

    # 2. Check failed attempt lockout for this IP and username
    lockout_id = f"{client_ip}:{username}"
    check_account_lockout(lockout_id)

    if not username or not password:
        record_failed_login(lockout_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    # 3. Resolve Tenant Institution
    env = os.getenv("ENVIRONMENT", "development").strip().lower()
    code = (body.school_code or "").strip()
    if not code:
        if env == "production":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="school_code is required in production environment."
            )
        code = "DEFAULT"

    school = db_dal.get_school_by_code(code)
    if not school or not school[3]:  # is_active
        record_failed_login(lockout_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid institution code or institution account is inactive."
        )
    school_id = school[0]

    req_role = body.user_type

    # 4. Try admin (if role is admin or unspecified)
    if req_role in (None, "admin"):
        admin_row = _fetch_user(db_dal.get_admin_by_username, username, school_id)
        if admin_row:
            # admin_row: (admin_id, USERNAME, password, full_name, ...)
            admin_id, admin_user, stored_cred, full_name = admin_row[0], admin_row[1], admin_row[2], admin_row[3]
            is_valid, needs_upgrade = security.verify_and_check_upgrade(password, stored_cred)
            if is_valid:
                clear_rate_limit(lockout_id)
                if needs_upgrade:
                    new_hash = security.hash_password(password)
                    db_dal.set_admin_password_hash(admin_id, new_hash)

                token = security.create_access_token({
                    "user_id": admin_id,
                    "user_type": "admin",
                    "username": admin_user,
                    "school_id": school_id,
                })
                return LoginResponse(
                    access_token=token,
                    token_type="bearer",
                    user_type="admin",
                    user_id=admin_id,
                    name=full_name,
                    school_id=school_id,
                )
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        elif req_role == "admin":
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    # 5. Try parent (if role is parent or unspecified)
    if req_role in (None, "parent"):
        parent_row = _fetch_user(db_dal.get_parent_by_username, username, school_id)
        if parent_row:
            # parent_row: (parent_id, parent_name, phone, address, pickup_point, username, password, ...)
            p_id, p_name, _, _, _, p_user, stored_cred = (
                parent_row[0], parent_row[1], parent_row[2], parent_row[3], parent_row[4], parent_row[5], parent_row[6]
            )
            is_valid, needs_upgrade = security.verify_and_check_upgrade(password, stored_cred)
            if is_valid:
                clear_rate_limit(lockout_id)
                if needs_upgrade:
                    new_hash = security.hash_password(password)
                    db_dal.set_parent_password_hash(p_id, new_hash)

                token = security.create_access_token({
                    "user_id": p_id,
                    "user_type": "parent",
                    "username": p_user,
                    "parent_id": p_id,
                    "school_id": school_id,
                })
                return LoginResponse(
                    access_token=token,
                    token_type="bearer",
                    user_type="parent",
                    user_id=p_id,
                    name=p_name,
                    school_id=school_id,
                )
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        elif req_role == "parent":
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    # 6. Try driver (bus table) (if role is driver or unspecified)
    if req_role in (None, "driver"):
        driver_row = _fetch_user(db_dal.get_driver_by_username, username, school_id)
        if driver_row:
            # bus_row: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password, ...)
            bus_id, _, driver_name, _, _, _, d_user, stored_cred = (
                driver_row[0], driver_row[1], driver_row[2], driver_row[3],
                driver_row[4], driver_row[5], driver_row[6], driver_row[7]
            )
            is_valid, needs_upgrade = security.verify_and_check_upgrade(password, stored_cred or "")
            if is_valid:
                clear_rate_limit(lockout_id)
                if needs_upgrade:
                    new_hash = security.hash_password(password)
                    db_dal.set_driver_password_hash(bus_id, new_hash)

                token = security.create_access_token({
                    "user_id": bus_id,
                    "user_type": "driver",
                    "username": d_user,
                    "bus_id": bus_id,
                    "school_id": school_id,
                })
                return LoginResponse(
                    access_token=token,
                    token_type="bearer",
                    user_type="driver",
                    user_id=bus_id,
                    name=driver_name,
                    school_id=school_id,
                )
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        elif req_role == "driver":
            record_failed_login(lockout_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    # User not found in any targeted table: record failure against lockout and return 401
    record_failed_login(lockout_id)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")


@router.post("/change-password")
def change_password(body: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """
    Allow any authenticated user to securely change their own password.
    Requires existing password verification and enforces password complexity.
    """
    user_type = current_user.get("user_type")
    user_id = current_user.get("user_id")

    # 1. Validate new password strength
    is_strong, err_msg = security.validate_password_strength(body.new_password)
    if not is_strong:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # 2. Verify current password
    stored_hash = None
    if user_type == "admin":
        row = db_dal.get_admin_by_id(user_id)
        if row:
            stored_hash = row[2]
    elif user_type == "parent":
        row = db_dal.get_parent_by_id(user_id)
        if row:
            stored_hash = row[6]
    elif user_type == "driver":
        row = db_dal.get_bus_by_id(user_id)
        if row:
            stored_hash = row[7]

    if not stored_hash or not security.verify_password(body.current_password, stored_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

    # 3. Hash and store new password
    new_hash = security.hash_password(body.new_password)
    updated = False
    if user_type == "admin":
        updated = db_dal.set_admin_password_hash(user_id, new_hash)
    elif user_type == "parent":
        updated = db_dal.set_parent_password_hash(user_id, new_hash)
    elif user_type == "driver":
        updated = db_dal.set_driver_password_hash(user_id, new_hash)

    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update password.")

    # 4. Invalidate any active password reset tokens
    db_dal.clear_all_password_reset_tokens(user_type, user_id)

    return {"status": "success", "message": "Password changed successfully."}


@router.post("/admin/reset-password")
def admin_reset_password(body: AdminResetPasswordRequest, current_user: dict = Depends(require_admin)):
    """
    Allows a school administrator to safely reset credentials for any student's parent or driver.
    """
    is_strong, err_msg = security.validate_password_strength(body.new_password)
    if not is_strong:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    new_hash = security.hash_password(body.new_password)
    updated = False
    if body.user_type == "admin":
        updated = db_dal.set_admin_password_hash(body.user_id, new_hash)
    elif body.user_type == "parent":
        updated = db_dal.set_parent_password_hash(body.user_id, new_hash)
    elif body.user_type == "driver":
        updated = db_dal.set_driver_password_hash(body.user_id, new_hash)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User record not found or update failed.")

    return {"status": "success", "message": f"Password for {body.user_type} (ID {body.user_id}) reset successfully."}


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, request: Request):
    """
    Generates a secure, time-limited reset token for an account.
    Valid for 15 minutes.
    Generic response is returned to prevent user enumeration attacks.
    Reset tokens are NEVER returned in API responses or logs.
    """
    client_ip = request.client.host if request.client and request.client.host else "127.0.0.1"
    check_rate_limit(f"forgot_pwd:{client_ip}", max_requests=5, window_seconds=300, block_duration_seconds=600)

    username = body.username.strip()
    user_info = None

    admin_row = db_dal.get_admin_by_username(username)
    if admin_row:
        user_info = ("admin", admin_row[0])
    else:
        parent_row = db_dal.get_parent_by_username(username)
        if parent_row:
            user_info = ("parent", parent_row[0])
        else:
            driver_row = db_dal.get_driver_by_username(username)
            if driver_row:
                user_info = ("driver", driver_row[0])

    # Consistent generic response whether user exists or not (preventing enumeration)
    generic_msg = "If an account with that username exists, password reset instructions have been generated."
    if user_info:
        u_type, u_id = user_info
        token = security.generate_secure_token()
        expiry = int(time.time()) + 900  # 15 minutes
        db_dal.save_password_reset_token(u_type, u_id, token, expiry)
        # Out-of-band email/SMS dispatch would occur here in production.
        # Credentials and tokens are NEVER returned in response or logs.

    return {
        "status": "ok",
        "message": generic_msg,
    }


@router.post("/reset-password")
def reset_password_with_token(body: ResetPasswordWithTokenRequest):
    """
    Resets an account password using a valid, unexpired reset token.
    Enforces single-use token lifecycle: all reset tokens are invalidated upon use.
    """
    # 1. Validate password strength
    is_strong, err_msg = security.validate_password_strength(body.new_password)
    if not is_strong:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # 2. Look up user
    user_id = None
    if body.user_type == "admin":
        row = db_dal.get_admin_by_username(body.username)
        if row:
            user_id = row[0]
    elif body.user_type == "parent":
        row = db_dal.get_parent_by_username(body.username)
        if row:
            user_id = row[0]
    elif body.user_type == "driver":
        row = db_dal.get_driver_by_username(body.username)
        if row:
            user_id = row[0]

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

    # 3. Verify token
    now_ts = int(time.time())
    is_valid_token = db_dal.verify_password_reset_token(body.user_type, user_id, body.reset_token, now_ts)
    if not is_valid_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

    # 4. Hash and save new password
    new_hash = security.hash_password(body.new_password)
    updated = False
    if body.user_type == "admin":
        updated = db_dal.set_admin_password_hash(user_id, new_hash)
    elif body.user_type == "parent":
        updated = db_dal.set_parent_password_hash(user_id, new_hash)
    elif body.user_type == "driver":
        updated = db_dal.set_driver_password_hash(user_id, new_hash)

    # 5. Invalidate used token and any other active reset tokens for this user
    db_dal.clear_all_password_reset_tokens(body.user_type, user_id)

    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password.")

    return {"status": "success", "message": "Password reset successfully. You may now log in with your new password."}
