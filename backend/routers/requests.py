from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin, require_parent

router = APIRouter(prefix="/requests", tags=["Transport Requests"])


class CreateRequestBody(BaseModel):
    student_id: int
    requested_pickup_point: str


class ApproveRequestBody(BaseModel):
    new_route_id: Optional[int] = None
    new_pickup_point: Optional[str] = None


class TransportRequestOut(BaseModel):
    id: int
    request_id: int
    student_id: int
    student_name: str
    student_class: str
    class_name: str
    parent_name: str
    requested_pickup_point: str
    current_pickup_point: Optional[str] = ""
    request_status: str
    status: str
    parent_id: int


@router.get("", response_model=List[TransportRequestOut])
def list_pending_requests(user: dict = Depends(require_admin)):
    """List all pending transport change requests (admin only)."""
    rows = db_dal.get_pending_requests()
    return [
        TransportRequestOut(
            id=r[0],
            request_id=r[0],
            student_id=r[1],
            student_name=r[2],
            student_class=r[3],
            class_name=r[3],
            parent_name=r[4],
            requested_pickup_point=r[5],
            current_pickup_point="",
            request_status=r[6],
            status=r[6].lower(),
            parent_id=r[7],
        )
        for r in rows
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_request(body: CreateRequestBody, user: dict = Depends(require_parent)):
    """Create a transport change request (parent only)."""
    ok = db_dal.create_change_request(
        student_id=body.student_id,
        new_pickup_point=body.requested_pickup_point,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create request")
    return {"message": "Transport change request submitted successfully"}


@router.put("/{request_id}/approve")
@router.patch("/{request_id}/approve")
def approve_request(
    request_id: int,
    body: Optional[ApproveRequestBody] = None,
    user: dict = Depends(require_admin),
):
    """Approve a transport change request (admin only)."""
    pending = db_dal.get_pending_requests()
    req = next((r for r in pending if r[0] == request_id), None)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found or already processed")

    student_id = req[1]
    pickup = (body.new_pickup_point if body and body.new_pickup_point else req[5])
    route_id = (body.new_route_id if body and body.new_route_id else 1)
    parent_id = req[7]

    ok = db_dal.approve_change_request(
        request_id=request_id,
        student_id=student_id,
        new_route_id=route_id,
        new_pickup_point=pickup,
        parent_id=parent_id,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to approve request")
    return {"message": "Request approved successfully"}


@router.put("/{request_id}/reject")
@router.patch("/{request_id}/reject")
def reject_request(request_id: int, user: dict = Depends(require_admin)):
    """Reject a transport change request (admin only)."""
    ok = db_dal.reject_change_request(request_id=request_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found or already processed")
    return {"message": "Request rejected successfully"}
