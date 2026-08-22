import pytest

from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.reference_house_project import build_reference_house_workflow


def test_reference_house_has_independent_levels_in_one_workflow():
    workflow = build_reference_house_workflow()
    assert [level.name for level in workflow.model.levels.values()] == ["Prizemlje", "Sprat 1", "Sprat 2"]

    ground = workflow.set_active_level(next(level_id for level_id, level in workflow.model.levels.items() if level.name == "Prizemlje"))
    second = workflow.set_active_level(next(level_id for level_id, level in workflow.model.levels.items() if level.name == "Sprat 2"))

    original_second_height = second.height
    ground.height = 3.10

    assert ground.height == pytest.approx(3.10)
    assert second.height == pytest.approx(original_second_height)
    assert workflow.active_level is second


def test_reference_house_round_trip_preserves_level_separation(tmp_path):
    workflow = build_reference_house_workflow()
    first_level = next(iter(workflow.model.levels.values()))
    workflow.set_active_level(first_level.level_id)
    first_level.dead_load_kpa = 2.75

    path = save_workflow(workflow, tmp_path / "reference_house.latses.json")
    restored = load_workflow(path)

    assert list(restored.model.levels) == list(workflow.model.levels)
    assert restored.active_level_id == workflow.active_level_id
    assert restored.model.levels[first_level.level_id].dead_load_kpa == pytest.approx(2.75)
    assert restored.model.levels[first_level.level_id].name == "Prizemlje"
    assert restored.model.levels[next(iter(list(restored.model.levels)[1:]))].name == "Sprat 1"
