"""
ARES Route Planning Engine — core solver.

Data integrity statement
------------------------
The three MOLA PNG tiles in data/raw/ are colourised visual products.
Their RGB values DO NOT encode numerical elevation and are NOT used
in any calculation in this module.

No real Digital Elevation Model (DEM) is loaded. Therefore:
  - Slope data              → UNAVAILABLE
  - Terrain roughness       → UNAVAILABLE
  - Hazard classification   → UNAVAILABLE
  - Elevation profile       → UNAVAILABLE

What IS computed (from request coordinates):
  - Great-circle distance   → CALCULATED  (Haversine formula, Mars mean radius 3389.5 km)
  - Initial bearing         → CALCULATED  (standard geodetic formula)
  - Travel duration         → ESTIMATED   (distance ÷ stated nominal rover speed, flat terrain)

Priority mode behaviour
-----------------------
All priorities currently return the same direct great-circle estimate.
BALANCED and SAFETY do not have terrain or hazard data with which to
select alternate paths. SAFETY adds a survey reminder only.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Dict, Any

from backend.app.core.config import REGION_BOUNDS
from backend.app.core.route_models import (
    AlgorithmUsed,
    Coordinate,
    DataSourceInfo,
    DataSourceMode,
    PriorityModeExplanation,
    ProvenanceLabel,
    RoutePlanRequest,
    RoutePlanResponse,
    RoutePriority,
    RouteCoordinate,
    RouteSegment,
    RoverFeasibility,
    RoverType,
    TravelTimeEstimate,
    UnavailableField,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MARS_MEAN_RADIUS_KM: float = 3389.5  # IAU 2000 / IAG standard, used for Haversine

# Rover specs — illustrative operational parameters from NASA MSL/MER engineering
# documentation. These are NOT certified safety limits.
ROVER_SPECS: Dict[RoverType, Dict[str, Any]] = {
    RoverType.PCR: {
        "name":        "Pressurized Crew Rover (PCR-1)",
        "speed_kmh":   12.0,
        "range_km":    120.0,
    },
    RoverType.LUV: {
        "name":        "Lightweight Unpressurized Scout (LUV)",
        "speed_kmh":   18.0,
        "range_km":    45.0,
    },
    RoverType.HCH: {
        "name":        "Heavy Cargo & Habitat Hauler (HCH)",
        "speed_kmh":   6.0,
        "range_km":    80.0,
    },
}

PRIORITY_EXPLANATIONS: Dict[RoutePriority, Dict[str, str]] = {
    RoutePriority.DISTANCE: {
        "description": (
            "Direct route: a single great-circle (Haversine) line from start to destination "
            "with no intermediate POI waypoints. This is the geometric minimum-distance "
            "straight line between the two coordinates — it is NOT a terrain-aware "
            "shortest-path calculation. The name DISTANCE refers to minimising waypoint "
            "count (and therefore segment count), not to finding the shortest traversable "
            "surface path, which would require real terrain data."
        ),
        "effect_on_geometry": (
            "One segment from start to destination. Great-circle distance is the "
            "mathematical lower bound — actual surface traversal will be longer. "
            "No intermediate POIs are visited."
        ),
        "effect_on_waypoints": (
            "No intermediate POIs are included. The submitted start and destination "
            "coordinates are preserved exactly; no POI snapping is applied."
        ),
    },
    RoutePriority.BALANCED: {
        "description": (
            "Currently returns the same direct great-circle estimate as DISTANCE. "
            "No terrain or hazard data is available to select or validate waypoints."
        ),
        "effect_on_geometry": (
            "One direct great-circle segment is returned. This is geometric distance, "
            "not a traversable surface route."
        ),
        "effect_on_waypoints": (
            "No intermediate POIs are added. Submitted endpoint coordinates are preserved."
        ),
    },
    RoutePriority.SAFETY: {
        "description": (
            "Same routing geometry as BALANCED. Adds a planning reminder warning that "
            "each route leg should be independently surveyed before traversal. "
            "SAFETY does NOT change calculated distances, avoid hazards, or perform "
            "any terrain validation — that requires real DEM data, which is not loaded."
        ),
        "effect_on_geometry": (
            "Identical to BALANCED. No change to distance or bearing calculations."
        ),
        "effect_on_waypoints": (
            "Same direct geometry as the other priorities. An additional survey reminder "
            "is included in the warnings list."
        ),
    },
}


# ---------------------------------------------------------------------------
# Geodetic helpers
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance (km) using the Haversine formula.
    Coordinates: planetocentric latitude (°N), east longitude (°E).
    Mars mean radius = 3389.5 km (IAU standard).
    Provenance: CALCULATED.
    """
    r = MARS_MEAN_RADIUS_KM
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2.0 * r * math.asin(math.sqrt(min(a, 1.0)))  # clamp for float precision


