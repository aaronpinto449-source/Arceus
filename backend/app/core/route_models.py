"""
ARES Route Planning — Pydantic request/response models.

Coordinate convention: Planetocentric latitude (°N), East longitude (°E).
All derived geometry uses the IAU mean Mars radius (3389.5 km).

Data provenance labels used throughout this module:
  CALCULATED  — derived from verified coordinates by exact mathematics
  ESTIMATED   — computed from an explicitly stated assumption
  UNAVAILABLE — cannot be provided; required data does not exist
  SIMULATED   — illustrative placeholder; not derived from real data
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class RoutePriority(str, Enum):
    SAFETY   = "SAFETY"
    DISTANCE = "DISTANCE"
    BALANCED = "BALANCED"


class RoverType(str, Enum):
    PCR = "PCR"   # Pressurized Crew Rover
    LUV = "LUV"   # Lightweight Unpressurized Scout
    HCH = "HCH"   # Heavy Cargo & Habitat Hauler


class AlgorithmUsed(str, Enum):
    DIJKSTRA_POI_GRAPH  = "DIJKSTRA-POI-GRAPH"   # Dijkstra over verified POI waypoint graph
    HAVERSINE_DIRECT    = "HAVERSINE-DIRECT"       # Great-circle straight line, no intermediate waypoints


class DataSourceMode(str, Enum):
    GEOMETRY_ONLY = "GEOMETRY_ONLY"   # Great-circle distance from verified coordinates; no terrain data
    MEASURED      = "MEASURED"         # Reserved for future real DEM integration


class ProvenanceLabel(str, Enum):
    CALCULATED  = "CALCULATED"   # Exact mathematics from verified input coordinates
    ESTIMATED   = "ESTIMATED"    # Computed from a stated assumption (e.g. nominal rover speed)
    UNAVAILABLE = "UNAVAILABLE"  # Required data does not exist in this system
    SIMULATED   = "SIMULATED"    # Illustrative placeholder, not derived from real data


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0,   description="Planetocentric latitude (°N)")
    lon: float = Field(..., ge=-180.0, le=360.0, description="East longitude (°E)")


class RoutePlanRequest(BaseModel):
    region_id:   str           = Field(...,                  description="Mars region ID (e.g. 'gale-crater')")
    start:       Coordinate    = Field(...,                  description="Departure coordinate")
    destination: Coordinate    = Field(...,                  description="Arrival coordinate")
    rover_type:  RoverType     = Field(RoverType.PCR,        description="Surface vehicle type")
    priority:    RoutePriority = Field(RoutePriority.BALANCED, description="Traversal planning preference")

    @model_validator(mode="after")
    def start_and_dest_differ(self) -> "RoutePlanRequest":
        if (abs(self.start.lat - self.destination.lat) < 1e-7 and
                abs(self.start.lon - self.destination.lon) < 1e-7):
            raise ValueError("Start and destination coordinates must differ.")
        return self


# ---------------------------------------------------------------------------
# Response components
# ---------------------------------------------------------------------------

class RouteCoordinate(BaseModel):
    lat:        float          = Field(..., description="Planetocentric latitude (°N)")
    lon:        float          = Field(..., description="East longitude (°E)")
    label:      Optional[str]  = Field(None, description="Waypoint name")
    is_poi:     bool           = Field(False, description="True if this is a verified NASA POI")
    provenance: ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)


class RouteSegment(BaseModel):
    index:        int             = Field(..., description="Zero-based segment index")
    from_label:   str
    to_label:     str
    from_coord:   RouteCoordinate
    to_coord:     RouteCoordinate
    distance_km:  float           = Field(..., description="[CALCULATED] Great-circle segment distance (km)")
    bearing_deg:  float           = Field(..., description="[CALCULATED] Initial bearing (°, 0=N, clockwise)")
    distance_provenance: ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    bearing_provenance:  ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    # Fix #3 — per-segment obstacle disclaimer
    geometry_caveat: str = Field(
        default=(
            "This segment is a straight great-circle line between two coordinates. "
            "It has not been checked against actual surface terrain, obstacles, or "
            "impassable features. The actual traversal path will be longer than the "
            "calculated great-circle distance."
        ),
        description=(
            "Reminder that this segment is a geometric approximation only. "
            "It does not account for craters, scarps, lava flows, or any other "
            "surface feature between the two endpoints."
        ),
    )


class TravelTimeEstimate(BaseModel):
    rover_name:              str
    rover_nominal_speed_kmh: float
    estimated_duration_min:  float = Field(..., description="[ESTIMATED] Duration at nominal speed")
    estimated_duration_hrs:  float
    provenance:              ProvenanceLabel = Field(ProvenanceLabel.ESTIMATED)
    assumption:              str   = Field(..., description="Explicit statement of what is assumed")
    supported:               bool  = True


class UnavailableField(BaseModel):
    """Represents a data field that cannot be populated due to missing source data."""
    supported: bool  = False
    provenance: ProvenanceLabel = Field(ProvenanceLabel.UNAVAILABLE)
    reason:    str


class PriorityModeExplanation(BaseModel):
    mode:        RoutePriority
    description: str
    effect_on_geometry: str
    effect_on_waypoints: str


class DataSourceInfo(BaseModel):
    mode:            DataSourceMode
    description:     str
    dem_available:   bool  = False
    mola_tiles_used: bool  = True
    resolution_note: str
    coordinate_system: str = "IAU Planetocentric Latitude (°N), East Longitude (°E)"
    mars_radius_km:    float = 3389.5
    # Fix #5 — expose snap threshold in API response
    snap_threshold_deg: float = Field(
        default=0.05,
        description=(
            "POI coordinate snap tolerance in degrees. "
            "If a supplied start or destination coordinate lies within this angular "
            "distance of a verified POI, it is snapped to that POI and a warning is issued. "
            "0.05° ≈ 3 km at the Mars equatorial radius."
        ),
    )
    snap_threshold_km_approx: str = Field(
        default="~3 km (computed at Mars equatorial radius 3396.2 km)",
        description="Human-readable approximate snap threshold distance.",
    )


class RoverFeasibility(BaseModel):
    rover_range_km:     float
    total_distance_km:  float
    within_range:       bool
    margin_km:          float
    provenance:         ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    # Fix #2 — rover range caveat
    range_caveat: str = Field(
        default=(
            "Vehicle range figures are illustrative planning assumptions, not verified "
            "engineering specifications. Actual range depends on terrain gradient, "
            "power consumption rate, crew schedule, thermal conditions, and mission "
            "constraints. These values should not be used as certified operational limits."
        ),
        description=(
            "Disclaimer that rover range_km is an illustrative figure, not a certified specification."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class RoutePlanResponse(BaseModel):
    # Route geometry  [CALCULATED]
    coordinates:          List[RouteCoordinate]
    segments:             List[RouteSegment]
    total_distance_km:    float = Field(..., description="[CALCULATED] Sum of great-circle segment distances (km)")

    # Rover feasibility  [CALCULATED]
    feasibility:          RoverFeasibility

    # Travel time  [ESTIMATED]
    travel_time:          Optional[TravelTimeEstimate] = None

    # Unavailable fields — honest gaps, not fake numbers
    terrain_cost:         UnavailableField
    slope_data:           UnavailableField
    hazard_exposure:      UnavailableField
    elevation_profile:    UnavailableField

    # Priority mode explanation
    priority_explanation: PriorityModeExplanation

    # Metadata
    algorithm_used:   AlgorithmUsed
    data_source:      DataSourceInfo
    priority_used:    RoutePriority
    rover_type:       RoverType

    # Transparency
    warnings:     List[str]
    limitations:  List[str]

    scientific_disclaimer: str = (
        "Route segments are great-circle (straight-line) geometric approximations "
        "between verified waypoint coordinates on a spherical Mars model "
        "(IAU mean radius 3389.5 km). Actual surface paths are longer due to "
        "topography. No terrain, slope, elevation, or hazard data is used. "
        "This output is a geometric planning aid and must NOT be used for "
        "real astronaut navigation decisions."
    )
