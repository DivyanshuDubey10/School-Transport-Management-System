from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import security
from dal import db_dal
from middleware.auth_middleware import require_admin, require_parent

router = APIRouter(prefix="/parents", tags=["Parents"])


class ParentCreate(BaseModel):
    parent_name: Optional[str] = None
    name: Optional[str] = None
    phone: str
    address: str
    pickup_point: str
    username: str
    password: str


class ParentUpdate(BaseModel):
    parent_name: Optional[str] = None
    name: Optional[str] = None
    phone: str
    address: str
    pickup_point: str
    username: str


class ParentOut(BaseModel):
    id: int
    parent_id: int
    name: str
    parent_name: str
    phone: str
    address: str
    pickup_point: str
    username: str


class ChildOut(BaseModel):
    id: int
    student_id: int
    name: str
    student_name: str
    class_name: str
    student_class: str
    fee_paid: float
    fee_balance: float
    bus_number: Optional[str]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    route_name: Optional[str]
    pickup_point: Optional[str]


@router.get("", response_model=List[ParentOut])
def list_parents(
    search: str = Query(default="", alias="search"),
    user: dict = Depends(require_admin),
):
    """List all parents (admin only)."""
    rows = db_dal.get_all_parents(search_query=search)
    return [
        ParentOut(
            id=r[0],
            parent_id=r[0],
            name=r[1],
            parent_name=r[1],
            phone=r[2],
            address=r[3],
            pickup_point=r[4],
            username=r[5],
        )
        for r in rows
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_parent(body: ParentCreate, user: dict = Depends(require_admin)):
    """Add a new parent with a hashed password (admin only)."""
    p_name = body.parent_name or body.name or ""
    hashed = security.hash_password(body.password)
    ok = db_dal.add_parent(
        name=p_name,
        phone=body.phone,
        address=body.address,
        pickup_point=body.pickup_point,
        username=body.username,
        password=hashed,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create parent")
    return {"message": "Parent created successfully"}


@router.put("/{parent_id}")
def update_parent(parent_id: int, body: ParentUpdate, user: dict = Depends(require_admin)):
    """Update a parent's details (admin only)."""
    p_name = body.parent_name or body.name or ""
    ok = db_dal.update_parent(
        parent_id=parent_id,
        name=p_name,
        phone=body.phone,
        address=body.address,
        pickup_point=body.pickup_point,
        username=body.username,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found or update failed")
    return {"message": "Parent updated successfully"}


@router.delete("/{parent_id}", status_code=status.HTTP_200_OK)
def delete_parent(parent_id: int, user: dict = Depends(require_admin)):
    """Delete a parent and their associated students (admin only)."""
    ok = db_dal.delete_parent(parent_id=parent_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")
    return {"message": "Parent deleted successfully"}


@router.get("/my-children", response_model=List[ChildOut])
def my_children(user: dict = Depends(require_parent)):
    """Return children records for the currently logged-in parent."""
    parent_id = user.get("parent_id") or user.get("user_id")
    rows = db_dal.get_parent_dashboard_students(parent_id=parent_id)
    return [
        ChildOut(
            id=r[0],
            student_id=r[0],
            name=r[1],
            student_name=r[1],
            class_name=r[2],
            student_class=r[2],
            fee_paid=float(r[3]) if r[3] is not None else 0.0,
            fee_balance=float(r[4]) if r[4] is not None else 0.0,
            bus_number=r[5],
            driver_name=r[6],
            driver_phone=r[7],
            route_name=r[8],
            pickup_point=r[9],
        )
        for r in rows
    ]
