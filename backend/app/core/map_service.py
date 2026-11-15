"""
ARES Mission Control - MOLA Cartography, CTX High-Res Imagery & Spatial Service
Streams optimized in-memory MOLA tiles, CTX mosaics, and computes planetary geodetic metrics.
"""

import io
import math
import csv
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from PIL import Image
import numpy as np

from backend.app.core.config import MAP_FILES, REGION_BOUNDS, MARS_EQUATORIAL_RADIUS_KM, DATA_RAW_DIR

# In-memory RAM cache for optimized image tile bytes
_IMAGE_CACHE: Dict[str, bytes] = {}

# Exact georeferenced bounding coordinates for 6m Jezero CTX Mosaic
# Evaluated from ModelTiepointTag (4573663.25, 1109693.14), Scale (6m/px), and Mars 2000 Sphere (R=3396190m)
JEZERO_CTX_BOUNDS = {
    "lat_min": 18.2110,
    "lat_max": 18.7212,
    "lon_min": 77.1605,
    "lon_max": 77.6992,
    "resolution_m": 6.0,
    "crs": "Equirectangular Mars 2000 Sphere (IAU)",
    "instrument": "Context Camera (CTX) / Mars Reconnaissance Orbiter (MRO)",
}

JEZERO_CTX_FILE = DATA_RAW_DIR / "jezero" / "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0.tif"
JEZERO_CRISM_FILE = DATA_RAW_DIR / "jezero" / "hydrous_sites_geo_map.csv"


