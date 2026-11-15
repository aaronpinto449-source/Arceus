"""
Unit tests for ARES Route Solver.
Tests geometry-only estimation, numerical DEM terrain-aware evaluation,
safety advisories, geodetic math, and boundary validation.
"""

import math
import unittest

from backend.app.core.route_models import (
    Coordinate,
    RoutePlanRequest,
    RoutePriority,
    RoverType,
)
from backend.app.core.route_solver import haversine_km, plan_route


class TestRouteSolver(unittest.TestCase):

    def test_geometry_only_fallback_honest_estimates(self):
        """When DEM is bypassed or absent, all fields report honest unavailable provenance."""
        for priority in list(RoutePriority):
            start = Coordinate(lat=-4.591, lon=137.441)
            destination = Coordinate(lat=-5.079, lon=137.849)
            request = RoutePlanRequest(
                region_id="gale-crater",
                start=start,
                destination=destination,
                priority=priority,
                use_dem=False,
            )

            response = plan_route(request)

            self.assertEqual(response.algorithm_used.value, "HAVERSINE-DIRECT")
            self.assertEqual(len(response.coordinates), 2)
            self.assertEqual(len(response.segments), 1)
            self.assertEqual((response.coordinates[0].lat, response.coordinates[0].lon), (-4.591, 137.441))
            self.assertEqual((response.coordinates[1].lat, response.coordinates[1].lon), (-5.079, 137.849))
            self.assertFalse(response.coordinates[0].is_poi)
            self.assertFalse(response.coordinates[1].is_poi)
            self.assertAlmostEqual(response.total_distance_km, response.segments[0].distance_km, places=3)
            self.assertFalse(response.data_source.dem_available)
            self.assertFalse(response.data_source.mola_tiles_used)
            self.assertFalse(response.terrain_cost.supported)
            self.assertFalse(response.slope_data.supported)
            self.assertFalse(response.hazard_exposure.supported)
            self.assertFalse(response.elevation_profile.supported)

    def test_dem_terrain_aware_evaluation(self):
        """When local DEM is present, elevation profile, slope analysis, and terrain cost are populated."""
        start = Coordinate(lat=-4.591, lon=137.441)
        destination = Coordinate(lat=-5.079, lon=137.849)
        request = RoutePlanRequest(
            region_id="gale-crater",
            start=start,
            destination=destination,
            priority=RoutePriority.BALANCED,
            use_dem=True,
        )

        response = plan_route(request)

        self.assertEqual(response.algorithm_used.value, "HAVERSINE-DIRECT")
        self.assertEqual(len(response.coordinates), 2)
        self.assertEqual(len(response.segments), 1)
        # Verify submitted endpoints are preserved exactly
        self.assertEqual((response.coordinates[0].lat, response.coordinates[0].lon), (-4.591, 137.441))
        self.assertEqual((response.coordinates[1].lat, response.coordinates[1].lon), (-5.079, 137.849))
        self.assertTrue(response.data_source.dem_available)
        self.assertTrue(response.elevation_profile.supported)
        self.assertTrue(response.slope_data.supported)
        self.assertTrue(response.terrain_cost.supported)
        self.assertFalse(response.hazard_exposure.supported)

        # Elevation range check in Gale Crater (Bradbury Landing to Mount Sharp flank)
        self.assertLess(response.elevation_profile.min_elevation_m, -4000.0)
        self.assertGreater(response.elevation_profile.max_elevation_m, 0.0)
        self.assertGreater(len(response.elevation_profile.samples), 10)

        # Slope metrics
        self.assertGreater(response.slope_data.mean_slope_deg, 0.0)
        self.assertGreater(response.slope_data.max_slope_deg, 15.0)
        self.assertTrue(response.slope_data.steep_slopes_detected)

    def test_safety_priority_adds_survey_warning_without_claiming_safety(self):
        """Safety priority issues orbital survey warnings and leaves hazard classification unavailable."""
        response = plan_route(RoutePlanRequest(
            region_id="gale-crater",
            start=Coordinate(lat=-4.59, lon=137.44),
            destination=Coordinate(lat=-5.08, lon=137.85),
            priority=RoutePriority.SAFETY,
            use_dem=False,
        ))

        self.assertTrue(any("No terrain safety validation" in warning for warning in response.warnings))
        self.assertEqual(response.hazard_exposure.provenance.value, "UNAVAILABLE")

    def test_haversine_one_degree_at_equator_uses_mars_radius(self):
        """Mars circumference ~21,296 km -> 1 deg at equator ~59.16 km."""
        dist = haversine_km(0, 0, 0, 1)
        self.assertAlmostEqual(dist, 59.16, delta=0.05)

    def test_solver_rejects_coordinates_outside_region(self):
        """Coordinates outside region bounding box raise ValueError."""
        request = RoutePlanRequest(
            region_id="gale-crater",
            start=Coordinate(lat=10, lon=137.44),
            destination=Coordinate(lat=-5.08, lon=137.85),
            priority=RoutePriority.BALANCED,
        )

        with self.assertRaises(ValueError) as ctx:
            plan_route(request)
        self.assertIn("outside region", str(ctx.exception))

    def test_solver_rejects_identical_coordinates(self):
        """Start and destination at same point must be rejected."""
        with self.assertRaises(ValueError):
            RoutePlanRequest(
                region_id="gale-crater",
                start=Coordinate(lat=-4.59, lon=137.44),
                destination=Coordinate(lat=-4.59, lon=137.44),
                priority=RoutePriority.BALANCED,
            )


if __name__ == "__main__":
    unittest.main()
