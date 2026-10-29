from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin

router = APIRouter(prefix="/routes", tags=["Routes"])


class RouteCreate(BaseModel):
    route_name: str


class RouteUpdate(BaseModel):
    route_name: str


class RouteOut(BaseModel):
    id: int
    route_id: int
    route_name: str


@router.get("", response_model=List[RouteOut])
def list_routes(
    search: str = Query(default="", alias="search"),
    user: dict = Depends(require_admin),
):
    """List all routes (admin only)."""
    rows = db_dal.get_all_routes(search_query=search)
    return [RouteOut(id=r[0], route_id=r[0], route_name=r[1]) for r in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_route(body: RouteCreate, user: dict = Depends(require_admin)):
    """Add a new route (admin only)."""
    ok = db_dal.add_route(route_name=body.route_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create route")
    return {"message": "Route created successfully"}


@router.put("/{route_id}")
def update_route(route_id: int, body: RouteUpdate, user: dict = Depends(require_admin)):
    """Update a route's name (admin only)."""
    ok = db_dal.update_route(route_id=route_id, route_name=body.route_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found or update failed")
    return {"message": "Route updated successfully"}


@router.delete("/{route_id}", status_code=status.HTTP_200_OK)
def delete_route(route_id: int, user: dict = Depends(require_admin)):
    """Delete a route (cascades to buses and students) (admin only)."""
    ok = db_dal.delete_route(route_id=route_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return {"message": "Route deleted successfully"}
