"""
ARES Mission Control - API Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response, Query

from backend.app.core.config import REGIONS, REGION_BOUNDS, REGION_POIS
from backend.app.core.map_service import get_optimized_map_bytes, calculate_ground_resolution

router = APIRouter(prefix="/api")


@router.get("/health")
def get_health() -> Dict[str, Any]:
    """Mission Control System Health Diagnostic."""
    return {
        "status": "OPERATIONAL",
        "system": "ARES Planetary Mission Control API",
        "version": "1.0.0",
        "sol": "001",
        "planetary_target": "Mars (4th planet from Sun)",
        "telemetry_stream": "NOMINAL"
    }


@router.get("/regions")
def list_regions() -> List[Dict[str, Any]]:
    """List all available Mars exploration zones."""
    output = []
    for reg_id, reg in REGIONS.items():
        bounds = REGION_BOUNDS.get(reg_id, {})
        pois = REGION_POIS.get(reg_id, [])
        output.append({
            **reg,
            "bounds": bounds,
            "poi_count": len(pois)
        })
    return output


@router.get("/regions/{region_id}")
def get_region(region_id: str) -> Dict[str, Any]:
    """Retrieve full scientific profile and bounds for a specific region."""
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found in planetary database")

    reg = REGIONS[region_id]
    bounds = REGION_BOUNDS.get(region_id, {})
    pois = REGION_POIS.get(region_id, [])
    return {
        **reg,
        "bounds": bounds,
        "pois": pois
    }


@router.get("/regions/{region_id}/pois")
def get_region_pois(region_id: str) -> List[Dict[str, Any]]:
    """Retrieve verified NASA scientific points of interest for a region."""
    if region_id not in REGION_POIS:
        raise HTTPException(status_code=404, detail=f"No POIs found for region '{region_id}'")
    return REGION_POIS[region_id]


@router.get("/regions/{region_id}/map")
def get_region_map(
    region_id: str,
    max_dim: int = 1536,
    quality: int = 85
) -> Response:
    """Stream optimized in-memory MOLA colorized elevation tile."""
    # Ensure integer bounds
    clamped_dim = max(512, min(3072, int(max_dim)))
    clamped_quality = max(50, min(95, int(quality)))

    jpeg_bytes = get_optimized_map_bytes(region_id, max_dim=clamped_dim, quality=clamped_quality)
    if not jpeg_bytes:
        raise HTTPException(status_code=404, detail=f"MOLA map image not available for '{region_id}'")

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Planetary-Basemap": "NASA-MGS-MOLA-MEG256"
        }
    )


@router.get("/telemetry/resolution")
def get_spatial_resolution(lat: float = 0.0) -> Dict[str, Any]:
    """Calculate local spatial ground resolution at given latitude."""
    return calculate_ground_resolution(float(lat))
