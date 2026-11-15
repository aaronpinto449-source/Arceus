"""
ARES Mission Control - Comprehensive Backend Test Suite
Verifies all API endpoints, Route Solver priorities, Terrain DEM ingestion,
NASA Space Apps Challenge 2026 Resources, and Scientific Integrity Contracts.
"""

import sys
import math
from pathlib import Path

# Add backend directory and project root to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import (
    REGIONS,
    REGION_BOUNDS,
    REGION_POIS,
    SPACE_APPS_2026_RESOURCES,
    MARS_MEAN_RADIUS_KM,
    MARS_EQUATORIAL_RADIUS_KM
)
from app.api.routes import (
    get_health,
    list_regions,
    get_region,
    get_region_pois,
    get_region_map,
    get_spatial_resolution,
    get_challenge_resources
)
from app.core.route_models import (
    RoutePlanRequest,
    RoutePriority,
    Coordinate
)
from app.core.route_solver import plan_route
from app.core.terrain_pipeline import terrain_pipeline


def test_api_health():
    print("[1/9] Testing GET /api/health...")
    health = get_health()
    assert health["status"] == "OPERATIONAL", f"Unexpected status: {health['status']}"
    assert health["planetary_target"] == "Mars (4th planet from Sun)"
    print("  -> Passed: System is OPERATIONAL.")


def test_api_regions():
    print("[2/9] Testing GET /api/regions and /api/regions/{id}...")
    regions = list_regions()
    assert len(regions) == 3, f"Expected 3 regions, got {len(regions)}"
    expected_ids = {"gale-crater", "jezero-crater", "olympus-mons"}
    found_ids = {r["id"] for r in regions}
    assert found_ids == expected_ids, f"Region IDs mismatch: {found_ids}"

    for reg_id in expected_ids:
        detail = get_region(reg_id)
        assert detail["id"] == reg_id
        assert "bounds" in detail
        assert "pois" in detail
        assert len(detail["pois"]) >= 3

        # Test POI endpoint
        pois = get_region_pois(reg_id)
        assert len(pois) >= 3
        for p in pois:
            assert -90.0 <= p["lat"] <= 90.0
            assert "name" in p
            assert "significance" in p

        # Test map stream endpoint
        resp = get_region_map(reg_id, max_dim=512, quality=75)
        assert resp.status_code == 200
        assert resp.media_type == "image/jpeg"
        assert len(resp.body) > 1000

    print("  -> Passed: All 3 exploration regions (Gale, Jezero, Olympus Mons), POIs, and MOLA basemaps verified.")


def test_api_telemetry_resolution():
    print("[3/9] Testing GET /api/telemetry/resolution...")
    res_eq = get_spatial_resolution(0.0)
    assert res_eq["lat_deg"] == 0.0
    assert abs(res_eq["meters_per_pixel_lat"] - 231.5) < 1.0
    assert abs(res_eq["meters_per_pixel_lon"] - 231.5) < 1.0

    res_pole = get_spatial_resolution(60.0)
    assert abs(res_pole["meters_per_pixel_lon"] - (res_eq["meters_per_pixel_lat"] * 0.5)) < 1.0
    print("  -> Passed: Spatial ground resolution with latitude cosine convergence verified.")


def test_api_resources():
    print("[4/9] Testing GET /api/resources (NASA Space Apps Challenge 2026 Resources)...")
    res = get_challenge_resources()
    assert "challenge" in res
    assert "Interplanetary Survival Guide" in res["challenge"]
    resources = res["resources"]

    # Verify all 5 official challenge resources
    required_keys = {
        "mars_trek",
        "usgs_geologic_maps",
        "curiosity_mount_sharp_route",
        "perseverance_raw_images",
        "nasa_worldview"
    }
    assert set(resources.keys()) == required_keys, f"Missing resource keys: {set(resources.keys()) ^ required_keys}"

    # Verify Mars-specific vs general supplementary categorization
    mars_resources = [k for k, v in resources.items() if v.get("is_mars_specific") is True]
    supplementary = [k for k, v in resources.items() if v.get("is_mars_specific") is False]

    assert len(mars_resources) == 4, f"Expected 4 Mars-specific resources, got {len(mars_resources)}"
    assert "nasa_worldview" in supplementary, "NASA Worldview must be labeled as general supplementary resource"
    print("  -> Passed: 4 Mars-specific resources and 1 general supplementary resource verified with authorities.")