def initial_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Initial bearing in degrees (0 = north, clockwise).
    Provenance: CALCULATED.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


# ---------------------------------------------------------------------------
# Coordinate validation
# ---------------------------------------------------------------------------

def _validate_in_region(coord: Coordinate, region_id: str, label: str) -> None:
    """Raise ValueError if coord is outside the region bounding box."""
    bounds = REGION_BOUNDS.get(region_id)
    if bounds is None:
        known = ", ".join(REGION_BOUNDS.keys())
        raise ValueError(f"Unknown region '{region_id}'. Known: {known}.")
    lat_min, lat_max = bounds["lat_min"], bounds["lat_max"]
    lon_min, lon_max = bounds["lon_min"], bounds["lon_max"]
    if not (lat_min <= coord.lat <= lat_max):
        raise ValueError(
            f"Invalid {label}: latitude {coord.lat}°N is outside region "
            f"'{region_id}' bounds ({lat_min}°N – {lat_max}°N)."
        )
    if not (lon_min <= coord.lon <= lon_max):
        raise ValueError(
            f"Invalid {label}: longitude {coord.lon}°E is outside region "
            f"'{region_id}' bounds ({lon_min}°E – {lon_max}°E)."
        )


# ---------------------------------------------------------------------------
# Segment builder
# ---------------------------------------------------------------------------

def _make_segment(
    index: int,
    from_poi: Dict[str, Any],
    to_poi: Dict[str, Any],
) -> RouteSegment:
    dist  = haversine_km(from_poi["lat"], from_poi["lon"], to_poi["lat"], to_poi["lon"])
    bear  = initial_bearing(from_poi["lat"], from_poi["lon"], to_poi["lat"], to_poi["lon"])
    return RouteSegment(
        index=index,
        from_label=from_poi["name"],
        to_label=to_poi["name"],
        from_coord=RouteCoordinate(
            lat=from_poi["lat"], lon=from_poi["lon"],
            label=from_poi["name"],
            is_poi=from_poi.get("_is_poi", False),
            provenance=ProvenanceLabel.CALCULATED,
        ),
        to_coord=RouteCoordinate(
            lat=to_poi["lat"], lon=to_poi["lon"],
            label=to_poi["name"],
            is_poi=to_poi.get("_is_poi", False),
            provenance=ProvenanceLabel.CALCULATED,
        ),
        distance_km=round(dist, 3),
        bearing_deg=round(bear, 2),
        distance_provenance=ProvenanceLabel.CALCULATED,
        bearing_provenance=ProvenanceLabel.CALCULATED,
    )


# ---------------------------------------------------------------------------
# Solver — direct great-circle line
# ---------------------------------------------------------------------------

def _coord_as_node(coord: Coordinate, label: str) -> Dict[str, Any]:
    return {"id": f"__{label}__", "name": label, "lat": coord.lat, "lon": coord.lon, "_is_poi": False}


def _solve_direct(
    request: RoutePlanRequest,
    warnings: List[str],
) -> Tuple[List[RouteCoordinate], List[RouteSegment]]:
    start_node = _coord_as_node(request.start, "Start")
    dest_node  = _coord_as_node(request.destination, "Destination")
    seg = _make_segment(0, start_node, dest_node)
    coords = [seg.from_coord, seg.to_coord]
    warnings.append(
        "A single great-circle leg is returned for every priority. "
        "No intermediate waypoints or terrain checks are applied. This geometric "
        "estimate does not represent a driveable surface path."
    )
    return coords, [seg]


# ---------------------------------------------------------------------------
# Travel time
# ---------------------------------------------------------------------------

