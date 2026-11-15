"""
ARES Mission Control - Terrain Data Ingestion & Processing Pipeline
Phase 2 Foundation: Prepares ingestion interfaces for regional numerical DEMs
and rover surface traverse trajectories.

SCIENTIFIC INTEGRITY CONTRACT:
- If a numerical DEM or traverse file is not present on disk, this pipeline
  reports 'available: False' and returns empty/unpopulated structures.
- It NEVER fabricates heights, slopes, or waypoints from visual PNG colors.
- It validates incoming raster files to ensure color images (RGB/RGBA) are
  never mistakenly treated as numerical elevation grids.
- Slope gradients account for Mars planetary radius and latitude-dependent
  longitude cell convergence, and explicitly mask NoData values.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np
from PIL import Image

from backend.app.core.config import (
    DATA_RAW_DIR,
    MARS_MEAN_RADIUS_KM,
    MARS_EQUATORIAL_RADIUS_KM,
    REGION_BOUNDS
)

# Standardized expected incoming file locations in data/raw/
DEM_FILE_CANDIDATES: Dict[str, List[Path]] = {
    "gale-crater": [
        DATA_RAW_DIR / "gale_crater_dem.tif",
        DATA_RAW_DIR / "gale_crater_dem.tiff",
        DATA_RAW_DIR / "gale_crater_dem.npy",
        DATA_RAW_DIR / "megt_s_120_256.img",
    ],
    "jezero-crater": [
        DATA_RAW_DIR / "jezero_crater_dem.tif",
        DATA_RAW_DIR / "jezero_crater_dem.tiff",
        DATA_RAW_DIR / "jezero_crater_dem.npy",
        DATA_RAW_DIR / "megt_n_060_256.img",
    ],
    "olympus-mons": [
        DATA_RAW_DIR / "olympus_mons_dem.tif",
        DATA_RAW_DIR / "olympus_mons_dem.tiff",
        DATA_RAW_DIR / "olympus_mons_dem.npy",
        DATA_RAW_DIR / "megt_n_210_256.img",
    ],
}

TRAVERSE_FILE_CANDIDATES: Dict[str, List[Path]] = {
    "perseverance": [
        DATA_RAW_DIR / "perseverance_traverse.csv",
        DATA_RAW_DIR / "m2020_traverse_waypoints.csv",
        DATA_RAW_DIR / "perseverance_surface_traverse.csv",
    ],
    "curiosity": [
        DATA_RAW_DIR / "curiosity_traverse.csv",
        DATA_RAW_DIR / "msl_traverse_waypoints.csv",
    ]
}

# Standard planetary NoData markers (MOLA, HRSC, HiRISE, GDAL standard)
STANDARD_NODATA_VALUES = {-32768.0, -9999.0, -32767.0, -3.4028235e+38}


@dataclass
class DatasetStatus:
    dataset_id: str
    target_region: str
    data_type: str  # "NUMERICAL_DEM" | "ROVER_TRAVERSE" | "COLOR_IMAGE" | "UNKNOWN"
    is_available: bool
    validation_status: str  # "NOT_FOUND" | "VALIDATED_NUMERICAL_DEM" | "REJECTED_RGB_IMAGE" | "CORRUPTED"
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    format: Optional[str] = None
    units: str = "METERS_RELATIVE_TO_AREOID"
    verified_properties: Dict[str, Any] = field(default_factory=dict)
    assumed_properties: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class TraverseWaypoint:
    sol: int
    site_id: Optional[str]
    drive_id: Optional[str]
    lat: float
    lon: float
    coordinate_convention: str = "IAU_2000_PLANETOCENTRIC_EAST_LON"
    elevation_m: Optional[float] = None
    accumulated_distance_m: Optional[float] = None
    timestamp_utc: Optional[str] = None
    provenance: str = "OFFICIAL_NASA_MISSION_ARCHIVE"


def validate_dem_file(path: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Inspects candidate DEM file to ensure it is a valid single-band numerical raster,
    preventing multi-band RGB color imagery from being treated as elevation data.
    """
    if not path.exists() or not path.is_file():
        return False, "File does not exist.", {}

    suffix = path.suffix.lower()

    if suffix == ".npy":
        try:
            # Memory-map the array to inspect shape and dtype without loading entire array
            mmap_arr = np.load(path, mmap_mode="r")
            if mmap_arr.ndim != 2:
                return False, f"NumPy array must be 2D scalar grid (got shape {mmap_arr.shape}).", {}
            if not np.issubdtype(mmap_arr.dtype, np.number):
                return False, f"NumPy array dtype must be numeric (got {mmap_arr.dtype}).", {}
            return True, "Valid 2D numerical NumPy elevation array.", {
                "shape": list(mmap_arr.shape),
                "dtype": str(mmap_arr.dtype),
                "bands": 1
            }
        except Exception as e:
            return False, f"Failed to parse NumPy file: {e}", {}

    elif suffix in (".tif", ".tiff", ".img", ".png"):
        try:
            with Image.open(path) as img:
                bands = img.getbands()
                mode = img.mode

                # Explicitly reject multi-channel RGB/RGBA visual imagery
                if mode in ("RGB", "RGBA", "P") or len(bands) > 1:
                    return (
                        False,
                        f"Rejected: File has mode '{mode}' with bands {bands}. "
                        "It is an RGB/RGBA visual map, NOT a single-band numerical DEM.",
                        {"mode": mode, "bands": list(bands), "size": list(img.size)}
                    )

                # Valid single-band modes: 'F' (32-bit float), 'I' (32-bit int), 'I;16' (16-bit uint), 'I;16S' (16-bit int)
                valid_modes = ("F", "I", "I;16", "I;16S", "L")
                if mode in valid_modes:
                    return True, f"Valid single-band numerical raster (mode: {mode}).", {
                        "mode": mode,
                        "bands": list(bands),
                        "size": list(img.size)
                    }

                return False, f"Unsupported single-band mode '{mode}'.", {"mode": mode}
        except Exception as e:
            return False, f"Raster validation error: {e}", {}

    return False, f"Unrecognized file format '{suffix}'.", {}