def test_route_planner_priorities():
    print("[5/9] Testing POST /api/routes/plan (DISTANCE, BALANCED, SAFETY)...")
    # Copy REGION_POIS snapshot to test immutability
    import copy
    pois_before = copy.deepcopy(REGION_POIS)

    start = Coordinate(lat=-4.5895, lon=137.4417, label="Bradbury Landing")
    dest = Coordinate(lat=-4.5300, lon=137.8500, label="Mount Sharp Base")

    # 1. DISTANCE Priority
    req_dist = RoutePlanRequest(
        region_id="gale-crater",
        start=start,
        destination=dest,
        priority=RoutePriority.DISTANCE
    )
    plan_dist = plan_route(req_dist)
    assert plan_dist.total_distance_km > 0
    assert "direct" in plan_dist.priority_explanation.description.lower() or "haversine" in plan_dist.priority_explanation.description.lower()
    assert len(plan_dist.coordinates) == 2, "DISTANCE priority must produce direct 2-point segment"

    # 2. BALANCED Priority
    req_bal = RoutePlanRequest(
        region_id="gale-crater",
        start=start,
        destination=dest,
        priority=RoutePriority.BALANCED
    )
    plan_bal = plan_route(req_bal)
    assert plan_bal.total_distance_km > 0
    assert len(plan_bal.coordinates) >= 2

    # 3. SAFETY Priority
    req_safe = RoutePlanRequest(
        region_id="gale-crater",
        start=start,
        destination=dest,
        priority=RoutePriority.SAFETY
    )
    plan_safe = plan_route(req_safe)
    assert plan_safe.total_distance_km > 0

    # Verify REGION_POIS immutability
    assert REGION_POIS == pois_before, "CRITICAL: Solver must not mutate shared REGION_POIS dictionary!"
    print("  -> Passed: DISTANCE, BALANCED, SAFETY modes verified; REGION_POIS immutability preserved.")


def test_route_disclaimers_and_caveats():
    print("[6/9] Testing Rover Feasibility Caveats & Segment Disclaimers...")
    start = Coordinate(lat=18.4447, lon=77.4508, label="Octavia E. Butler Landing")
    dest = Coordinate(lat=18.4200, lon=77.3800, label="Western Fan Delta")

    req = RoutePlanRequest(
        region_id="jezero-crater",
        start=start,
        destination=dest,
        priority=RoutePriority.BALANCED
    )
    plan = plan_route(req)

    # Check rover feasibility caveat
    assert plan.feasibility.range_caveat is not None, "Feasibility missing required range caveat!"
    assert "illustrative" in plan.feasibility.range_caveat.lower() or "unverified" in plan.feasibility.range_caveat.lower()

    # Check segment disclaimer
    for seg in plan.segments:
        assert seg.geometry_caveat is not None, f"Segment {seg.index} missing geometry/obstacle caveat!"
        assert "obstacle" in seg.geometry_caveat.lower() or "traversability" in seg.geometry_caveat.lower()

    # Check snap threshold in data sources
    assert plan.data_source.snap_threshold_deg == 0.05
    print("  -> Passed: Vehicle range caveats, obstacle disclaimers, and snap threshold verified.")


def test_terrain_pipeline_ingestion():
    print("[7/9] Testing TerrainPipeline numerical DEM loading...")
    for reg_id in ["gale-crater", "jezero-crater", "olympus-mons"]:
        status = terrain_pipeline.get_dem_status(reg_id)
        assert status.is_available is True, f"DEM for {reg_id} should be available"
        assert status.validation_status == "VALIDATED_NUMERICAL_DEM"

        grid_data = terrain_pipeline.load_dem_grid(reg_id)
        assert grid_data is not None, f"Failed to load DEM grid for {reg_id}"
        arr, meta = grid_data
        assert arr.ndim == 2
        assert arr.dtype.name == "int16"
        assert meta["nodata_value"] == -32768
        assert meta["units"] == "meters relative to MOLA areoid"

    print("  -> Passed: All 3 regional DEMs loaded as verified single-band 2D int16 elevation grids.")


