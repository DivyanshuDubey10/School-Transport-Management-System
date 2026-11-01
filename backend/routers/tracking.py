import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user
from dal import db_dal

router = APIRouter(prefix="/tracking", tags=["Live Tracking"])

# Predefined coordinate waypoints for routes to ensure realistic maps
DEFAULT_ROUTE_WAYPOINTS: Dict[str, List[Dict[str, Any]]] = {
    "default": [
        {"name": "Delhi Public School Main Campus", "lat": 28.6139, "lng": 77.2090, "type": "school"},
        {"name": "Purana Bazar Crossing", "lat": 28.6195, "lng": 77.2165, "type": "stop"},
        {"name": "Civil Lines Gate 2", "lat": 28.6270, "lng": 77.2240, "type": "stop"},
        {"name": "Model Town Block B", "lat": 28.6340, "lng": 77.2315, "type": "stop"},
        {"name": "Green Park Community Hall", "lat": 28.6410, "lng": 77.2390, "type": "stop"},
    ],
    "purana": [
        {"name": "Central Campus", "lat": 28.6139, "lng": 77.2090, "type": "school"},
        {"name": "Purana Bazar Chowk", "lat": 28.6190, "lng": 77.2155, "type": "stop"},
        {"name": "Purana Bazar Bus Stand", "lat": 28.6235, "lng": 77.2198, "type": "stop"},
        {"name": "Railway Colony North", "lat": 28.6295, "lng": 77.2270, "type": "stop"},
    ],
    "express": [
        {"name": "Campus Terminal", "lat": 28.6139, "lng": 77.2090, "type": "school"},
        {"name": "Ring Road Flyover", "lat": 28.6210, "lng": 77.2280, "type": "stop"},
        {"name": "Sector 14 Central Plaza", "lat": 28.6310, "lng": 77.2420, "type": "stop"},
        {"name": "Highland Residency Gate", "lat": 28.6420, "lng": 77.2550, "type": "stop"},
    ],
}

# In-memory tracking state dictionary: bus_id -> tracking_data
LIVE_BUS_LOCATIONS: Dict[int, Dict[str, Any]] = {}


class LocationUpdatePayload(BaseModel):
    bus_id: int
    latitude: float
    longitude: float
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    status: Optional[str] = "In Transit"
    next_stop: Optional[str] = None


class TripControlPayload(BaseModel):
    bus_id: int


def _get_route_waypoints(route_name: str) -> List[Dict[str, Any]]:
    name_lower = (route_name or "").lower()
    if "purana" in name_lower:
        return DEFAULT_ROUTE_WAYPOINTS["purana"]
    elif "express" in name_lower or "highway" in name_lower:
        return DEFAULT_ROUTE_WAYPOINTS["express"]
    return DEFAULT_ROUTE_WAYPOINTS["default"]


