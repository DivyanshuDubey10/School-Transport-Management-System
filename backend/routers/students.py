from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin

router = APIRouter(prefix="/students", tags=["Students"])


class StudentCreate(BaseModel):
    student_name: Optional[str] = None
    name: Optional[str] = None
    student_class: Optional[str] = None
    class_name: Optional[str] = None
    parent_id: int
    route_id: Optional[int] = None
    fee_paid: float = 0.0
    fee_balance: float = 0.0


class StudentUpdate(BaseModel):
    student_name: Optional[str] = None
    name: Optional[str] = None
    student_class: Optional[str] = None
    class_name: Optional[str] = None
    parent_id: int
    route_id: Optional[int] = None
    fee_paid: float = 0.0
    fee_balance: float = 0.0


class StudentOut(BaseModel):
    id: int
    student_id: int
    name: str
    student_name: str
    class_name: str
    student_class: str
    parent_id: int
    phone: Optional[str]
    parent_phone: Optional[str]
    address: Optional[str]
    bus_id: Optional[int]
    route_id: Optional[int]
    fee_paid: float
    fee_balance: float
    transport_status: str


@router.get("", response_model=List[StudentOut])
def list_students(
    search: str = Query(default="", alias="search"),
    user: dict = Depends(require_admin),
):
    """List all students, optionally filtered by name or class (admin only)."""
    rows = db_dal.get_all_students(search_query=search)
    return [
        StudentOut(
            id=r[0],
            student_id=r[0],
            name=r[1],
            student_name=r[1],
            class_name=r[2],
            student_class=r[2],
            parent_id=r[3],
            phone=r[4],
            parent_phone=r[4],
            address=r[5],
            bus_id=r[6],
            route_id=r[7],
            fee_paid=float(r[8]) if r[8] is not None else 0.0,
            fee_balance=float(r[9]) if r[9] is not None else 0.0,
            transport_status=r[10] or "active",
        )
        for r in rows
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(body: StudentCreate, user: dict = Depends(require_admin)):
    """Add a new student (admin only)."""
    s_name = body.student_name or body.name or ""
    s_class = body.student_class or body.class_name or ""
    ok = db_dal.add_student(
        student_name=s_name,
        student_class=s_class,
        parent_id=body.parent_id,
        route_id=body.route_id or 1,
        fee_paid=body.fee_paid,
        fee_balance=body.fee_balance,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create student")
    return {"message": "Student created successfully"}


@router.put("/{student_id}")
def update_student(student_id: int, body: StudentUpdate, user: dict = Depends(require_admin)):
    """Update an existing student's details (admin only)."""
    s_name = body.student_name or body.name or ""
    s_class = body.student_class or body.class_name or ""
    ok = db_dal.update_student(
        student_id=student_id,
        name=s_name,
        class_name=s_class,
        parent_id=body.parent_id,
        route_id=body.route_id or 1,
        fee_paid=body.fee_paid,
        fee_balance=body.fee_balance,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or update failed")
    return {"message": "Student updated successfully"}


@router.delete("/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, user: dict = Depends(require_admin)):
    """Delete a student record (admin only)."""
    ok = db_dal.delete_student(student_id=student_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return {"message": "Student deleted successfully"}