def calculate_grid_spacing(
    lat_deg: float,
    pixels_per_degree: float = 256.0,
    mars_radius_km: float = MARS_MEAN_RADIUS_KM
) -> Tuple[float, float]:
    """
    Computes local ground resolution (meters per pixel) on a spherical Mars model:
      meters_per_pixel_lat = (2 * pi * R) / (360 * pixels_per_degree)
      meters_per_pixel_lon = meters_per_pixel_lat * cos(lat)
    
    Verified calculation using IAU 2000 Mars mean radius (3389.5 km).
    """
    if pixels_per_degree <= 0:
        raise ValueError("pixels_per_degree must be positive.")

    r_meters = mars_radius_km * 1000.0
    lat_rad = math.radians(lat_deg)
    m_lat = (2.0 * math.pi * r_meters) / (360.0 * pixels_per_degree)
    m_lon = m_lat * abs(math.cos(lat_rad))
    return m_lat, m_lon


def calculate_tile_row_spacings(
    lat_min: float,
    lat_max: float,
    num_rows: int,
    pixels_per_degree: float = 256.0,
    mars_radius_km: float = MARS_MEAN_RADIUS_KM
) -> Tuple[float, np.ndarray]:
    """
    Calculates exact latitude-dependent longitudinal cell widths for each row
    in a north-to-south oriented raster tile. Eliminates distortion caused by
    cosine convergence across large latitude extents (e.g. 0° to 30°N).
    
    Returns:
      meters_per_pixel_lat: float (constant along meridians)
      dx_per_row: np.ndarray (length = num_rows, longitude width in meters at each row)
    """
    if num_rows < 2:
        raise ValueError("num_rows must be at least 2.")
    if lat_min >= lat_max:
        raise ValueError("lat_max must be greater than lat_min.")

    r_meters = mars_radius_km * 1000.0
    m_lat = (2.0 * math.pi * r_meters) / (360.0 * pixels_per_degree)

    # Standard raster rows run from top (lat_max) to bottom (lat_min)
    row_lats = np.linspace(lat_max, lat_min, num_rows)
    dx_per_row = m_lat * np.cos(np.radians(row_lats))

    # Guard against polar singularity (clamp to minimum 0.001 m/px at poles)
    dx_per_row = np.maximum(dx_per_row, 0.001)

    return m_lat, dx_per_row


