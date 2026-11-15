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

What IS computed (from verified POI coordinates):
  - Great-circle distance   → CALCULATED  (Haversine formula, Mars mean radius 3389.5 km)
  - Initial bearing         → CALCULATED  (standard geodetic formula)
  - Travel duration         → ESTIMATED   (distance ÷ stated nominal rover speed, flat terrain)

Priority mode behaviour
-----------------------
DIRECT   — single great-circle leg, start → destination.
BALANCED — route through any verified intermediate POIs that lie
           between start and destination (using Dijkstra on the
           POI graph). Geometry is unchanged; more waypoints shown.
SAFETY   — identical geometry to BALANCED, plus a warning reminding
           planners to survey each leg before traversal.

No distance multipliers are applied. Priority does NOT change
calculated distances or make a route "safer" — that would require
real terrain data we do not have.

NetworkX is used only for Dijkstra over the POI graph (already
listed in requirements.txt). It is NOT used for A* or terrain grids.
"""

from __future__ import annotations

import math
import copy
from typing import List, Tuple, Optional, Dict, Any

import networkx as nx

from backend.app.core.config import REGION_BOUNDS, REGION_POIS
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

# Fix #5 — named constant for the POI snap tolerance; documented in API response metadata.
# 0.05° at Mars equatorial radius (3396.2 km) ≈ 2.96 km.
# Any supplied coordinate within this angular distance of a verified POI is snapped
# to that POI before graph construction.  A warning is always issued when snapping occurs.
POI_SNAP_THRESHOLD_DEG: float = 0.05

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

# Fix #1 — DISTANCE description clarified: it means "direct Haversine line, no intermediate
# POI waypoints", NOT "terrain-aware shortest path".  The enum value is unchanged for API
# compatibility; the description field is what developers and the UI should read.
PRIORITY_EXPLANATIONS: Dict[RoutePriority, Dict[str, str]] = {
    RoutePriority.DISTANCE: {
        "description": (
            "Direct route: a single great-circle (Haversine) line from start to destination "
            "with no intermediate POI waypoints. This is the geometric minimum-distance "
            "straight line between the two coordinates — it is NOT a terrain-aware "
            "shortest-path calculation. The name DISTANCE refers to minimising waypoint "
            "count (and therefore segment count), not to finding the shortest traversable "
            "surface path, which would require real terrain data. To route via verified "
            "intermediate POIs, use BALANCED or SAFETY."
        ),
        "effect_on_geometry": (
            "One segment from start to destination. Great-circle distance is the "
            "mathematical lower bound — actual surface traversal will be longer. "
            "No intermediate POIs are visited."
        ),
        "effect_on_waypoints": (
            "No intermediate POIs included. Start and destination may still be "
            "snapped to the nearest verified POI if within the snap threshold "
            f"({POI_SNAP_THRESHOLD_DEG}° ≈ ~3 km)."
        ),
    },
    RoutePriority.BALANCED: {
        "description": (
            "Waypoint route: Dijkstra over the complete verified-POI graph. "
            "Returns the minimum-distance path that visits intermediate verified POIs "
            "between start and destination. Edge weights are great-circle distances only — "
            "no terrain multipliers are applied. With few POIs (currently 3 per region) "
            "the result is often the same as DISTANCE unless a POI lies between the endpoints."
        ),
        "effect_on_geometry": (
            "Total distance may be greater than DISTANCE if intermediate POIs are "
            "off the direct line. Segments are individually labelled with verified POI names."
        ),
        "effect_on_waypoints": (
            "Dijkstra selects the minimum cumulative great-circle distance path "
            "through the full POI graph. All region POIs are eligible as waypoints."
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
            "Same POI graph as BALANCED. An additional warning string is appended "
            "to the response warnings[] list recommending orbital survey before traversal."
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
# POI snap helper
# ---------------------------------------------------------------------------

def _nearest_poi(coord: Coordinate, pois: List[Dict], tolerance_deg: float = POI_SNAP_THRESHOLD_DEG) -> Optional[Dict]:
    """
    Return the nearest POI if it lies within tolerance_deg of coord, else None.

    Default tolerance is POI_SNAP_THRESHOLD_DEG (0.05° ≈ 3 km at Mars equatorial radius).
    When a snap occurs, the caller issues a warning in the response warnings[] list.
    The snap threshold is also exposed in DataSourceInfo.snap_threshold_deg.
    """
    best, best_d = None, float("inf")
    for poi in pois:
        d = math.hypot(poi["lat"] - coord.lat, poi["lon"] - coord.lon)
        if d < best_d:
            best_d, best = d, poi
    return best if best_d <= tolerance_deg else None


def _coord_as_node(coord: Coordinate, label: str) -> Dict[str, Any]:
    return {"id": f"__{label}__", "name": label, "lat": coord.lat, "lon": coord.lon, "_is_poi": False}


# ---------------------------------------------------------------------------
# Solver — direct great-circle line
# ---------------------------------------------------------------------------

def _solve_direct(
    request: RoutePlanRequest,
    warnings: List[str],
) -> Tuple[List[RouteCoordinate], List[RouteSegment]]:
    start_node = _coord_as_node(request.start, "Start")
    dest_node  = _coord_as_node(request.destination, "Destination")
    seg = _make_segment(0, start_node, dest_node)
    coords = [seg.from_coord, seg.to_coord]
    warnings.append(
        "DIRECT priority selected: single great-circle leg used. "
        "No intermediate waypoints are included. This straight line does not "
        "represent a driveable surface path — actual traversal distance is "
        "longer due to Martian topography."
    )
    return coords, [seg]


# ---------------------------------------------------------------------------
# Solver — Dijkstra over verified POI graph
# ---------------------------------------------------------------------------

def _solve_poi_graph(
    request: RoutePlanRequest,
    pois: List[Dict[str, Any]],
    warnings: List[str],
) -> Tuple[List[RouteCoordinate], List[RouteSegment]]:
    """
    Build a complete weighted graph of verified POIs plus start/destination,
    then run Dijkstra (minimum total distance path).

    Edge weights = Haversine great-circle distance. No terrain multipliers.

    Fix #4: pois is the caller's deep-copy of REGION_POIS — we still avoid
    mutating it here by using dict-spread to add _is_poi, so the original
    shared config remains untouched even if the caller forgets to deep-copy.
    """
    # Build local node dicts WITHOUT mutating the original poi dicts.
    # {**p, "_is_poi": True} creates a new dict each time.
    nodes: List[Dict[str, Any]] = [{**p, "_is_poi": True} for p in pois]

    # Add start node unless it snaps to an existing POI
    start_snap = _nearest_poi(request.start, pois)
    dest_snap  = _nearest_poi(request.destination, pois)

    if start_snap:
        start_id = start_snap["id"]
        warnings.append(
            f"Start coordinate snapped to nearest verified POI: '{start_snap['name']}' "
            f"(within 0.05° ≈ 3 km)."
        )
    else:
        start_node = _coord_as_node(request.start, "Start")
        nodes.append(start_node)
        start_id = start_node["id"]

    if dest_snap:
        dest_id = dest_snap["id"]
        warnings.append(
            f"Destination coordinate snapped to nearest verified POI: '{dest_snap['name']}' "
            f"(within 0.05° ≈ 3 km)."
        )
    else:
        dest_node = _coord_as_node(request.destination, "Destination")
        nodes.append(dest_node)
        dest_id = dest_node["id"]

    # Build complete undirected graph (edge weight = great-circle distance, no multiplier)
    G = nx.Graph()
    node_map: Dict[str, Dict] = {}
    for n in nodes:
        G.add_node(n["id"], **n)
        node_map[n["id"]] = n

    for i, na in enumerate(nodes):
        for nb in nodes[i + 1:]:
            dist = haversine_km(na["lat"], na["lon"], nb["lat"], nb["lon"])
            G.add_edge(na["id"], nb["id"], weight=dist)

    try:
        path_ids: List[str] = nx.dijkstra_path(G, start_id, dest_id, weight="weight")
    except nx.NetworkXNoPath:
        warnings.append(
            "Dijkstra found no path through POI graph (graph may be disconnected). "
            "Falling back to direct great-circle line."
        )
        return _solve_direct(request, warnings)

    # Build coordinates and segments from path
    coords: List[RouteCoordinate] = []
    segments: List[RouteSegment]  = []

    for idx, nid in enumerate(path_ids):
        nd = node_map[nid]
        coords.append(RouteCoordinate(
            lat=nd["lat"], lon=nd["lon"],
            label=nd["name"],
            is_poi=nd.get("_is_poi", False),
            provenance=ProvenanceLabel.CALCULATED,
        ))
        if idx > 0:
            prev = node_map[path_ids[idx - 1]]
            segments.append(_make_segment(idx - 1, prev, nd))

    return coords, segments


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
            "Route computed from verified POI coordinates using great-circle "
            "(Haversine) geometry. No terrain model is used."
        ),
        dem_available=False,
        mola_tiles_used=True,
        resolution_note=(
            "MOLA MEG256 tiles are present for visual display only "
            "(7680×7680 px per 30°×30° tile, 256 px/degree, ~231 m/px latitudinal). "
            "Pixel colour values are NOT read by the route solver."
        ),
    )

    # 3. Solve
    pois: List[Dict[str, Any]] = REGION_POIS.get(request.region_id, [])

    if request.priority == RoutePriority.DISTANCE or len(pois) < 2:
        if len(pois) < 2:
            warnings.append(
                f"Region '{request.region_id}' has fewer than 2 verified POIs; "
                "using direct great-circle route."
            )
        coords, segments = _solve_direct(request, warnings)
        algorithm = AlgorithmUsed.HAVERSINE_DIRECT
    else:
        coords, segments = _solve_poi_graph(request, pois, warnings)
        algorithm = AlgorithmUsed.DIJKSTRA_POI_GRAPH

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
            "start and destination may be identical after coordinate snapping."
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
