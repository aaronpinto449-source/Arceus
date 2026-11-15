"""
ARES Mission Control - MOLA Cartography & Spatial Service
Streams optimized in-memory MOLA tiles and computes planetary geodetic metrics.
"""

import io
import math
from typing import Dict, Any, Optional
from PIL import Image

from backend.app.core.config import MAP_FILES, REGION_BOUNDS, MARS_EQUATORIAL_RADIUS_KM

# In-memory RAM cache for optimized JPEG tile bytes
_IMAGE_CACHE: Dict[str, bytes] = {}


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