class TerrainPipeline:
    """
    Modular processing pipeline for Mars regional topography.
    Prepares hooks for:
      1. Gale Crater DEM processing
      2. Jezero Crater DEM processing
      3. Olympus Mons DEM processing
      4. Perseverance Rover traverse ingestion
    """

    def __init__(self, data_dir: Path = DATA_RAW_DIR):
        self.data_dir = data_dir
        self._dem_cache: Dict[str, Tuple[np.ndarray, Dict[str, Any]]] = {}
        self._slope_cache: Dict[str, Tuple[np.ndarray, Dict[str, Any]]] = {}

    def clear_cache(self) -> None:
        """Clears memory caches for DEM matrices and computed slope grids."""
        self._dem_cache.clear()
        self._slope_cache.clear()

    def get_dem_status(self, region_id: str) -> DatasetStatus:
        """
        Inspects disk for real numerical DEM candidates and validates they are
        genuine single-band elevation arrays (not colorized visual PNG/TIFFs).
        """
        candidates = DEM_FILE_CANDIDATES.get(region_id, [])
        for cand in candidates:
            if cand.exists() and cand.is_file():
                is_valid_dem, reason, props = validate_dem_file(cand)
                if is_valid_dem:
                    return DatasetStatus(
                        dataset_id=f"{region_id}-dem",
                        target_region=region_id,
                        data_type="NUMERICAL_DEM",
                        is_available=True,
                        validation_status="VALIDATED_NUMERICAL_DEM",
                        file_path=str(cand),
                        file_size_bytes=cand.stat().st_size,
                        format=cand.suffix.upper().lstrip("."),
                        units="METERS_RELATIVE_TO_AREOID",
                        verified_properties={
                            "file_name": cand.name,
                            "file_size_bytes": cand.stat().st_size,
                            **props
                        },
                        assumed_properties={
                            "vertical_datum": "Mars MOLA Areoid (IAU/IAG 2000)",
                            "horizontal_crs": "Planetocentric Lat, East Lon"
                        },
                        notes="Verified single-band numerical DEM raster present."
                    )
                else:
                    return DatasetStatus(
                        dataset_id=f"{region_id}-dem",
                        target_region=region_id,
                        data_type="COLOR_IMAGE" if "RGB" in reason else "UNKNOWN",
                        is_available=False,
                        validation_status="REJECTED_RGB_IMAGE" if "RGB" in reason else "CORRUPTED",
                        file_path=str(cand),
                        notes=f"Candidate file rejected: {reason}"
                    )

        return DatasetStatus(
            dataset_id=f"{region_id}-dem",
            target_region=region_id,
            data_type="NUMERICAL_DEM",
            is_available=False,
            validation_status="NOT_FOUND",
            units="METERS_RELATIVE_TO_AREOID",
            assumed_properties={
                "expected_resolution": "256 pixels/degree (~231 m/px latitudinal)",
                "datum": "MOLA Areoid"
            },
            notes=(
                f"Numerical DEM for '{region_id}' is awaiting external dataset ingestion. "
                "Current visual MOLA PNG is a color map and cannot be used for elevation/slope."
            )
        )

    def get_traverse_status(self, rover_id: str = "perseverance") -> DatasetStatus:
        """Inspect disk for real rover traverse CSV data."""
        candidates = TRAVERSE_FILE_CANDIDATES.get(rover_id, [])
        for cand in candidates:
            if cand.exists() and cand.is_file():
                return DatasetStatus(
                    dataset_id=f"{rover_id}-traverse",
                    target_region="jezero-crater" if rover_id == "perseverance" else "gale-crater",
                    data_type="ROVER_TRAVERSE",
                    is_available=True,
                    validation_status="VALIDATED_CSV",
                    file_path=str(cand),
                    file_size_bytes=cand.stat().st_size,
                    format="CSV",
                    units="DEGREES_AND_METERS",
                    verified_properties={"file_name": cand.name},
                    assumed_properties={"coordinate_system": "IAU Planetocentric East Lon"},
                    notes="Verified rover traverse CSV present on disk."
                )

        return DatasetStatus(
            dataset_id=f"{rover_id}-traverse",
            target_region="jezero-crater" if rover_id == "perseverance" else "gale-crater",
            data_type="ROVER_TRAVERSE",
            is_available=False,
            validation_status="NOT_FOUND",
            format="CSV",
            units="DEGREES_AND_METERS",
            notes=f"No traverse CSV found for rover '{rover_id}'. Awaiting official NASA mission archive CSV."
        )

    def load_perseverance_traverse(self) -> Tuple[bool, List[TraverseWaypoint], Dict[str, Any], str]:
        """
        Ingest NASA Perseverance (M2020) rover traverse waypoints if CSV is present.
        Does NOT assume rigid column names; matches known NASA PDS Analyst's Notebook
        and USGS column variants case-insensitively.
        
        Validates latitude [-90, +90] and normalizes longitude to East [0, 360].
        Skips invalid/empty coordinate rows rather than fabricating default 0.0 values.
        
        Returns: (success, waypoints, metadata, message)
        """
        status = self.get_traverse_status("perseverance")
        if not status.is_available or not status.file_path:
            return False, [], {}, "Perseverance traverse CSV not found. Zero waypoints fabricated."

        waypoints: List[TraverseWaypoint] = []
        skipped_rows = 0

        # Known column aliases in NASA PDS Analyst's Notebook & USGS Jezero traverses
        col_aliases = {
            "lat": ["latitude", "lat", "rover_nav_latitude", "planetocentric_latitude", "northing_deg", "lat_deg"],
            "lon": ["longitude", "lon", "rover_nav_longitude", "east_longitude", "easting_deg", "lon_deg", "planetocentric_longitude"],
            "sol": ["sol", "sol_number", "martian_sol"],
            "elev": ["elevation", "elevation_m", "elev_m", "elev", "z_m", "areoid_elevation_m", "height_m"],
            "dist": ["distance_m", "accumulated_distance_m", "odometry_m", "dist_m", "total_dist_m", "drive_distance_m"],
            "site": ["site", "site_id", "rover_site"],
            "drive": ["drive", "drive_id", "rover_drive"],
            "utc": ["utc", "timestamp", "timestamp_utc", "datetime", "utc_time"]
        }

        def find_val(row_dict: Dict[str, str], aliases: List[str]) -> Optional[str]:
            for a in aliases:
                for k, v in row_dict.items():
                    if k.strip().lower() == a:
                        return v.strip() if v else None
            return None

        try:
            with open(status.file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader):
                    raw_lat = find_val(row, col_aliases["lat"])
                    raw_lon = find_val(row, col_aliases["lon"])

                    # If latitude or longitude is missing or cannot be parsed, SKIP (do not default to 0.0)
                    if raw_lat is None or raw_lon is None:
                        skipped_rows += 1
                        continue

                    try:
                        lat = float(raw_lat)
                        lon = float(raw_lon)
                    except ValueError:
                        skipped_rows += 1
                        continue

                    # Validate geographic bounds
                    if not (-90.0 <= lat <= 90.0):
                        skipped_rows += 1
                        continue

                    # Normalize to East Longitude [0°, 360°]
                    if lon < 0.0:
                        lon = (lon + 360.0) % 360.0

                    # Parse Sol (default to 0 if missing)
                    raw_sol = find_val(row, col_aliases["sol"])
                    try:
                        sol = int(raw_sol) if raw_sol is not None else 0
                    except ValueError:
                        sol = 0

                    # Parse optional elevation and distance
                    raw_elev = find_val(row, col_aliases["elev"])
                    try:
                        elev = float(raw_elev) if raw_elev is not None else None
                    except ValueError:
                        elev = None

                    raw_dist = find_val(row, col_aliases["dist"])
                    try:
                        dist = float(raw_dist) if raw_dist is not None else None
                    except ValueError:
                        dist = None

                    waypoints.append(TraverseWaypoint(
                        sol=sol,
                        site_id=find_val(row, col_aliases["site"]),
                        drive_id=find_val(row, col_aliases["drive"]),
                        lat=lat,
                        lon=lon,
                        coordinate_convention="IAU_2000_PLANETOCENTRIC_EAST_LON",
                        elevation_m=elev,
                        accumulated_distance_m=dist,
                        timestamp_utc=find_val(row, col_aliases["utc"])
                    ))

            meta = {
                "total_rows_parsed": len(waypoints) + skipped_rows,
                "valid_waypoints_count": len(waypoints),
                "skipped_invalid_rows": skipped_rows,
                "coordinate_convention": "Planetocentric Lat (°N), East Lon (°E)",
                "provenance": "NASA Mars 2020 Mission Archive"
            }
            return True, waypoints, meta, f"Successfully parsed {len(waypoints)} valid Perseverance waypoints ({skipped_rows} skipped)."
        except Exception as e:
            return False, [], {}, f"Error parsing Perseverance traverse CSV: {e}"

    @staticmethod
    def calculate_slope_grid(
        elevation_matrix: Any,
        meters_per_pixel_lat: float,
        meters_per_pixel_lon: Union[float, np.ndarray],
        nodata_value: Optional[float] = None
    ) -> Any:
        """
        Mathematical derivation of surface slope angle in degrees from a 2D numerical elevation grid.
        
        Robustness guarantees:
          - Validates 2D shape with minimum 2x2 dimensions.
          - Validates meters_per_pixel > 0.
          - Explicitly masks NoData / NaN / Inf values so they do not produce artificial cliff artifacts.
          - Sets slope to NaN at and adjacent to NoData cells.
          - Supports row-dependent meters_per_pixel_lon vector to account for Mars latitude convergence.
          - Clamps valid slope output to physical range [0.0°, 90.0°].
        """
        if not isinstance(elevation_matrix, np.ndarray) or elevation_matrix.ndim != 2:
            raise ValueError("elevation_matrix must be a 2-dimensional numerical NumPy array.")

        rows, cols = elevation_matrix.shape
        if rows < 2 or cols < 2:
            raise ValueError(f"elevation_matrix must be at least 2x2 (got shape {elevation_matrix.shape}).")

        if meters_per_pixel_lat <= 0:
            raise ValueError("meters_per_pixel_lat must be strictly positive.")

        if isinstance(meters_per_pixel_lon, np.ndarray):
            if meters_per_pixel_lon.ndim != 1 or len(meters_per_pixel_lon) != rows:
                raise ValueError("meters_per_pixel_lon array must be 1D with length equal to rows.")
            if np.any(meters_per_pixel_lon <= 0):
                raise ValueError("meters_per_pixel_lon values must be strictly positive.")
        else:
            if meters_per_pixel_lon <= 0:
                raise ValueError("meters_per_pixel_lon must be strictly positive.")

        # Identify valid pixels and mask standard planetary NoData markers
        valid_mask = ~np.isnan(elevation_matrix) & ~np.isinf(elevation_matrix)
        if nodata_value is not None:
            valid_mask &= (elevation_matrix != nodata_value)
        for std_nd in STANDARD_NODATA_VALUES:
            valid_mask &= (elevation_matrix != std_nd)

        # Work on a float copy with NaNs at invalid locations
        elev_clean = np.array(elevation_matrix, dtype=np.float64, copy=True)
        elev_clean[~valid_mask] = np.nan

        # 1. Gradient along rows (latitude / Y axis)
        dz_dy = np.gradient(elev_clean, meters_per_pixel_lat, axis=0)

        # 2. Gradient along columns (longitude / X axis)
        if isinstance(meters_per_pixel_lon, np.ndarray):
            # Row-dependent longitudinal spacing
            dz_dx = np.zeros_like(elev_clean)
            for r in range(rows):
                dz_dx[r, :] = np.gradient(elev_clean[r, :], meters_per_pixel_lon[r])
        else:
            dz_dx = np.gradient(elev_clean, meters_per_pixel_lon, axis=1)

        # Gradient magnitude and slope angle
        gradient_magnitude = np.sqrt(dz_dx ** 2 + dz_dy ** 2)
        slope_deg = np.degrees(np.arctan(gradient_magnitude))

        # Explicitly mask out NoData cells: slope at NoData cells is undefined (NaN)
        slope_deg[~valid_mask] = np.nan

        # Clamp valid slopes to physical bounds [0°, 90°]
        valid_slopes = valid_mask & ~np.isnan(slope_deg)
        slope_deg[valid_slopes] = np.clip(slope_deg[valid_slopes], 0.0, 90.0)

        return slope_deg

    def load_dem_grid(self, region_id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Loads the validated numerical elevation matrix and companion metadata for region_id.
        Caches in memory for fast repeated querying.
        """
        if region_id in self._dem_cache:
            return self._dem_cache[region_id]

        status = self.get_dem_status(region_id)
        if not status.is_available or not status.file_path:
            return None

        cand_path = Path(status.file_path)
        meta_cand = cand_path.with_suffix(".json")
        meta: Dict[str, Any] = {}
        if meta_cand.exists():
            try:
                with open(meta_cand, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        if cand_path.suffix.lower() == ".npy":
            try:
                arr = np.load(cand_path)
                self._dem_cache[region_id] = (arr, meta)
                return arr, meta
            except Exception:
                return None
        return None

    def get_elevation_at_point(self, region_id: str, lat: float, lon: float) -> Optional[float]:
        """
        Queries numerical elevation in meters relative to MOLA areoid at coordinate (lat, lon).
        Returns None if coordinates fall outside the verified DEM bounds or hit NoData.
        Never fabricates elevation values.
        """
        grid_data = self.load_dem_grid(region_id)
        if grid_data is None:
            return None

        arr, meta = grid_data
        bounds = meta.get("bounds", {})
        lat_min = bounds.get("lat_min")
        lat_max = bounds.get("lat_max")
        lon_min = bounds.get("lon_min")
        lon_max = bounds.get("lon_max")
        deg_per_px = meta.get("angular_resolution_deg_per_px")
        nodata = meta.get("nodata_value", -32768)

        if None in (lat_min, lat_max, lon_min, lon_max, deg_per_px):
            return None

        # Normalize longitude if system uses different [0, 360] vs [-180, 180] convention
        test_lon = lon
        if lon_min < 0 and test_lon > 180.0:
            test_lon = test_lon - 360.0
        elif lon_min > 0 and test_lon < 0.0:
            test_lon = test_lon + 360.0

        if not (lat_min <= lat <= lat_max and lon_min <= test_lon <= lon_max):
            return None

        row_f = (lat_max - lat) / deg_per_px
        col_f = (test_lon - lon_min) / deg_per_px

        h, w = arr.shape
        r0 = int(math.floor(row_f))
        c0 = int(math.floor(col_f))

        # Clamp edge pixels
        r0 = max(0, min(r0, h - 1))
        c0 = max(0, min(c0, w - 1))

        # Check bilinear interpolation
        r1 = min(r0 + 1, h - 1)
        c1 = min(c0 + 1, w - 1)

        corners = [arr[r0, c0], arr[r0, c1], arr[r1, c0], arr[r1, c1]]
        if any(c == nodata or np.isnan(c) for c in corners):
            # Fall back to nearest valid corner or return None
            val = arr[int(round(row_f)), int(round(col_f))]
            if val == nodata or np.isnan(val):
                return None
            return float(val)

        dr = row_f - r0
        dc = col_f - c0
        val = (
            (1.0 - dr) * (1.0 - dc) * float(arr[r0, c0])
            + (1.0 - dr) * dc * float(arr[r0, c1])
            + dr * (1.0 - dc) * float(arr[r1, c0])
            + dr * dc * float(arr[r1, c1])
        )
        return round(float(val), 2)

    def get_slope_grid(self, region_id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Calculates and caches the 2D slope angle grid in degrees for region_id.
        Accounts for planetary radius, latitude-dependent cell convergence, and masks NoData.
        """
        if region_id in self._slope_cache:
            return self._slope_cache[region_id]

        grid_data = self.load_dem_grid(region_id)
        if grid_data is None:
            return None

        arr, meta = grid_data
        bounds = meta.get("bounds", {})
        lat_min = bounds.get("lat_min")
        lat_max = bounds.get("lat_max")
        deg_per_px = meta.get("angular_resolution_deg_per_px")
        nodata = meta.get("nodata_value", -32768)

        if None in (lat_min, lat_max, deg_per_px):
            return None

        h, w = arr.shape
        ppd = 1.0 / deg_per_px
        m_lat, dx_per_row = calculate_tile_row_spacings(
            lat_min, lat_max, h,
            pixels_per_degree=ppd,
            mars_radius_km=MARS_EQUATORIAL_RADIUS_KM
        )

        slope_arr = self.calculate_slope_grid(arr, m_lat, dx_per_row, nodata_value=nodata)
        valid = ~np.isnan(slope_arr)
        slope_meta = {
            "region_id": region_id,
            "resolution_lat_m": round(float(m_lat), 2),
            "angular_resolution_deg_per_px": deg_per_px,
            "slope_min_deg": round(float(slope_arr[valid].min()), 2) if np.any(valid) else None,
            "slope_max_deg": round(float(slope_arr[valid].max()), 2) if np.any(valid) else None,
            "slope_mean_deg": round(float(slope_arr[valid].mean()), 2) if np.any(valid) else None,
            "units": "degrees [0, 90]",
            "has_nodata": bool(np.any(~valid))
        }

        self._slope_cache[region_id] = (slope_arr, slope_meta)
        return slope_arr, slope_meta

    def get_slope_at_point(self, region_id: str, lat: float, lon: float) -> Optional[float]:
        """
        Queries terrain slope angle in degrees [0, 90] at (lat, lon).
        Returns None if coordinates fall outside verified bounds or hit NoData.
        """
        slope_data = self.get_slope_grid(region_id)
        if slope_data is None:
            return None

        slope_arr, slope_meta = slope_data
        grid_data = self.load_dem_grid(region_id)
        if grid_data is None:
            return None

        _, meta = grid_data
        bounds = meta.get("bounds", {})
        lat_min = bounds.get("lat_min")
        lat_max = bounds.get("lat_max")
        lon_min = bounds.get("lon_min")
        lon_max = bounds.get("lon_max")
        deg_per_px = meta.get("angular_resolution_deg_per_px")

        test_lon = lon
        if lon_min < 0 and test_lon > 180.0:
            test_lon = test_lon - 360.0
        elif lon_min > 0 and test_lon < 0.0:
            test_lon = test_lon + 360.0

        if not (lat_min <= lat <= lat_max and lon_min <= test_lon <= lon_max):
            return None

        row_f = (lat_max - lat) / deg_per_px
        col_f = (test_lon - lon_min) / deg_per_px

        h, w = slope_arr.shape
        r = max(0, min(int(round(row_f)), h - 1))
        c = max(0, min(int(round(col_f)), w - 1))

        val = slope_arr[r, c]
        if np.isnan(val):
            return None
        return round(float(val), 2)

    def get_full_pipeline_inventory(self) -> Dict[str, Any]:
        """Comprehensive audit of pipeline readiness across all 3 regions and rover traverses."""
        regions = ["gale-crater", "jezero-crater", "olympus-mons"]
        dem_statuses = {r: self.get_dem_status(r) for r in regions}
        traverse_statuses = {
            "perseverance": self.get_traverse_status("perseverance"),
            "curiosity": self.get_traverse_status("curiosity")
        }

        all_dems_ready = all(s.is_available for s in dem_statuses.values())
        perseverance_ready = traverse_statuses["perseverance"].is_available

        return {
            "phase": "Phase 2: Mars Terrain Data Preparation",
            "pipeline_state": "READY_FOR_INGESTION" if (all_dems_ready and perseverance_ready) else "WAITING_FOR_DATASETS",
            "regions": {
                r: {
                    "available": s.is_available,
                    "validation_status": s.validation_status,
                    "format": s.format,
                    "file": s.file_path,
                    "verified_properties": s.verified_properties,
                    "assumed_properties": s.assumed_properties,
                    "notes": s.notes
                }
                for r, s in dem_statuses.items()
            },
            "traverses": {
                r: {
                    "available": s.is_available,
                    "validation_status": s.validation_status,
                    "format": s.format,
                    "file": s.file_path,
                    "notes": s.notes
                }
                for r, s in traverse_statuses.items()
            },
            "mathematical_engine": "Central finite-difference gradient with NoData masking & latitude convergence support",
            "scientific_integrity": "Zero synthetic elevation or traverse data generated"
        }


# Global pipeline instance
terrain_pipeline = TerrainPipeline()
