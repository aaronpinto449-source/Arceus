import type { Region, PointOfInterest, GroundResolution, RoutePlanRequest, RoutePlanResponse, PointElevationResponse, CrismHydrousSite } from '../types';
import { INITIAL_REGIONS } from '../data/regions';

const ENV_API_URL = import.meta.env.VITE_API_BASE_URL;
const AUTO_ORIGIN_API = typeof window !== 'undefined' && window.location.hostname && !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1')
  ? `${window.location.origin}/api`
  : 'http://127.0.0.1:8001/api';

const API_BASE_URL = ENV_API_URL || AUTO_ORIGIN_API;
const API_FALLBACK_URL = 'http://127.0.0.1:8000/api';

async function fetchWithFallback(endpoint: string, options?: RequestInit): Promise<Response> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return res;
  } catch (err) {
    // If primary port failed, try alternate port 8000
    try {
      const res = await fetch(`${API_FALLBACK_URL}${endpoint}`, options);
      return res;
    } catch {
      throw err;
    }
  }
}

export const api = {
  async checkHealth(): Promise<{ status: string; sol: string }> {
    try {
      const res = await fetchWithFallback('/health');
      if (!res.ok) throw new Error('Health check failed');
      return await res.json();
    } catch {
      return { status: 'STANDALONE', sol: '001' };
    }
  },

  async getRegions(): Promise<Region[]> {
    try {
      const res = await fetchWithFallback('/regions');
      if (!res.ok) throw new Error('Failed to fetch regions');
      return await res.json();
    } catch {
      return INITIAL_REGIONS;
    }
  },

  async getRegion(id: string): Promise<Region> {
    try {
      const res = await fetchWithFallback(`/regions/${id}`);
      if (!res.ok) throw new Error(`Failed to fetch region ${id}`);
      return await res.json();
    } catch {
      const found = INITIAL_REGIONS.find(r => r.id === id);
      if (found) return found;
      return INITIAL_REGIONS[0];
    }
  },

  async getRegionPOIs(id: string): Promise<PointOfInterest[]> {
    try {
      const res = await fetchWithFallback(`/regions/${id}/pois`);
      if (!res.ok) throw new Error(`Failed to fetch POIs for ${id}`);
      return await res.json();
    } catch {
      const found = INITIAL_REGIONS.find(r => r.id === id);
      return found?.pois || [];
    }
  },

  getRegionMapUrl(id: string, maxDim: number = 1536): string {
    return `${API_BASE_URL}/regions/${id}/map?max_dim=${maxDim}&quality=85`;
  },

  getRegionSlopeMapUrl(id: string): string {
    return `${API_BASE_URL}/regions/${id}/slope-map`;
  },

  getRegionElevationMapUrl(id: string): string {
    return `${API_BASE_URL}/regions/${id}/elevation-map`;
  },

  getJezeroCtxMapUrl(): string {
    return `${API_BASE_URL}/regions/jezero-crater/ctx-map`;
  },

  async getRegionLayers(id: string): Promise<any> {
    try {
      const res = await fetchWithFallback(`/regions/${id}/layers`);
      if (!res.ok) throw new Error('Failed to fetch layers');
      return await res.json();
    } catch {
      return null;
    }
  },

  async getHydrousSites(regionId: string = 'jezero-crater'): Promise<CrismHydrousSite[]> {
    try {
      const res = await fetchWithFallback(`/regions/${regionId}/hydrous-sites`);
      if (!res.ok) throw new Error('Failed to fetch hydrous sites');
      return await res.json();
    } catch {
      return [];
    }
  },

  async getPointElevation(regionId: string, lat: number, lon: number): Promise<PointElevationResponse> {
    try {
      const res = await fetchWithFallback(`/regions/${regionId}/elevation?lat=${lat}&lon=${lon}`);
      if (!res.ok) throw new Error('Elevation query failed');
      return await res.json();
    } catch {
      return {
        lat,
        lon,
        elevation_m: null,
        slope_deg: null,
        dem_available: false,
        source: 'UNAVAILABLE'
      };
    }
  },

  async getSpatialResolution(lat: number): Promise<GroundResolution> {
    try {
      const res = await fetchWithFallback(`/telemetry/resolution?lat=${lat}`);
      if (!res.ok) throw new Error('Failed to calculate resolution');
      return await res.json();
    } catch {
      const rad = (lat * Math.PI) / 180.0;
      const cosLat = Math.cos(rad);
      const mLat = (2.0 * Math.PI * 3389500.0) / (360.0 * 256.0);
      const mLon = mLat * Math.abs(cosLat);
      return {
        lat_deg: lat,
        meters_per_pixel_lat: Math.round(mLat * 10) / 10,
        meters_per_pixel_lon: Math.round(mLon * 10) / 10,
        cos_factor: Math.round(cosLat * 1000) / 1000,
        longitude_compression_pct: Math.round((1.0 - Math.abs(cosLat)) * 1000) / 10
      };
    }
  },

  async planRoute(payload: RoutePlanRequest): Promise<RoutePlanResponse> {
    const urls = [API_BASE_URL, API_FALLBACK_URL];
    let lastError: Error | null = null;

    for (const base of urls) {
      try {
        const res = await fetch(`${base}/routes/plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errorBody = await res.json().catch(() => null);
          const detail = errorBody?.detail || `API error (${res.status})`;
          throw new Error(detail);
        }

        return await res.json();
      } catch (err: any) {
        lastError = err;
        // If it's a genuine 422 or server business logic error, don't try other port
        if (err.message && !err.message.includes('fetch') && !err.message.includes('NetworkError') && !err.message.includes('Failed to')) {
          throw err;
        }
      }
    }

    throw lastError || new Error('Backend route planning service unreachable.');
  },

  async getChallengeResources(): Promise<{ challenge: string; challenge_url: string; resources: Record<string, any> }> {
    try {
      const res = await fetchWithFallback('/resources');
      if (!res.ok) throw new Error('Failed to fetch resources');
      return await res.json();
    } catch {
      return {
        challenge: 'Interplanetary Survival Guide: Martian Map',
        challenge_url: 'https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/?tab=resources',
        resources: {
          mars_trek: {
            title: 'NASA Jet Propulsion Laboratory (JPL) Mars Trek',
            url: 'https://trek.nasa.gov/mars/',
            description: 'NASA web-based portal for exploration of Mars, showcasing data collected by NASA at various landing sites.',
            category: 'Mars Planetary Portal & Tile Services',
            authority: 'NASA JPL / Solar System Treks',
            is_mars_specific: true
          },
          usgs_geologic_maps: {
            title: 'USGS-NASA Planetary Geologic Mapping Program',
            url: 'https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars',
            description: 'High-quality standardized geologic map of Mars (SIM 3292) providing stratigraphic terrain classifications.',
            category: 'Mars Geological Cartography & Surface Material',
            authority: 'USGS Astrogeology Science Center / NASA',
            is_mars_specific: true
          },
          curiosity_mount_sharp_route: {
            title: "Curiosity's Proposed Path up Mount Sharp",
            url: 'https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/',
            description: "NASA Science mission visual depicting Curiosity's traversal corridor from Bradbury Landing up lower Mount Sharp.",
            category: 'Mars Traversability Ground Truth & Route Planning',
            authority: 'NASA Science Mission Directorate / JPL',
            is_mars_specific: true
          },
          perseverance_raw_images: {
            title: 'NASA Mars Perseverance Raw Images Gallery',
            url: 'https://mars.nasa.gov/mars2020/multimedia/raw-images/',
            description: 'Over 1 million surface point-of-view images captured by the Perseverance rover across Jezero Crater.',
            category: 'Mars Point-of-View Visual Ground Truth',
            authority: 'NASA Mars 2020 Mission / JPL-Caltech',
            is_mars_specific: true
          },
          nasa_worldview: {
            title: 'NASA Worldview (Earthdata)',
            url: 'https://worldview.earthdata.nasa.gov/',
            description: 'General supplementary reference cited on the challenge page as an exemplar for multi-sensor layer compositing (Earth observation reference, not a Mars dataset).',
            category: 'General Supplementary Resource (Earth Observation Exemplar)',
            authority: 'NASA Earth Science Data and Information System (ESDIS)',
            is_mars_specific: false
          }
        }
      };
    }
  }
};

