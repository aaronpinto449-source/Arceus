import pytest

from backend.app.core.route_models import (
    Coordinate,
    RoutePlanRequest,
    RoutePriority,
)
from backend.app.core.route_solver import haversine_km, plan_route


@pytest.mark.parametrize("priority", list(RoutePriority))
def test_route_priorities_return_honest_geometry_only_estimate(priority):
    start = Coordinate(lat=-4.591, lon=137.441)
    destination = Coordinate(lat=-5.079, lon=137.849)
    request = RoutePlanRequest(
        region_id="gale-crater",
        start=start,
        destination=destination,
        priority=priority,
    )

    response = plan_route(request)

    assert response.algorithm_used == "HAVERSINE-DIRECT"
    assert len(response.coordinates) == 2
    assert len(response.segments) == 1
    assert (response.coordinates[0].lat, response.coordinates[0].lon) == (-4.591, 137.441)
    assert (response.coordinates[1].lat, response.coordinates[1].lon) == (-5.079, 137.849)
    assert response.coordinates[0].is_poi is False
    assert response.coordinates[1].is_poi is False
    assert response.total_distance_km == pytest.approx(response.segments[0].distance_km)
    assert response.data_source.dem_available is False
    assert response.data_source.mola_tiles_used is False
    assert response.terrain_cost.supported is False
    assert response.slope_data.supported is False
    assert response.hazard_exposure.supported is False
    assert response.elevation_profile.supported is False


def test_safety_priority_adds_survey_warning_without_claiming_safety():
    response = plan_route(RoutePlanRequest(
        region_id="gale-crater",
        start=Coordinate(lat=-4.59, lon=137.44),
        destination=Coordinate(lat=-5.08, lon=137.85),
        priority=RoutePriority.SAFETY,
    ))

    assert any("No terrain safety validation" in warning for warning in response.warnings)
    assert response.hazard_exposure.provenance.value == "UNAVAILABLE"


def test_haversine_one_degree_at_equator_uses_mars_radius():
    assert haversine_km(0, 0, 0, 1) == pytest.approx(59.16, abs=0.02)


def test_solver_rejects_coordinates_outside_region():
    request = RoutePlanRequest(
        region_id="gale-crater",
        start=Coordinate(lat=10, lon=137.44),
        destination=Coordinate(lat=-5.08, lon=137.85),
        priority=RoutePriority.BALANCED,
    )

    with pytest.raises(ValueError, match="outside region"):
        plan_route(request)