@router.post("/update")
def update_bus_location(
    payload: LocationUpdatePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Called periodically by driver's device (or driver portal simulator) to push GPS updates.
    """
    bus = db_dal.get_bus_by_id(payload.bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    bus_number = bus[1]
    driver_name = bus[2]
    route_id = bus[5]

    route_name = "Assigned Route"
    if route_id:
        routes = db_dal.get_all_routes()
        for r in routes:
            if r[0] == route_id:
                route_name = r[1]
                break

    waypoints = _get_route_waypoints(route_name)

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"

    LIVE_BUS_LOCATIONS[payload.bus_id] = {
        "bus_id": payload.bus_id,
        "bus_number": bus_number,
        "driver_name": driver_name,
        "route_id": route_id,
        "route_name": route_name,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "speed": payload.speed or 0.0,
        "heading": payload.heading or 0.0,
        "status": payload.status or "In Transit",
        "next_stop": payload.next_stop or (waypoints[1]["name"] if len(waypoints) > 1 else "School Campus"),
        "last_updated": now_iso,
        "waypoints": waypoints,
    }

    return {"status": "ok", "bus_id": payload.bus_id, "timestamp": now_iso}


@router.post("/trip/start")
def start_trip(
    payload: TripControlPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Starts trip for a bus."""
    bus = db_dal.get_bus_by_id(payload.bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    route_id = bus[5]
    route_name = "Assigned Route"
    if route_id:
        routes = db_dal.get_all_routes()
        for r in routes:
            if r[0] == route_id:
                route_name = r[1]
                break

    waypoints = _get_route_waypoints(route_name)
    start_pt = waypoints[0]

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    LIVE_BUS_LOCATIONS[payload.bus_id] = {
        "bus_id": payload.bus_id,
        "bus_number": bus[1],
        "driver_name": bus[2],
        "route_id": route_id,
        "route_name": route_name,
        "latitude": start_pt["lat"],
        "longitude": start_pt["lng"],
        "speed": 22.5,
        "heading": 40.0,
        "status": "In Transit",
        "next_stop": waypoints[1]["name"] if len(waypoints) > 1 else "Next Stop",
        "last_updated": now_iso,
        "waypoints": waypoints,
    }

    return {"status": "started", "bus_id": payload.bus_id, "tracking": LIVE_BUS_LOCATIONS[payload.bus_id]}


@router.post("/trip/stop")
def stop_trip(
    payload: TripControlPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Stops trip for a bus."""
    if payload.bus_id in LIVE_BUS_LOCATIONS:
        LIVE_BUS_LOCATIONS[payload.bus_id]["status"] = "Completed"
        LIVE_BUS_LOCATIONS[payload.bus_id]["speed"] = 0.0
        LIVE_BUS_LOCATIONS[payload.bus_id]["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"

    return {"status": "stopped", "bus_id": payload.bus_id}


@router.get("/bus/{bus_id}")
def get_bus_tracking(
    bus_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns live tracking data for a specific bus.
    If no live GPS data has been sent yet, returns initialized route data.
    """
    if bus_id in LIVE_BUS_LOCATIONS:
        return LIVE_BUS_LOCATIONS[bus_id]

    bus = db_dal.get_bus_by_id(bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    route_id = bus[5]
    route_name = "Assigned Route"
    if route_id:
        routes = db_dal.get_all_routes()
        for r in routes:
            if r[0] == route_id:
                route_name = r[1]
                break

    waypoints = _get_route_waypoints(route_name)
    initial_pt = waypoints[0]

    return {
        "bus_id": bus_id,
        "bus_number": bus[1],
        "driver_name": bus[2],
        "route_id": route_id,
        "route_name": route_name,
        "latitude": initial_pt["lat"],
        "longitude": initial_pt["lng"],
        "speed": 0.0,
        "heading": 0.0,
        "status": "Idle",
        "next_stop": waypoints[1]["name"] if len(waypoints) > 1 else "Purana Bazar",
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
        "waypoints": waypoints,
    }


@router.get("/fleet")
def get_fleet_tracking(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns live location of all buses in the fleet for Admin view.
    """
    all_buses = db_dal.get_all_buses()
    fleet = []

    for b in all_buses:
        # b: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
        b_id = b[0]
        if b_id in LIVE_BUS_LOCATIONS:
            fleet.append(LIVE_BUS_LOCATIONS[b_id])
        else:
            # Fallback initialized state
            route_name = "Assigned Route"
            r_id = b[5]
            if r_id:
                routes = db_dal.get_all_routes()
                for r in routes:
                    if r[0] == r_id:
                        route_name = r[1]
                        break
            waypoints = _get_route_waypoints(route_name)
            # Offset slightly per bus index so buses don't overlap if all idle
            offset = (b_id % 5) * 0.003
            fleet.append({
                "bus_id": b_id,
                "bus_number": b[1],
                "driver_name": b[2],
                "route_id": r_id,
                "route_name": route_name,
                "latitude": waypoints[0]["lat"] + offset,
                "longitude": waypoints[0]["lng"] + offset,
                "speed": 0.0,
                "heading": 0.0,
                "status": "Idle",
                "next_stop": waypoints[1]["name"] if len(waypoints) > 1 else "School Campus",
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
                "waypoints": waypoints,
            })

    return {"count": len(fleet), "buses": fleet}
