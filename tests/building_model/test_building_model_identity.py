from lat_ces.building_model.core import BuildingModel
from lat_ces.building_model.example_model import make_small_reference_house


def test_building_model_has_stable_canonical_identity():
    model = BuildingModel(name="Test House")
    assert model.building_model_id.startswith("BLDG-")
    assert model.building_model_id == model.building_model_id


def test_reference_house_preserves_its_canonical_identity():
    model = make_small_reference_house()
    assert model.building_model_id.startswith("BLDG-")
    assert model.building_model_id == model.building_model_id


def test_existing_constructor_api_remains_compatible():
    model = BuildingModel("Test House", {}, {}, "all_walls")
    assert model.name == "Test House"
    assert model.load_bearing_mode == "all_walls"
    assert model.building_model_id.startswith("BLDG-")


def test_independent_models_have_distinct_identities():
    first = BuildingModel(name="House A")
    second = BuildingModel(name="House B")
    assert first.building_model_id != second.building_model_id
