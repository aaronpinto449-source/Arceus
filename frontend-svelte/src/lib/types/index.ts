export type NavigationPage = 
  | 'Mission Overview'
  | 'Mars Explorer'
  | 'Route Planner'
  | 'Terrain Intelligence'
  | 'Hazard Analysis'
  | 'Science Discovery';

export type InterfaceMode = 'desktop' | 'field';

export interface RegionBounds {
  lat_min: number;
  lat_max: number;
  lon_min: number;
  lon_max: number;
  pixel_width: number;
  pixel_height: number;
  pixels_per_degree: number;
  lat_convention: string;
  lon_convention: string;
  projection: string;
  reference_meridian: string;
}

export interface PointOfInterest {
  id: string;
  name: string;
  lat: number;
  lon: number;
  type: string;
  description: string;
  significance: string;
  source_reference?: string;
  investigation_focus?: string;
  data_provenance_type?: string;
  nasa_mission?: string;
}

export interface Region {
  id: string;
  name: string;
  lat: number;
  lon: number;
  elevation_approx: string;
  diameter: string;
  geology: string;
  description: string;
  objective: string;
  mission_context: string;
  elevation_summary: string;
  bounds: RegionBounds;
  poi_count?: number;
  pois?: PointOfInterest[];
}

export interface GroundResolution {
  lat_deg: number;
  meters_per_pixel_lat: number;
  meters_per_pixel_lon: number;
  cos_factor: number;
  longitude_compression_pct: number;
}

export interface SelectedTarget {
  lat: number;
  lon: number;
  name: string;
  type?: string;
  source?: string;
}

export interface PointElevationResponse {
  lat: number;
  lon: number;
  elevation_m: number | null;
  slope_deg: number | null;
  dem_available: boolean;
  difficulty_level?: string;
  traversability_rating?: string;
  slip_risk?: string;
  resolution_m?: number;
  source: string;
}

export interface CrismHydrousSite {
  id: string;
  target_id: string;
  name: string;
  lat: number;
  lon: number;
  mineral_type: string;
  description: string;
  instrument: string;
  provenance: string;
}

export interface MissionTelemetry {
  sol: string;
  commDelay: string;
  systemStatus: 'NOMINAL' | 'WARNING' | 'ALERT';
  powerGrid: string;
  surfaceTemp: string;
  atmosphericPressure: string;
}

// ---------------------------------------------------------------------------
// Route Planning Types (matching FastAPI backend models)
// ---------------------------------------------------------------------------

export type RoutePriority = 'SAFETY' | 'DISTANCE' | 'BALANCED';
export type RoverType = 'PCR' | 'LUV' | 'HCH';
export type ProvenanceLabel = 'CALCULATED' | 'ESTIMATED' | 'UNAVAILABLE' | 'SIMULATED';

export interface RouteCoordinate {
  lat: number;
  lon: number;
  label?: string | null;
  is_poi: boolean;
  provenance: ProvenanceLabel;
}

export interface RouteSegment {
  index: number;
  from_label: string;
  to_label: string;
  from_coord: RouteCoordinate;
  to_coord: RouteCoordinate;
  distance_km: number;
  bearing_deg: number;
  distance_provenance: ProvenanceLabel;
  bearing_provenance: ProvenanceLabel;
  geometry_caveat: string;
}

export interface TravelTimeEstimate {
  rover_name: string;
  rover_nominal_speed_kmh: number;
  estimated_duration_min: number;
  estimated_duration_hrs: number;
  provenance: ProvenanceLabel;
  assumption: string;
  supported: boolean;
}

export interface UnavailableField {
  supported: boolean;
  provenance: ProvenanceLabel;
  reason: string;
}

export interface ElevationSample {
  distance_km: number;
  lat: number;
  lon: number;
  elevation_m: number;
}

export interface ElevationProfileData {
  supported: boolean;
  provenance: ProvenanceLabel;
  min_elevation_m: number;
  max_elevation_m: number;
  start_elevation_m: number;
  end_elevation_m: number;
  elevation_change_m: number;
  elevation_gain_m: number;
  samples: ElevationSample[];
  reason?: string;
}

export interface SlopeAnalysisData {
  supported: boolean;
  provenance: ProvenanceLabel;
  min_slope_deg: number;
  max_slope_deg: number;
  mean_slope_deg: number;
  steep_slopes_detected: boolean;
  max_recommended_slope_deg: number;
  reason?: string;
}

export interface TerrainCostData {
  supported: boolean;
  provenance: ProvenanceLabel;
  cost_index: number;
  slope_penalty: number;
  reason?: string;
}

export interface PriorityModeExplanation {
  mode: RoutePriority;
  description: string;
  effect_on_geometry: string;
  effect_on_waypoints: string;
}

export interface DataSourceInfo {
  mode: string;
  description: string;
  dem_available: boolean;
  mola_tiles_used: boolean;
  resolution_note: string;
  coordinate_system: string;
  mars_radius_km: number;
  snap_threshold_deg?: number;
  snap_threshold_km_approx?: string;
}

export interface RoverFeasibility {
  rover_range_km: number;
  total_distance_km: number;
  within_range: boolean;
  margin_km: number;
  return_trip_km?: number;
  return_feasible?: boolean;
  return_margin_km?: number;
  provenance: ProvenanceLabel;
  range_caveat: string;
}

export interface RoutePlanResponse {
  coordinates: RouteCoordinate[];
  segments: RouteSegment[];
  total_distance_km: number;
  feasibility: RoverFeasibility;
  travel_time?: TravelTimeEstimate | null;
  terrain_cost: TerrainCostData | UnavailableField;
  slope_data: SlopeAnalysisData | UnavailableField;
  hazard_exposure: UnavailableField;
  elevation_profile: ElevationProfileData | UnavailableField;
  priority_explanation: PriorityModeExplanation;
  algorithm_used: 'DIJKSTRA-POI-GRAPH' | 'HAVERSINE-DIRECT';
  data_source: DataSourceInfo;
  priority_used: RoutePriority;
  rover_type: RoverType;
  warnings: string[];
  limitations: string[];
  scientific_disclaimer: string;
}

export interface RoutePlanRequest {
  region_id: string;
  start: { lat: number; lon: number };
  destination: { lat: number; lon: number };
  rover_type?: RoverType;
  priority?: RoutePriority;
  use_dem?: boolean;
}

