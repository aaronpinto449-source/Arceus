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
        "between verified POI waypoints.\n\n"
        "**Priority Modes:**\n"
        "- `DISTANCE`: Direct single-leg Haversine route between start and destination coordinates. "
        "Calculates the geometric lower-bound straight-line distance; it does NOT perform "
        "obstacle-aware or terrain-shortest-path navigation.\n"
        "- `BALANCED`: Multi-waypoint route solved via Dijkstra over the graph of verified regional NASA POIs. "
        "Does NOT guarantee surface traversability or obstacle clearance between POIs.\n"
        "- `SAFETY`: Identical routing geometry to BALANCED, with an explicit advisory to conduct orbital "
        "reconnaissance before traversal.\n\n"
        "**Important Constraints:**\n"
        "- No numerical DEM, slope, elevation, or hazard data is used — these fields are explicitly "
        "marked UNAVAILABLE in the response.\n"
        "- Travel duration is ESTIMATED from assumed nominal rover speed on flat terrain.\n"
        "- Rover range feasibility compares against illustrative planning assumptions.\n"
        "- This endpoint must NOT be used for real astronaut navigation decisions."
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
    - `priority`:
      - `DISTANCE`: Direct single-segment Haversine line (geometric minimum, not obstacle-aware).
      - `BALANCED`: Dijkstra path across verified regional POIs (does not guarantee terrain traversability).
      - `SAFETY`: Same as BALANCED with additional operational survey advisory.

    **Output:**
    - Route geometry (coordinates, segments with individual obstacle disclaimers)
    - Calculated: great-circle distance, bearing
    - Estimated: travel duration (with explicit operational speed assumption)
    - Rover feasibility vs nominal illustrative range (with range caveat)
    - Unavailable: slope, terrain cost, hazard exposure, elevation profile
    - Documented snap threshold (0.05° ≈ ~3 km)
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
