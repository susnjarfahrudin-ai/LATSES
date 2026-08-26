import pytest

from lat_ces.building.underfloor_routing import route_room_serpentine
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_underfloor_route_is_deterministic_and_inside_room() -> None:
    workflow = build_reference_house_workflow()
    level = next(iter(workflow.model.levels.values()))
    room = next(iter(level.rooms.values()))

    route_a = route_room_serpentine(room, spacing_m=0.15)
    route_b = route_room_serpentine(room, spacing_m=0.15)

    assert route_a == route_b
    assert route_a.status == "SCHEMATIC"
    assert route_a.length_m > 0
    assert route_a.spacing_m == 0.15
    assert route_a.points_m

    x0 = room.footprint.origin.x
    y0 = room.footprint.origin.y
    x1 = x0 + room.footprint.length
    y1 = y0 + room.footprint.width
    assert all(x0 <= x <= x1 and y0 <= y <= y1 and z == 0.0 for x, y, z in route_a.points_m)


def test_underfloor_route_spacing_must_be_positive() -> None:
    workflow = build_reference_house_workflow()
    room = next(iter(next(iter(workflow.model.levels.values())).rooms.values()))
    with pytest.raises(ValueError):
        route_room_serpentine(room, spacing_m=0.0)