def get_optimized_map_bytes(region_id: str, max_dim: int = 1536, quality: int = 85) -> Optional[bytes]:
    """
    Load raw MOLA PNG from disk, downsample in memory, and return JPEG bytes.
    Subsequent calls return directly from memory cache.
    Zero disk writes or duplicates.
    """
    cache_key = f"{region_id}_{max_dim}_{quality}"
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    image_path = MAP_FILES.get(region_id)
    if not image_path or not image_path.exists():
        return None

    raw_img = Image.open(image_path)
    resized_img = raw_img.resize((max_dim, max_dim), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    resized_img.save(buf, format="JPEG", quality=quality)
    jpeg_bytes = buf.getvalue()

    _IMAGE_CACHE[cache_key] = jpeg_bytes
    return jpeg_bytes


def get_jezero_ctx_bytes(max_dim: int = 2048, quality: int = 85) -> Optional[bytes]:
    """
    Stream high-resolution 6-meter/pixel Jezero CTX orthomosaic as web-optimized JPEG.
    Caches in memory for instant delivery.
    """
    cache_key = f"jezero_ctx_{max_dim}_{quality}"
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    if not JEZERO_CTX_FILE.exists():
        return None

    try:
        with Image.open(JEZERO_CTX_FILE) as img:
            # Maintain aspect ratio (5322 x 5040)
            img.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            jpeg_bytes = buf.getvalue()
            _IMAGE_CACHE[cache_key] = jpeg_bytes
            return jpeg_bytes
    except Exception:
        return None


def get_elevation_tint_bytes(region_id: str) -> Optional[bytes]:
    """
    Generates a high-precision hypsometric elevation tint overlay directly from
    the validated numerical DEM array (int16).
    Produces transparent RGBA PNG where elevation values map to scientific palette.
    """
    cache_key = f"dem_elev_tint_{region_id}"
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    from backend.app.core.terrain_pipeline import terrain_pipeline
    dem_data = terrain_pipeline.load_dem_grid(region_id)
    if not dem_data:
        return None

    arr, meta = dem_data
    nodata = meta.get("nodata_value", -32768)

    valid = (arr != nodata) & ~np.isnan(arr)
    if not np.any(valid):
        return None

    min_val = float(arr[valid].min())
    max_val = float(arr[valid].max())
    span = max_val - min_val if max_val > min_val else 1.0

    norm = np.zeros_like(arr, dtype=np.float32)
    norm[valid] = (arr[valid] - min_val) / span

    # Hypsometric stops: Basin (blue) -> Plain (cyan) -> Moderate (green) -> Ridge (yellow) -> Mountain (orange) -> Peak (white)
    stops = [
        (0.0, [41, 168, 222]),   # Deep blue-cyan
        (0.25, [75, 175, 80]),   # Green
        (0.50, [240, 206, 68]),  # Yellow
        (0.75, [235, 115, 41]),  # Orange
        (1.0, [255, 255, 255]),  # White
    ]

    h, w = arr.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    r = np.zeros_like(norm)
    g = np.zeros_like(norm)
    b = np.zeros_like(norm)

    for i in range(len(stops) - 1):
        t0_val, c0 = stops[i]
        t1_val, c1 = stops[i + 1]
        mask = valid & (norm >= t0_val) & (norm <= t1_val)
        frac = (norm[mask] - t0_val) / (t1_val - t0_val)
        r[mask] = c0[0] + frac * (c1[0] - c0[0])
        g[mask] = c0[1] + frac * (c1[1] - c0[1])
        b[mask] = c0[2] + frac * (c1[2] - c0[2])

    rgba[valid, 0] = r[valid].astype(np.uint8)
    rgba[valid, 1] = g[valid].astype(np.uint8)
    rgba[valid, 2] = b[valid].astype(np.uint8)
    rgba[valid, 3] = 145  # Semi-transparent overlay to blend with shaded relief

    img = Image.fromarray(rgba, "RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    _IMAGE_CACHE[cache_key] = png_bytes
    return png_bytes


def get_crism_hydrous_sites() -> List[Dict[str, Any]]:
    """
    Extracts verified MRO CRISM spectral hydrous mineral detections in the Jezero region
    from the provided hydrous_sites_geo_map.csv dataset.
    """
    if not JEZERO_CRISM_FILE.exists():
        return []

    sites = []
    descriptions = {
        "HRL000040FF": "Neretva Vallis Inflow Delta — Fe/Mg phyllosilicates & smectite clay signatures.",
        "HRL00010963": "Eastern Crater Floor Margin — Carbonate and olivine-bearing bedrock unit.",
        "FRT0001182A": "Northern Crater Rim Massif — Noachian crustal basement silicate blocks.",
        "FRT000165F7": "Western Fan Delta Front — Layered deltaic clays with astrobiological preservation potential.",
        "HRL0000B8C2": "Southern Rim Ejecta — Hydrated silica and altered impact melt.",
    }

    try:
        with open(JEZERO_CRISM_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if len(row) >= 2:
                    try:
                        lon = float(row[0])
                        lat = float(row[1])
                        target_id = row[3].strip(' "') if len(row) > 3 and row[3] else f"CRISM-{idx}"
                        if 17.2 <= lat <= 19.2 and 76.8 <= lon <= 78.6:
                            sites.append({
                                "id": f"CRISM-{target_id}",
                                "target_id": target_id,
                                "name": f"CRISM Mineral Unit ({target_id})",
                                "lat": round(lat, 4),
                                "lon": round(lon, 4),
                                "mineral_type": "Hydrous Phyllosilicates / Carbonates",
                                "description": descriptions.get(target_id, "Verified MRO CRISM spectral detection of ancient water-altered minerals."),
                                "instrument": "Compact Reconnaissance Imaging Spectrometer for Mars (CRISM)",
                                "provenance": "NASA MRO / PDS Geosciences Node"
                            })
                    except (ValueError, IndexError):
                        continue
    except Exception:
        return []

    return sites


def calculate_ground_resolution(lat_deg: float, pixels_per_degree: float = 256.0) -> Dict[str, float]:
    """
    Calculate local spatial resolution in metres per pixel at a given latitude.
    Accounts for cosine longitude convergence on Mars.
    """
    lat_rad = math.radians(lat_deg)
    meters_per_deg_lat = (2.0 * math.pi * MARS_EQUATORIAL_RADIUS_KM * 1000.0) / 360.0
    meters_per_pixel_lat = meters_per_deg_lat / pixels_per_degree
    meters_per_pixel_lon = meters_per_pixel_lat * math.cos(lat_rad)

    return {
        "lat_deg": round(lat_deg, 4),
        "meters_per_pixel_lat": round(meters_per_pixel_lat, 2),
        "meters_per_pixel_lon": round(meters_per_pixel_lon, 2),
        "cos_factor": round(math.cos(lat_rad), 4),
        "longitude_compression_pct": round((1.0 - math.cos(lat_rad)) * 100.0, 2)
    }
