"""
ARES Mission Control - API Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response, Query

from backend.app.core.config import REGIONS, REGION_BOUNDS, REGION_POIS, SPACE_APPS_2026_RESOURCES
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


@router.get("/resources")
def get_challenge_resources() -> Dict[str, Any]:
    """Official NASA Space Apps Challenge 2026 Resources & Attribution."""
    return {
        "challenge": "Interplanetary Survival Guide: Martian Map",
        "challenge_url": "https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/?tab=resources",
        "resources": SPACE_APPS_2026_RESOURCES
    }


@router.get("/regions/{region_id}/elevation")
def get_point_elevation(region_id: str, lat: float = Query(...), lon: float = Query(...)) -> Dict[str, Any]:
    """Retrieve measured elevation, slope, and terrain difficulty from verified DEM."""
    from backend.app.core.terrain_pipeline import terrain_pipeline
    elev = terrain_pipeline.get_elevation_at_point(region_id, float(lat), float(lon))
    slope = terrain_pipeline.get_slope_at_point(region_id, float(lat), float(lon))
    dem_status = terrain_pipeline.get_dem_status(region_id)

    # Physical terrain classification derived from slope
    difficulty = "UNAVAILABLE"
    traversability = "UNKNOWN"
    slip_risk = "UNKNOWN"

    if slope is not None:
        if slope < 5.0:
            difficulty = "LEVEL 1 — FIRM BEDROCK / MINIMAL GRADIENT"
            traversability = "OPTIMAL"
            slip_risk = "<10% (Nominal Traction)"
        elif slope <= 12.0:
            difficulty = "LEVEL 2 — MODERATE INCLINE"
            traversability = "TRAVERSABLE"
            slip_risk = "15%–35% (Advisory Guidance)"
        elif slope <= 20.0:
            difficulty = "LEVEL 3 — STEEP REGOLITH SLIP RISK"
            traversability = "RESTRICTED / SLIP HAZARD"
            slip_risk = "40%–80% (Kinematic Slip Warning)"
        else:
            difficulty = "LEVEL 4 — IMPASSABLE SCARP / CLIFF"
            traversability = "NON-TRAVERSABLE"
            slip_risk = ">80% (Critical Roll/Stall Danger)"

    return {
        "region_id": region_id,
        "lat": lat,
        "lon": lon,
        "dem_available": dem_status.is_available,
        "elevation_m": elev,
        "slope_deg": slope,
        "difficulty_level": difficulty,
        "traversability": traversability,
        "slip_risk": slip_risk,
        "resolution": "200 m/pixel",
        "units": "meters relative to MOLA Areoid datum",
        "datum": "MOLA Areoid (IAU 2000)",
        "source": "USGS HRSC/MOLA 200m blended DEM" if dem_status.is_available else "UNAVAILABLE"
    }


@router.get("/regions/{region_id}/layers")
def get_region_layers(region_id: str) -> Dict[str, Any]:
    """Inspect and retrieve verified scientific cartographic layers available for this region."""
    from backend.app.core.map_service import JEZERO_CTX_BOUNDS, JEZERO_CTX_FILE
    from backend.app.core.config import REGION_BOUNDS
    from backend.app.core.terrain_pipeline import terrain_pipeline

    dem_status = terrain_pipeline.get_dem_status(region_id)
    reg_bounds = REGION_BOUNDS.get(region_id, {})

    layers: Dict[str, Any] = {
        "mola_basemap": {
            "name": "MOLA MEG256 Color Basemap",
            "type": "VISUAL_CARTOGRAPHY",
            "available": True,
            "bounds": reg_bounds,
            "description": "Visual shaded relief cartography from MGS MOLA MEG256 dataset (not numerical elevation).",
            "url": f"/api/regions/{region_id}/map"
        },
        "dem_elevation": {
            "name": "USGS 200m DEM Hypsometric Tint",
            "type": "NUMERICAL_ELEVATION_OVERLAY",
            "available": dem_status.is_available,
            "description": "Hypsometric elevation tint calculated directly from 200m blended numerical DEM array.",
            "url": f"/api/regions/{region_id}/elevation-map"
        },
        "dem_slope": {
            "name": "USGS 200m Slope Hazard Heatmap",
            "type": "NUMERICAL_SLOPE_OVERLAY",
            "available": dem_status.is_available,
            "description": "Physical surface slope angles computed via central finite difference gradient calculus.",
            "url": f"/api/regions/{region_id}/slope-map"
        }
    }

    if region_id == "jezero-crater" and JEZERO_CTX_FILE.exists():
        layers["ctx_orthomosaic"] = {
            "name": "Jezero 6m CTX Orthomosaic",
            "type": "ORBITAL_IMAGERY_HIGH_RES",
            "available": True,
            "bounds": JEZERO_CTX_BOUNDS,
            "resolution": "6.0 meters/pixel",
            "instrument": "MRO Context Camera (CTX)",
            "url": "/api/regions/jezero-crater/ctx-map"
        }
        layers["crism_minerals"] = {
            "name": "CRISM Hydrous Mineral Sites",
            "type": "SPECTRAL_MINERALOGY",
            "available": True,
            "instrument": "MRO CRISM Spectrometer",
            "url": "/api/regions/jezero-crater/hydrous-sites"
        }

    return {
        "region_id": region_id,
        "layers": layers
    }


@router.get("/regions/jezero-crater/ctx-map")
def get_jezero_ctx_map(max_dim: int = 2048, quality: int = 85) -> Response:
    """Stream high-resolution 6-meter/pixel Jezero CTX orthomosaic as optimized JPEG."""
    from backend.app.core.map_service import get_jezero_ctx_bytes
    jpeg_bytes = get_jezero_ctx_bytes(max_dim=max_dim, quality=quality)
    if not jpeg_bytes:
        raise HTTPException(status_code=404, detail="Jezero CTX mosaic file not found on disk")

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Instrument": "MRO-CTX-6M-ORTHOMOSAIC"
        }
    )


@router.get("/regions/{region_id}/elevation-map")
def get_region_elevation_map(region_id: str) -> Response:
    """Stream transparent RGBA PNG hypsometric tint overlay calculated from numerical DEM."""
    from backend.app.core.map_service import get_elevation_tint_bytes
    png_bytes = get_elevation_tint_bytes(region_id)
    if not png_bytes:
        raise HTTPException(status_code=404, detail=f"Numerical DEM elevation grid not available for '{region_id}'")

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Terrain-Layer": "USGS-MOLA-HRSC-HYPSOMETRIC-TINT"
        }
    )


@router.get("/regions/{region_id}/hydrous-sites")
def get_region_hydrous_sites(region_id: str) -> List[Dict[str, Any]]:
    """Retrieve verified MRO CRISM spectral hydrous mineral detections for the region."""
    from backend.app.core.map_service import get_crism_hydrous_sites
    if region_id == "jezero-crater":
        return get_crism_hydrous_sites()
    return []


@router.get("/regions/{region_id}/slope-map")
def get_region_slope_map(region_id: str) -> Response:
    """Stream transparent RGBA PNG overlay depicting physical terrain slope gradients."""
    import io
    from PIL import Image
    import numpy as np
    from backend.app.core.terrain_pipeline import terrain_pipeline

    slope_data = terrain_pipeline.get_slope_grid(region_id)
    if slope_data is None:
        raise HTTPException(status_code=404, detail=f"Numerical DEM slope grid not available for '{region_id}'")

    slope_grid, meta = slope_data
    h, w = slope_grid.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    valid = ~np.isnan(slope_grid)
    gentle = valid & (slope_grid < 5.0)
    moderate = valid & (slope_grid >= 5.0) & (slope_grid <= 15.0)
    steep = valid & (slope_grid > 15.0)

    rgba[gentle] = [84, 201, 154, 90]     # Ares green (safe <5°)
    rgba[moderate] = [242, 169, 59, 130]  # Ares amber (moderate 5°-15°)
    rgba[steep] = [239, 85, 85, 180]      # Ares red (steep >15°)

    img = Image.fromarray(rgba, "RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Terrain-Layer": "USGS-MOLA-HRSC-SLOPE-GRADIENT"
        }
    )

