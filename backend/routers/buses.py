from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin

router = APIRouter(prefix="/buses", tags=["Buses"])


class BusCreate(BaseModel):
    bus_number: str
    driver_name: str
    driver_phone: str
    capacity: int
    route_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    driver_username: Optional[str] = None
    driver_password: Optional[str] = None


class BusUpdate(BaseModel):
    bus_number: str
    driver_name: str
    driver_phone: str
    capacity: int
    route_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    driver_username: Optional[str] = None
    driver_password: Optional[str] = None


class BusOut(BaseModel):
    id: int
    bus_id: int
    bus_number: str
    driver_name: str
    driver_phone: str
    capacity: int
    route_id: Optional[int]
    route_name: Optional[str]
    username: Optional[str]
    driver_username: Optional[str]


@router.get("", response_model=List[BusOut])
def list_buses(
    search: str = Query(default="", alias="search"),
    user: dict = Depends(require_admin),
):
    """List all buses with their route names (admin only)."""
    rows = db_dal.get_all_buses(search_query=search)
    return [
        BusOut(
            id=r[0],
            bus_id=r[0],
            bus_number=r[1],
            driver_name=r[2],
            driver_phone=r[3],
            capacity=r[4],
            route_id=r[5],
            route_name=r[6],
            username=r[7],
            driver_username=r[7],
        )
        for r in rows
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_bus(body: BusCreate, user: dict = Depends(require_admin)):
    """Add a new bus, hashing the driver password if provided (admin only)."""
    uname = body.username or body.driver_username
    pwd = body.password or body.driver_password
    ok = db_dal.add_bus(
        bus_number=body.bus_number,
        driver_name=body.driver_name,
        driver_phone=body.driver_phone,
        capacity=body.capacity,
        route_id=body.route_id or 1,
        username=uname,
        password=pwd,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create bus")
    return {"message": "Bus created successfully"}


@router.put("/{bus_id}")
def update_bus(bus_id: int, body: BusUpdate, user: dict = Depends(require_admin)):
    """Update a bus record (admin only). Password is re-hashed if supplied."""
    uname = body.username or body.driver_username
    pwd = body.password or body.driver_password
    ok = db_dal.update_bus(
        bus_id=bus_id,
        bus_number=body.bus_number,
        driver_name=body.driver_name,
        driver_phone=body.driver_phone,
        capacity=body.capacity,
        username=uname,
        password=pwd,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found or update failed")
    return {"message": "Bus updated successfully"}


@router.delete("/{bus_id}", status_code=status.HTTP_200_OK)
def delete_bus(bus_id: int, user: dict = Depends(require_admin)):
    """Delete a bus record (admin only)."""
    ok = db_dal.delete_bus(bus_id=bus_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found or could not be deleted")
    return {"message": "Bus deleted successfully"}
