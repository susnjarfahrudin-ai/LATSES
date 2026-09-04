import pytest

from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import Room
from lat_ces.building.underfloor_routing import route_room_serpentine


@pytest.fixture
def room() -> Room:
    return Room(
        name="UFH test room",
        footprint=Box3D(
            origin=Point3D(0.0, 0.0, 0.0),
            length=4.0,
            width=3.0,
            height=2.8,
        ),
    )


def test_underfloor_route_is_deterministic_and_inside_room(room: Room) -> None:
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


def test_underfloor_route_spacing_must_be_positive(room: Room) -> None:
    with pytest.raises(ValueError):
        route_room_serpentine(room, spacing_m=0.0)
