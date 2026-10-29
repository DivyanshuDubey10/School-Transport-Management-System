from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import security
from dal import db_dal

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int
    name: str


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    """
    Authenticate a user (admin, parent, or driver) and return a JWT access token.
    """
    username = body.username.strip()
    password = body.password.strip()

    # 1. Try admin
    admin_row = db_dal.get_admin_by_username(username)
    if admin_row:
        # admin_row: (admin_id, USERNAME, password, full_name)
        if security.verify_password(password, admin_row[2]):
            token = security.create_access_token({
                "user_id": admin_row[0],
                "user_type": "admin",
                "username": admin_row[1],
            })
            return LoginResponse(
                access_token=token,
                token_type="bearer",
                user_type="admin",
                user_id=admin_row[0],
                name=admin_row[3],
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 2. Try parent
    parent_row = db_dal.get_parent_by_username(username)
    if parent_row:
        # parent_row: (parent_id, parent_name, phone, address, pickup_point, username, password)
        if security.verify_password(password, parent_row[6]):
            token = security.create_access_token({
                "user_id": parent_row[0],
                "user_type": "parent",
                "username": parent_row[5],
                "parent_id": parent_row[0],
            })
            return LoginResponse(
                access_token=token,
                token_type="bearer",
                user_type="parent",
                user_id=parent_row[0],
                name=parent_row[1],
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 3. Try driver (bus table)
    driver_row = db_dal.get_driver_by_username(username)
    if driver_row:
        # bus_row: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
        if driver_row[7] and security.verify_password(password, driver_row[7]):
            token = security.create_access_token({
                "user_id": driver_row[0],
                "user_type": "driver",
                "username": driver_row[6],
                "bus_id": driver_row[0],
            })
            return LoginResponse(
                access_token=token,
                token_type="bearer",
                user_type="driver",
                user_id=driver_row[0],
                name=driver_row[2],
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
