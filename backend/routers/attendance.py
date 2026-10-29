from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin, require_driver, get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])


class AttendanceRecord(BaseModel):
    student_id: int
    status: str  # "Present" | "Absent"


class MarkAttendanceRequest(BaseModel):
    date: str  # YYYY-MM-DD
    records: List[AttendanceRecord]


class AttendanceAdminOut(BaseModel):
    date: str
    student_name: str
    student_class: str
    bus_number: str
    attendance_status: str


class StudentForDriver(BaseModel):
    student_id: int
    student_name: str
    student_class: str
    pickup_point: Optional[str]
    phone: Optional[str]
    parent_name: Optional[str]


class StudentAttendanceHistory(BaseModel):
    date: str
    attendance_status: str


@router.get("", response_model=List[AttendanceAdminOut])
def list_attendance(
    search: str = Query(default="", alias="search"),
    user: dict = Depends(require_admin),
):
    """Return all attendance records (admin only)."""
    rows = db_dal.get_attendance_history_for_admin(search_query=search)
    return [
        AttendanceAdminOut(
            date=str(r[0]),
            student_name=r[1],
            student_class=r[2],
            bus_number=r[3],
            attendance_status=r[4],
        )
        for r in rows
    ]


@router.get("/my-students", response_model=List[StudentForDriver])
def my_students(user: dict = Depends(require_driver)):
    """Return the list of students on the driver's bus (driver only)."""
    bus_id = user.get("bus_id") or user.get("user_id")
    rows = db_dal.get_students_by_bus(bus_id=bus_id)
    return [
        StudentForDriver(
            student_id=r[0],
            student_name=r[1],
            student_class=r[2],
            pickup_point=r[3],
            phone=r[4],
            parent_name=r[5],
        )
        for r in rows
    ]


@router.post("/mark", status_code=status.HTTP_201_CREATED)
def mark_attendance(body: MarkAttendanceRequest, user: dict = Depends(require_driver)):
    """Mark attendance for all students on the driver's bus for a given date (driver only)."""
    bus_id = user.get("bus_id") or user.get("user_id")
    failures = []
    for record in body.records:
        ok = db_dal.mark_attendance(
            student_id=record.student_id,
            bus_id=bus_id,
            date=body.date,
            status=record.status,
        )
        if not ok:
            failures.append(record.student_id)
    if failures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to mark attendance for student IDs: {failures}",
        )
    return {"message": "Attendance marked successfully"}


@router.get("/student/{student_id}", response_model=List[StudentAttendanceHistory])
def student_attendance_history(student_id: int, user: dict = Depends(get_current_user)):
    """Return last 30 attendance records for a student (any authenticated user)."""
    rows = db_dal.get_attendance_history_for_student(student_id=student_id)
    return [
        StudentAttendanceHistory(date=str(r[0]), attendance_status=r[1])
        for r in rows
    ]
