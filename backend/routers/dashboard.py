from fastapi import APIRouter, Depends
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dal import db_dal
from middleware.auth_middleware import require_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_summary(user: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Return aggregated dashboard statistics for the admin overview."""
    stats = db_dal.get_dashboard_stats()
    parents = db_dal.get_all_parents()
    occupancy_rows = db_dal.get_route_occupancy()
    fees = db_dal.get_fee_status_distribution()

    return {
        "stats": {
            "total_students": stats.get("total_students", 0),
            "active_buses": stats.get("total_buses", 0),
            "designated_routes": stats.get("total_routes", 0),
            "total_parents": len(parents),
        },
        "route_occupancy": [
            {
                "route_name": r[0],
                "students": r[1],
                "capacity": r[2],
            }
            for r in occupancy_rows
        ],
        "fee_status": {
            "paid": fees.get("fully_paid", 0),
            "pending": fees.get("pending", 0),
        },
    }


@router.get("/stats")
def get_stats(user: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Return high-level dashboard statistics (admin only)."""
    return db_dal.get_dashboard_stats()


@router.get("/occupancy")
def get_occupancy(user: dict = Depends(require_admin)) -> List[Dict[str, Any]]:
    """Return per-route occupancy data (admin only)."""
    rows = db_dal.get_route_occupancy()
    return [
        {
            "route_name": row[0],
            "students": row[1],
            "capacity": row[2],
        }
        for row in rows
    ]


@router.get("/fees")
def get_fees(user: dict = Depends(require_admin)) -> Dict[str, int]:
    """Return fee payment distribution (admin only)."""
    return db_dal.get_fee_status_distribution()