def _travel_time(total_km: float, rover: RoverType) -> TravelTimeEstimate:
    spec = ROVER_SPECS[rover]
    speed = spec["speed_kmh"]
    duration_hrs = total_km / speed
    return TravelTimeEstimate(
        rover_name=spec["name"],
        rover_nominal_speed_kmh=speed,
        estimated_duration_min=round(duration_hrs * 60.0, 1),
        estimated_duration_hrs=round(duration_hrs, 2),
        provenance=ProvenanceLabel.ESTIMATED,
        assumption=(
            f"Assumes constant {speed} km/h nominal flat-terrain speed for {spec['name']}. "
            "No slope, soil cohesion, lighting-window, or crew-schedule corrections applied. "
            "Actual traversal time will be longer. [ESTIMATED]"
        ),
        supported=True,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def plan_route(request: RoutePlanRequest) -> RoutePlanResponse:
    """
    Compute a geometrically honest route between two Mars coordinates.

    All errors in validation raise ValueError; the caller (FastAPI endpoint)
    converts these to HTTP 422 responses.
    """
    warnings:    List[str] = []
    limitations: List[str] = [
        "No numerical Mars DEM (Digital Elevation Model) is loaded. MOLA colourised "
        "PNG tiles are visual products only — their RGB values do NOT encode "
        "elevation and are NOT read by this solver.",
        "Great-circle segments are straight-line geometric approximations. Actual "
        "surface paths are longer due to craters, scarps, and slope relief.",
        "Slope, terrain roughness, and hazard data are UNAVAILABLE. These fields "
        "are not populated with simulated numbers.",
        "Travel duration is ESTIMATED from nominal rover speed on flat terrain only.",
    ]

    # 1. Validate region and coordinates
    if request.region_id not in REGION_BOUNDS:
        known = ", ".join(REGION_BOUNDS.keys())
        raise ValueError(f"Unknown region '{request.region_id}'. Known: {known}.")

    _validate_in_region(request.start,       request.region_id, "start")
    _validate_in_region(request.destination, request.region_id, "destination")

    # 2. Data source metadata
    data_source = DataSourceInfo(
        mode=DataSourceMode.GEOMETRY_ONLY,
        description=(
            "Route computed from the submitted coordinates using great-circle "
            "(Haversine) geometry. POIs are not used to alter the endpoints."
        ),
        dem_available=False,
        mola_tiles_used=False,
        resolution_note=(
            "MOLA MEG256 tiles are present for visual display only "
            "(7680×7680 px per 30°×30° tile, 256 px/degree, ~231 m/px latitudinal). "
            "Pixel colour values are NOT read by the route solver."
        ),
    )

    # 3. Geometry-only solver: preserve the supplied endpoints for all priorities.
    coords, segments = _solve_direct(request, warnings)
    algorithm = AlgorithmUsed.HAVERSINE_DIRECT

    if request.priority == RoutePriority.SAFETY:
        warnings.append(
            "SAFETY priority selected. Routing geometry is identical to BALANCED. "
            "Before committing to any surface traversal, mission planners should "
            "independently survey each route leg using orbital imagery (HiRISE, CTX) "
            "and assess local terrain conditions. No terrain safety validation is "
            "performed by this system."
        )

    # 4. Totals
    total_distance_km = round(sum(s.distance_km for s in segments), 3)
    if total_distance_km < 1e-6:
        raise ValueError(
            "Computed route distance is effectively zero — "
            "start and destination may be identical."
        )

    # 5. Rover feasibility
    spec = ROVER_SPECS[request.rover_type]
    within_range = total_distance_km <= spec["range_km"]
    if not within_range:
        warnings.append(
            f"Route distance ({total_distance_km:.1f} km) exceeds the "
            f"{spec['name']} nominal range ({spec['range_km']} km). "
            "Mission planning should consider intermediate charging or resupply points."
        )

    feasibility = RoverFeasibility(
        rover_range_km=spec["range_km"],
        total_distance_km=total_distance_km,
        within_range=within_range,
        margin_km=round(spec["range_km"] - total_distance_km, 1),
        provenance=ProvenanceLabel.CALCULATED,
    )

    # 6. Priority explanation
    exp = PRIORITY_EXPLANATIONS[request.priority]
    priority_explanation = PriorityModeExplanation(
        mode=request.priority,
        description=exp["description"],
        effect_on_geometry=exp["effect_on_geometry"],
        effect_on_waypoints=exp["effect_on_waypoints"],
    )

    # 7. Unavailable fields — honest gaps
    terrain_cost = UnavailableField(
        provenance=ProvenanceLabel.UNAVAILABLE,
        reason=(
            "Terrain cost requires a numerical slope or surface-roughness model. "
            "No DEM is loaded. This field is not populated."
        ),
    )
    slope_data = UnavailableField(
        provenance=ProvenanceLabel.UNAVAILABLE,
        reason=(
            "Slope data requires a numerical elevation model (DEM). "
            "MOLA colourised tiles are visual products only. This field is not populated."
        ),
    )
    hazard_exposure = UnavailableField(
        provenance=ProvenanceLabel.UNAVAILABLE,
        reason=(
            "Hazard exposure requires a classified terrain or hazard raster. "
            "No such dataset is loaded. This field is not populated."
        ),
    )
    elevation_profile = UnavailableField(
        provenance=ProvenanceLabel.UNAVAILABLE,
        reason=(
            "Elevation profile requires numerical DEM data. "
            "No DEM is loaded. This field is not populated."
        ),
    )

    return RoutePlanResponse(
        coordinates=coords,
        segments=segments,
        total_distance_km=total_distance_km,
        feasibility=feasibility,
        travel_time=_travel_time(total_distance_km, request.rover_type),
        terrain_cost=terrain_cost,
        slope_data=slope_data,
        hazard_exposure=hazard_exposure,
        elevation_profile=elevation_profile,
        priority_explanation=priority_explanation,
        algorithm_used=algorithm,
        data_source=data_source,
        priority_used=request.priority,
        rover_type=request.rover_type,
        warnings=warnings,
        limitations=limitations,
    )
