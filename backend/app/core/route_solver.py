"""
ARES Route Planning Engine — core solver.

Data integrity statement
------------------------
When regional numerical DEMs (USGS HRSC/MOLA 200m blended products) are available
on disk, this solver evaluates real elevation profiles and physical surface slopes
along the route traversal path.

When numerical DEM files are absent, the solver falls back gracefully to a pure
geometric estimate:
  - Slope data              → UNAVAILABLE
  - Terrain roughness       → UNAVAILABLE
  - Hazard classification   → UNAVAILABLE
  - Elevation profile       → UNAVAILABLE

Submitted coordinates are strictly preserved as endpoints across all priorities.
No synthetic or fabricated elevation values are ever generated.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Optional, Dict, Any

from backend.app.core.config import REGION_BOUNDS, REGIONAL_HAZARDS
from backend.app.core.route_models import (
    AlgorithmUsed,
    Coordinate,
    DataSourceInfo,
    DataSourceMode,
    ElevationProfileData,
    ElevationSample,
    PriorityModeExplanation,
    ProvenanceLabel,
    RoutePlanRequest,
    RoutePlanResponse,
    RoutePriority,
    RouteCoordinate,
    RouteSegment,
    RoverFeasibility,
    RoverType,
    SlopeAnalysisData,
    TerrainCostData,
    TravelTimeEstimate,
    UnavailableField,
)
from backend.app.core.terrain_pipeline import terrain_pipeline

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MARS_MEAN_RADIUS_KM: float = 3389.5  # IAU 2000 / IAG standard, used for Haversine
POI_SNAP_THRESHOLD_DEG: float = 0.05

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
            "Direct route: a single great-circle (Haversine) line from start to destination. "
            "Preserves the submitted coordinates and calculates the geometric direct distance."
        ),
        "effect_on_geometry": (
            "One direct segment between the submitted start and destination coordinates. "
            "Endpoints are preserved exactly."
        ),
        "effect_on_waypoints": "No intermediate waypoints are added.",
    },
    RoutePriority.BALANCED: {
        "description": (
            "Balanced operational route: computes direct great-circle geometry between the "
            "submitted coordinates while auditing terrain elevation and gradient along the path."
        ),
        "effect_on_geometry": (
            "Direct traversal segment preserving submitted coordinates. "
            "When DEM is loaded, evaluates topographic relief and slope metrics."
        ),
        "effect_on_waypoints": "Endpoints preserved; waypoints surveyed against regional topography.",
    },
    RoutePriority.SAFETY: {
        "description": (
            "Safety-oriented route evaluation: evaluates direct traversal geometry with extra "
            "advisory screening for steep terrain gradients (>15°) and reminders for orbital survey."
        ),
        "effect_on_geometry": "Direct traversal segment preserving submitted coordinates.",
        "effect_on_waypoints": (
            "Endpoints preserved. Additional warnings issued if steep terrain is detected along "
            "the path or when orbital verification is advised."
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
    return 2.0 * r * math.asin(math.sqrt(min(a, 1.0)))


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

def _coord_as_node(coord: Coordinate, label: str) -> Dict[str, Any]:
    return {"id": f"__{label}__", "name": label, "lat": coord.lat, "lon": coord.lon, "_is_poi": False}


def _make_segment(
    index: int,
    from_node: Dict[str, Any],
    to_node: Dict[str, Any],
) -> RouteSegment:
    dist = haversine_km(from_node["lat"], from_node["lon"], to_node["lat"], to_node["lon"])
    bear = initial_bearing(from_node["lat"], from_node["lon"], to_node["lat"], to_node["lon"])
    return RouteSegment(
        index=index,
        from_label=from_node["name"],
        to_label=to_node["name"],
        from_coord=RouteCoordinate(
            lat=from_node["lat"], lon=from_node["lon"],
            label=from_node["name"],
            is_poi=from_node.get("_is_poi", False),
            provenance=ProvenanceLabel.CALCULATED,
        ),
        to_coord=RouteCoordinate(
            lat=to_node["lat"], lon=to_node["lon"],
            label=to_node["name"],
            is_poi=to_node.get("_is_poi", False),
            provenance=ProvenanceLabel.CALCULATED,
        ),
        distance_km=round(dist, 3),
        bearing_deg=round(bear, 2),
        distance_provenance=ProvenanceLabel.CALCULATED,
        bearing_provenance=ProvenanceLabel.CALCULATED,
    )


def _solve_direct(
    request: RoutePlanRequest,
    warnings: List[str],
) -> Tuple[List[RouteCoordinate], List[RouteSegment]]:
    start_node = _coord_as_node(request.start, "Start")
    dest_node  = _coord_as_node(request.destination, "Destination")
    seg = _make_segment(0, start_node, dest_node)
    coords = [seg.from_coord, seg.to_coord]
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
            "No crew-schedule corrections applied. Actual traversal time may vary with terrain."
        ),
        supported=True,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def plan_route(request: RoutePlanRequest) -> RoutePlanResponse:
    """
    Compute a geometrically honest, terrain-aware route between two Mars coordinates.
    Preserves submitted endpoints and evaluates physical elevation / slope when DEM is present.
    """
    warnings:    List[str] = []
    limitations: List[str] = []

    # 1. Validate region and coordinates
    if request.region_id not in REGION_BOUNDS:
        known = ", ".join(REGION_BOUNDS.keys())
        raise ValueError(f"Unknown region '{request.region_id}'. Known: {known}.")

    _validate_in_region(request.start,       request.region_id, "start")
    _validate_in_region(request.destination, request.region_id, "destination")

    # 2. Geometry-only direct solver (preserves user-submitted coordinates)
    coords, segments = _solve_direct(request, warnings)
    algorithm = AlgorithmUsed.HAVERSINE_DIRECT

    total_distance_km = round(sum(s.distance_km for s in segments), 3)
    if total_distance_km < 1e-6:
        raise ValueError("Computed route distance is effectively zero — start and destination are identical.")

    # 3. Rover feasibility (one-way and return-to-base)
    spec = ROVER_SPECS[request.rover_type]
    within_range = total_distance_km <= spec["range_km"]
    if not within_range:
        warnings.append(
            f"Route distance ({total_distance_km:.1f} km) exceeds the "
            f"{spec['name']} nominal range ({spec['range_km']} km). "
            "Mission planning should consider intermediate charging or resupply points."
        )

    return_trip_km = round(total_distance_km * 2.0, 3)
    return_feasible = return_trip_km <= spec["range_km"]
    return_margin_km = round(spec["range_km"] - return_trip_km, 1)

    if not return_feasible and within_range:
        warnings.append(
            f"Return-to-base alert: Round-trip traversal ({return_trip_km:.1f} km) exceeds "
            f"{spec['name']} range ({spec['range_km']:.0f} km) by {abs(return_margin_km):.1f} km. "
            "A return mission requires field recharge or prepositioned assets."
        )

    feasibility = RoverFeasibility(
        rover_range_km=spec["range_km"],
        total_distance_km=total_distance_km,
        within_range=within_range,
        margin_km=round(spec["range_km"] - total_distance_km, 1),
        return_trip_km=return_trip_km,
        return_feasible=return_feasible,
        return_margin_km=return_margin_km,
        provenance=ProvenanceLabel.CALCULATED,
    )

    # 3b. Hazard proximity check
    reg_hazards = REGIONAL_HAZARDS.get(request.region_id, [])
    for hz in reg_hazards:
        min_d = min(
            haversine_km(
                request.start.lat + t * (request.destination.lat - request.start.lat),
                request.start.lon + t * (request.destination.lon - request.start.lon),
                hz["lat"],
                hz["lon"]
            )
            for t in [i / 10.0 for i in range(11)]
        )
        if min_d <= 8.0:
            risk_desc = hz.get("slope_risk", hz.get("slopeRisk", "Hazardous surface"))
            warnings.append(
                f"Hazard proximity notice: route passes within {min_d:.1f} km of {hz['name']} "
                f"({hz['type']}). Risk: {risk_desc}."
            )

    # 4. Check DEM availability in local terrain pipeline
    dem_status = terrain_pipeline.get_dem_status(request.region_id)
    use_dem = getattr(request, "use_dem", True)
    dem_available = dem_status.is_available and use_dem

    if dem_available:
        # Sample elevation and slope along the direct route path
        # Number of samples based on distance (minimum 15, maximum 50)
        num_samples = max(15, min(50, int(total_distance_km / 0.5) + 1))
        elevation_samples: List[ElevationSample] = []
        slopes: List[float] = []

        d_lat = request.destination.lat - request.start.lat
        d_lon = request.destination.lon - request.start.lon

        for i in range(num_samples):
            t = i / float(num_samples - 1)
            cur_lat = request.start.lat + t * d_lat
            cur_lon = request.start.lon + t * d_lon
            cur_dist = round(t * total_distance_km, 3)

            elev = terrain_pipeline.get_elevation_at_point(request.region_id, cur_lat, cur_lon)
            slope = terrain_pipeline.get_slope_at_point(request.region_id, cur_lat, cur_lon)

            if elev is not None:
                elevation_samples.append(ElevationSample(
                    distance_km=cur_dist,
                    lat=round(cur_lat, 5),
                    lon=round(cur_lon, 5),
                    elevation_m=round(elev, 2),
                ))

            if slope is not None and not math.isnan(slope):
                slopes.append(slope)

        if elevation_samples:
            elev_values = [s.elevation_m for s in elevation_samples]
            min_el = min(elev_values)
            max_el = max(elev_values)
            start_el = elev_values[0]
            end_el = elev_values[-1]
            gain = sum(max(0.0, elev_values[j + 1] - elev_values[j]) for j in range(len(elev_values) - 1))

            elevation_profile = ElevationProfileData(
                supported=True,
                provenance=ProvenanceLabel.CALCULATED,
                min_elevation_m=round(min_el, 2),
                max_elevation_m=round(max_el, 2),
                start_elevation_m=round(start_el, 2),
                end_elevation_m=round(end_el, 2),
                elevation_change_m=round(end_el - start_el, 2),
                elevation_gain_m=round(gain, 2),
                samples=elevation_samples,
            )
        else:
            elevation_profile = UnavailableField(
                provenance=ProvenanceLabel.UNAVAILABLE,
                reason="Coordinates fell outside the verified DEM boundaries or hit NoData.",
            )

        if slopes:
            min_sl = min(slopes)
            max_sl = max(slopes)
            mean_sl = sum(slopes) / len(slopes)
            steep_detected = max_sl > 15.0

            slope_data = SlopeAnalysisData(
                supported=True,
                provenance=ProvenanceLabel.CALCULATED,
                min_slope_deg=round(min_sl, 2),
                max_slope_deg=round(max_sl, 2),
                mean_slope_deg=round(mean_sl, 2),
                steep_slopes_detected=steep_detected,
                max_recommended_slope_deg=15.0,
            )

            if steep_detected:
                warnings.append(
                    f"Steep terrain alert: maximum measured slope along route is {max_sl:.1f}° "
                    "(operational threshold: 15.0°). Rover traversing this section may experience "
                    "slip or require autonomous hazard avoidance."
                )

            cost_idx = round(1.0 + (mean_sl / 15.0) * 0.5, 3)
            terrain_cost = TerrainCostData(
                supported=True,
                provenance=ProvenanceLabel.CALCULATED,
                cost_index=cost_idx,
                slope_penalty=round(mean_sl * 0.05, 3),
            )
        else:
            slope_data = UnavailableField(
                provenance=ProvenanceLabel.UNAVAILABLE,
                reason="Slope analysis could not be computed; coordinates fell outside DEM bounds.",
            )
            terrain_cost = UnavailableField(
                provenance=ProvenanceLabel.UNAVAILABLE,
                reason="Terrain cost requires numerical slope grid.",
            )

        data_source = DataSourceInfo(
            mode=DataSourceMode.MEASURED,
            description=(
                "Route evaluated against USGS HRSC/MOLA 200m numerical Digital Elevation Model (DEM). "
                "Elevation profile and slope angles are calculated from validated single-band elevation data."
            ),
            dem_available=True,
            mola_tiles_used=True,
            resolution_note="Regional 200 m/px numerical DEM grid (USGS HRSC/MOLA blended product, IAU 2000 Areoid datum).",
            snap_threshold_deg=POI_SNAP_THRESHOLD_DEG,
        )

        limitations.append(
            "Elevation and slope are evaluated from the 200 m/px regional DEM. "
            "Micro-topographical hazards (boulders <1m, small sand ripples) below raster resolution are not detected."
        )

    else:
        # Fallback to geometry-only unavailable fields
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
            snap_threshold_deg=POI_SNAP_THRESHOLD_DEG,
        )
        terrain_cost = UnavailableField(
            provenance=ProvenanceLabel.UNAVAILABLE,
            reason="Terrain cost requires a numerical slope or surface-roughness model. No DEM is loaded.",
        )
        slope_data = UnavailableField(
            provenance=ProvenanceLabel.UNAVAILABLE,
            reason="Slope data requires a numerical elevation model (DEM). No DEM is loaded.",
        )
        elevation_profile = UnavailableField(
            provenance=ProvenanceLabel.UNAVAILABLE,
            reason="Elevation profile requires numerical DEM data. No DEM is loaded.",
        )
        limitations.extend([
            "No numerical Mars DEM is loaded for this run. Slope, elevation profile, and terrain cost are UNAVAILABLE.",
            "Great-circle segments are straight-line geometric approximations. Actual surface paths are longer due to topography.",
        ])

    # Hazard classification raster is not currently loaded in either mode
    hazard_exposure = UnavailableField(
        provenance=ProvenanceLabel.UNAVAILABLE,
        reason=(
            "Hazard exposure requires a classified terrain or hazard raster. "
            "No such dataset is loaded. This field is not populated."
        ),
    )

    # 5. Priority handling
    if request.priority == RoutePriority.SAFETY:
        warnings.append(
            "SAFETY priority selected. Routing geometry is direct between endpoints. "
            "Before committing to any surface traversal, mission planners should "
            "independently survey each route leg using orbital imagery (HiRISE, CTX) "
            "and assess local terrain conditions. No terrain safety validation is performed by this system."
        )

    exp = PRIORITY_EXPLANATIONS[request.priority]
    priority_explanation = PriorityModeExplanation(
        mode=request.priority,
        description=exp["description"],
        effect_on_geometry=exp["effect_on_geometry"],
        effect_on_waypoints=exp["effect_on_waypoints"],
    )

    limitations.append("Travel duration is ESTIMATED from nominal rover speed on flat terrain only.")

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
