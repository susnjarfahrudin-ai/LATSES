import pytest

from lat_ces.building_model.reference_house_adapter import (
    ReferenceHouseGeometryError,
    map_reference_house_to_building_model,
)
from lat_ces.reference_house import ReferenceHouse


def test_reference_house_strict_mapping_rejects_invented_room_geometry():
    house = ReferenceHouse.default()

    with pytest.raises(ReferenceHouseGeometryError, match="room length/width geometry"):
        map_reference_house_to_building_model(house, strict_geometry=True)


def test_reference_house_non_strict_mapping_preserves_explicit_level_geometry_only():
    house = ReferenceHouse.default()

    model = map_reference_house_to_building_model(house, strict_geometry=False)

    assert model.name == house.data["name"]
    assert list(model.levels) == ["P", "S1", "S2", "S3"]
    assert all(level.length_m == 12.0 for level in model.levels.values())
    assert all(level.width_m == 10.0 for level in model.levels.values())
    assert all(level.height_m == 2.8 for level in model.levels.values())
    assert all(not level.rooms for level in model.levels.values())


def test_reference_house_fixture_metrics_remain_deterministic():
    house = ReferenceHouse.default()
    summary = house.summary()

    assert len(house.levels) == 4
    assert summary.floor_area_m2 == 454.0
    assert summary.volume_m3 == 1271.2
    assert summary.ventilation_m3_h == pytest.approx(1080.52)
