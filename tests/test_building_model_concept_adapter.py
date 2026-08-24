import pytest

from lat_ces.building_model import (
    BuildingModel,
    Level,
    Material,
    Opening,
    Room,
    Wall,
    LevelKind,
    to_concept,
)


def test_adapter_preserves_level_room_volume_and_openings():
    model = BuildingModel("Legacy")
    level = Level("ground", "Prizemlje", 10.0, 8.0, 2.8)
    level.add_room(Room("living", "Dnevni boravak", 5.0, 4.0, 2.8))
    wall = Wall("south", 10.0, 0.25, 2.8)
    wall.add_opening(Opening("window", 1.5, 1.4, 0.9, 2.0))
    level.add_wall(wall)
    model.add_level(level)
    model.materials["wall"] = Material("Brick", density_kg_m3=800)

    concept = to_concept(model)
    assert concept.levels["ground"] is LevelKind.GROUND
    assert concept.level_volume_m3("ground") == pytest.approx(224.0)
    assert concept.rooms["living"] == ("ground", 5.0, 4.0)
    assert len(concept.openings) == 1
    assert concept.materials["wall"].density_kg_m3 == 800
