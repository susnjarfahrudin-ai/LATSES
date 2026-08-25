import pytest

from lat_ces.reference_house import ReferenceHouse
from lat_ces.reference_house_preview_geometry import derive_preview_geometry


def test_preview_geometry_preserves_declared_positive_room_areas():
    house = ReferenceHouse.default()
    levels = derive_preview_geometry(house)

    source_by_level = {
        level["id"]: {
            room["id"]: room.get("area_m2", 0.0)
            for room in level["rooms"]
            if room.get("height_m", 0.0) > 0.0 and room.get("area_m2", 0.0) > 0.0
        }
        for level in house.levels
    }

    for level in levels:
        assert level.status == "DERIVED_PREVIEW"
        assert level.length_m == pytest.approx(12.0)
        assert level.width_m == pytest.approx(10.0)
        for room in level.rooms:
            assert room.status == "DERIVED_PREVIEW"
            assert room.engineering_usable is False
            assert room.area_m2 == pytest.approx(source_by_level[level.level_id][room.room_id])
            assert room.x_m >= 0.0
            assert room.y_m >= 0.0
            assert room.x_m + room.length_m <= level.length_m + 1e-9
            assert room.y_m + room.width_m <= level.width_m + 1e-9


def test_preview_geometry_does_not_change_reference_house_metrics():
    house = ReferenceHouse.default()
    before = house.summary()
    derive_preview_geometry(house)
    after = house.summary()

    assert after.floor_area_m2 == before.floor_area_m2
    assert after.volume_m3 == pytest.approx(before.volume_m3)
