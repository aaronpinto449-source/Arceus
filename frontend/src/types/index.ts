export type NavigationPage = 
  | 'Mission Overview'
  | 'Mars Explorer'
  | 'Route Planner'
  | 'Terrain Intelligence'
  | 'Hazard Analysis'
  | 'Science Discovery';

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

