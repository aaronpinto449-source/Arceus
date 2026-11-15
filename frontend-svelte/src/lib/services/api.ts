import type { Region, PointOfInterest, GroundResolution } from '../types';
import { INITIAL_REGIONS } from '../data/regions';

const API_BASE_URL = 'http://127.0.0.1:8001/api';

export const api = {
  async checkHealth(): Promise<{ status: string; sol: string }> {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (!res.ok) throw new Error('Health check failed');
      return await res.json();
    } catch {
      return { status: 'STANDALONE', sol: '001' };
    }
  },

  async getRegions(): Promise<Region[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/regions`);
      if (!res.ok) throw new Error('Failed to fetch regions');
      return await res.json();
    } catch {
      return INITIAL_REGIONS;
    }
  },

  async getRegion(id: string): Promise<Region> {
    try {
      const res = await fetch(`${API_BASE_URL}/regions/${id}`);
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
      const res = await fetch(`${API_BASE_URL}/regions/${id}/pois`);
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

  async getSpatialResolution(lat: number): Promise<GroundResolution> {
    try {
      const res = await fetch(`${API_BASE_URL}/telemetry/resolution?lat=${lat}`);
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
  }
};

