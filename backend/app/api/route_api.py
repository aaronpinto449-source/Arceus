"""
ARES Route Planning — FastAPI endpoint.

Exposes: POST /api/routes/plan
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.core.route_models import RoutePlanRequest, RoutePlanResponse
from backend.app.core.route_solver import plan_route

router = APIRouter(prefix="/api/routes", tags=["Route Planning"])


@router.post(
    "/plan",
    response_model=RoutePlanResponse,
    summary="Plan a waypoint-based surface route between two Mars coordinates",
    description=(
        "Computes a geometrically honest route using great-circle (Haversine) distances "
        "between verified POI waypoints. "
        "No terrain, slope, elevation, or hazard data is used — these fields are "
        "explicitly marked UNAVAILABLE in the response. "
        "Travel duration is ESTIMATED from stated nominal rover speed on flat terrain only. "
        "This endpoint must NOT be used for real astronaut navigation decisions."
    ),
)
def plan_route_endpoint(request: RoutePlanRequest) -> RoutePlanResponse:
    """
    Plan a Mars surface route.

    **Input:**
    - `region_id`: `gale-crater` | `jezero-crater` | `olympus-mons`
    - `start`: Departure coordinate (planetocentric lat °N, east lon °E)
    - `destination`: Arrival coordinate (same convention)
    - `rover_type`: `PCR` | `LUV` | `HCH`
    - `priority`: `SAFETY` | `DISTANCE` | `BALANCED`

    **Output:**
    - Route geometry (coordinates, segments)
    - Calculated: great-circle distance, bearing
    - Estimated: travel duration (stated assumption)
    - Unavailable: slope, terrain cost, hazard exposure, elevation profile
    - Rover feasibility vs nominal range
    - Full provenance labels and scientific disclaimer
    """
    try:
        return plan_route(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Route solver internal error: {exc}",
        ) from exc
