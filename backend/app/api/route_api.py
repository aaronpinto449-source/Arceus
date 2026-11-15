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
    summary="Estimate great-circle distance between two Mars coordinates",
    description=(
        "Returns a direct great-circle (Haversine) geometric estimate between the "
        "submitted coordinates. All priority values currently return this same geometry. "
        "No terrain, slope, elevation, or hazard data is used — these fields are "
        "explicitly marked UNAVAILABLE in the response. "
        "Travel duration is ESTIMATED from stated nominal rover speed on flat terrain only. "
        "The estimate is not a surface route and must NOT be used for real astronaut "
        "navigation decisions."
    ),
)
def plan_route_endpoint(request: RoutePlanRequest) -> RoutePlanResponse:
    """
    Estimate geometric distance between Mars coordinates.

    **Input:**
    - `region_id`: `gale-crater` | `jezero-crater` | `olympus-mons`
    - `start`: Departure coordinate (planetocentric lat °N, east lon °E)
    - `destination`: Arrival coordinate (same convention)
    - `rover_type`: `PCR` | `LUV` | `HCH`
    - `priority`: `SAFETY` | `DISTANCE` | `BALANCED`

    **Output:**
    - One direct great-circle segment (submitted endpoints are preserved)
    - Calculated: great-circle distance, bearing
    - Estimated: travel duration (stated assumption)
    - Unavailable: slope, terrain cost, hazard exposure, elevation profile
    - Comparison with an illustrative rover range assumption
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