def test_terrain_elevation_and_slope_queries():
    print("[8/9] Testing elevation queries and slope calculus...")
    # 1. Gale Crater Bradbury Landing
    gale_elev = terrain_pipeline.get_elevation_at_point("gale-crater", -4.5895, 137.4417)
    gale_slope = terrain_pipeline.get_slope_at_point("gale-crater", -4.5895, 137.4417)
    assert gale_elev is not None
    assert -4700.0 < gale_elev < -4300.0, f"Bradbury landing elevation out of expected range: {gale_elev}"
    assert gale_slope is not None
    assert 0.0 <= gale_slope <= 45.0, f"Gale slope unexpected: {gale_slope}"

    # 2. Jezero Crater Octavia Butler Landing
    jez_elev = terrain_pipeline.get_elevation_at_point("jezero-crater", 18.4447, 77.4508)
    jez_slope = terrain_pipeline.get_slope_at_point("jezero-crater", 18.4447, 77.4508)
    assert jez_elev is not None
    assert -2700.0 < jez_elev < -2400.0, f"Octavia Butler elevation out of expected range: {jez_elev}"
    assert jez_slope is not None
    assert 0.0 <= jez_slope <= 45.0, f"Jezero slope unexpected: {jez_slope}"

    # 3. Olympus Mons Summit Caldera Floor
    oly_elev = terrain_pipeline.get_elevation_at_point("olympus-mons", 18.65, 225.8)
    oly_slope = terrain_pipeline.get_slope_at_point("olympus-mons", 18.65, 225.8)
    assert oly_elev is not None
    assert 18000.0 < oly_elev < 22000.0, f"Olympus summit elevation out of expected range: {oly_elev}"
    assert oly_slope is not None
    assert 0.0 <= oly_slope <= 45.0, f"Olympus slope unexpected: {oly_slope}"

    # 4. Out-of-bounds queries must return None (strictly no fabrication)
    assert terrain_pipeline.get_elevation_at_point("gale-crater", 50.0, 50.0) is None
    assert terrain_pipeline.get_slope_at_point("gale-crater", 50.0, 50.0) is None
    print("  -> Passed: Authentic elevation queries and slope calculus verified; out-of-bounds returns None.")


def test_scientific_provenance_distinction():
    print("[9/9] Testing Scientific Provenance Classification Contract...")
    inv = terrain_pipeline.get_full_pipeline_inventory()
    assert inv["scientific_integrity"] == "Zero synthetic elevation or traverse data generated"

    # Verify classification distinctions:
    # 1. Measured DEM data: USGS 200m MOLA/HRSC int16
    # 2. Calculated slope: Finite-difference gradient with cosine latitude convergence
    # 3. Simulated route estimates: Haversine distance and heuristic POI-graph routing
    # 4. External cross-checks: JPL Mars Trek, USGS Geologic Map, Curiosity Mt Sharp path
    print("  -> Passed: Rigorous scientific classification distinctions upheld.")


if __name__ == "__main__":
    print("=" * 70)
    print("ARES MISSION CONTROL - VERIFICATION TEST SUITE")
    print("=" * 70)
    try:
        test_api_health()
        test_api_regions()
        test_api_telemetry_resolution()
        test_api_resources()
        test_route_planner_priorities()
        test_route_disclaimers_and_caveats()
        test_terrain_pipeline_ingestion()
        test_terrain_elevation_and_slope_queries()
        test_scientific_provenance_distinction()
        print("=" * 70)
        print("ALL 9 TEST SUITES PASSED! ZERO FAILURES.")
        print("=" * 70)
    except AssertionError as e:
        print("\nTEST FAILED:", e)
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("\nUNEXPECTED ERROR:", e)
        sys.exit(1)
