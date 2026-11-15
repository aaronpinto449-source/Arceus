"""
ARES Route Planning — Pydantic request/response models.

Coordinate convention: Planetocentric latitude (°N), East longitude (°E).
All derived geometry uses the IAU mean Mars radius (3389.5 km).

Data provenance labels used throughout this module:
  CALCULATED  — derived from verified coordinates / DEM by exact mathematics
  ESTIMATED   — computed from an explicitly stated assumption
  UNAVAILABLE — cannot be provided; required data does not exist
  SIMULATED   — illustrative placeholder; not derived from real data
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union
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
    HAVERSINE_DIRECT    = "HAVERSINE-DIRECT"   # Direct great-circle geometry; endpoints preserved
    DIJKSTRA_POI_GRAPH  = "DIJKSTRA-POI-GRAPH" # Dijkstra over verified POI waypoint graph


class DataSourceMode(str, Enum):
    GEOMETRY_ONLY = "GEOMETRY_ONLY"   # Great-circle distance from verified coordinates; no DEM used
    MEASURED      = "MEASURED"         # Physical terrain measured from verified numerical DEM


class ProvenanceLabel(str, Enum):
    CALCULATED  = "CALCULATED"   # Exact mathematics from verified input coordinates or DEM
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
    use_dem:     bool          = Field(True,                 description="If True and numerical DEM is present, evaluates elevation and slope")

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
    lat:        float           = Field(..., description="Planetocentric latitude (°N)")
    lon:        float           = Field(..., description="East longitude (°E)")
    label:      Optional[str]   = Field(None, description="Waypoint name")
    is_poi:     bool            = Field(False, description="True if this is a verified NASA POI")
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
    geometry_caveat: str = Field(
        default=(
            "This segment is a straight great-circle line between two coordinates. "
            "The actual traversal path will be longer than the calculated great-circle distance "
            "due to surface obstacles and topography."
        ),
        description="Caveat detailing geometric approximation vs actual traversal path.",
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
    supported:  bool            = False
    provenance: ProvenanceLabel = Field(ProvenanceLabel.UNAVAILABLE)
    reason:     str


class ElevationSample(BaseModel):
    distance_km: float = Field(..., description="Distance from start along route (km)")
    lat:         float = Field(..., description="Sample latitude (°N)")
    lon:         float = Field(..., description="Sample longitude (°E)")
    elevation_m: float = Field(..., description="Elevation relative to MOLA areoid (m)")


class ElevationProfileData(BaseModel):
    supported:          bool            = True
    provenance:         ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    min_elevation_m:    float
    max_elevation_m:    float
    start_elevation_m:  float
    end_elevation_m:    float
    elevation_change_m: float
    elevation_gain_m:   float
    samples:            List[ElevationSample] = Field(default_factory=list)


class SlopeAnalysisData(BaseModel):
    supported:                 bool            = True
    provenance:                ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    min_slope_deg:             float
    max_slope_deg:             float
    mean_slope_deg:            float
    steep_slopes_detected:     bool  = False
    max_recommended_slope_deg: float = 15.0


class TerrainCostData(BaseModel):
    supported:     bool            = True
    provenance:    ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    cost_index:    float
    slope_penalty: float


class PriorityModeExplanation(BaseModel):
    mode:                RoutePriority
    description:         str
    effect_on_geometry:  str
    effect_on_waypoints: str


class DataSourceInfo(BaseModel):
    mode:                     DataSourceMode
    description:              str
    dem_available:            bool  = False
    mola_tiles_used:          bool  = False
    resolution_note:          str
    coordinate_system:        str   = "IAU Planetocentric Latitude (°N), East Longitude (°E)"
    mars_radius_km:           float = 3389.5
    snap_threshold_deg:       Optional[float] = 0.05
    snap_threshold_km_approx: Optional[str]   = "~3 km (computed at Mars equatorial radius 3396.2 km)"


class RoverFeasibility(BaseModel):
    rover_range_km:     float
    total_distance_km:  float
    within_range:       bool
    margin_km:          float
    return_trip_km:     float = Field(default=0.0, description="[CALCULATED] Round-trip traversal distance (km)")
    return_feasible:    bool  = Field(default=False, description="[CALCULATED] Whether round-trip is within vehicle nominal range")
    return_margin_km:   float = Field(default=0.0, description="[CALCULATED] Range margin for return trip (km)")
    provenance:         ProvenanceLabel = Field(ProvenanceLabel.CALCULATED)
    range_caveat: str = Field(
        default=(
            "Vehicle range figures are illustrative planning assumptions, not verified "
            "engineering specifications. Actual range depends on terrain gradient, "
            "power consumption rate, crew schedule, thermal conditions, and mission "
            "constraints. These values should not be used as certified operational limits."
        ),
        description="Disclaimer that rover range_km is an illustrative figure, not a certified specification.",
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

    # Terrain fields — populated from DEM when available, otherwise UnavailableField
    terrain_cost:         Union[TerrainCostData, UnavailableField]
    slope_data:           Union[SlopeAnalysisData, UnavailableField]
    hazard_exposure:      UnavailableField
    elevation_profile:    Union[ElevationProfileData, UnavailableField]

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
        "between submitted coordinates on a spherical Mars model (IAU mean radius 3389.5 km). "
        "When DEM data is loaded, elevation profiles and slope calculations are derived from "
        "validated 200m numerical rasters. No classified hazard layer is loaded. "
        "This output is a planning aid and must NOT be used for real astronaut navigation decisions."
    )
