import pytest

from lat_ces.building_model import (
    BuildingConcept,
    LevelKind,
    MEPSystem,
    RoofCover,
    RoofCoverSpec,
    RoofModel,
    RoofShape,
    RoofStructure,
    RoofSubstructure,
    RoofSupport,
    StructuralLoadInput,
    SystemNode,
)


def make_concept() -> BuildingConcept:
    model = BuildingConcept("Test house")
    model.add_level("ground", LevelKind.GROUND, 10.0, 8.0, 2.8)
    model.add_level("floor1", LevelKind.FLOOR, 10.0, 8.0, 2.7)
    model.add_room("kitchen", "ground", 4.0, 3.5)
    model.add_room("bedroom", "floor1", 4.0, 3.5)
    model.add_system_node(SystemNode("boiler", MEPSystem.HEATING, "Boiler room", "ground"))
    return model


def test_basic_model_owns_levels_rooms_and_volume():
    model = make_concept()
    assert model.level_volume_m3("ground") == pytest.approx(224.0)
    assert model.total_volume_m3() == pytest.approx(440.0)
    assert model.nodes_for(MEPSystem.HEATING)[0].id == "boiler"


def test_roof_catalog_recommendation_is_not_silent_design_input():
    cover = RoofCoverSpec(
        cover=RoofCover.TILE,
        manufacturer="Example Manufacturer",
        product="Example Tile",
        recommended_pitch_deg=22.0,
        minimum_pitch_deg=17.0,
        mass_kg_m2=45.0,
        provenance=("manufacturer-datasheet:example",),
    )
    roof = RoofModel(
        length_m=10.0,
        width_m=8.0,
        shape=RoofShape.GABLE,
        support=RoofSupport.RC_SLAB,
        structure=RoofStructure.TIMBER_BEAMS,
        substructure=RoofSubstructure.COUNTER_BATTENS_BATTENS,
        cover=cover,
    )
    assert roof.plan_area_m2 == pytest.approx(80.0)
    assert roof.effective_pitch_deg() == 22.0
    assert roof.cover.provenance


def test_explicit_pitch_overrides_catalog_recommendation():
    cover = RoofCoverSpec(cover=RoofCover.SHEET_METAL, recommended_pitch_deg=12.0)
    roof = RoofModel(
        length_m=10.0,
        width_m=8.0,
        shape=RoofShape.MONOPITCH,
        support=RoofSupport.STEEL,
        structure=RoofStructure.STEEL_PROFILES,
        substructure=RoofSubstructure.BATTENS,
        cover=cover,
        pitch_deg=18.0,
    )
    assert roof.effective_pitch_deg() == 18.0


def test_structural_loads_are_explicit_and_provenanced():
    loads = StructuralLoadInput(
        snow_kN_m2=1.2,
        rain_kN_m2=0.35,
        wind_kN_m2=0.8,
        imposed_kN_m2=0.5,
        standard_reference="EN 1991 family / project national annex",
        provenance=("project-input",),
    )
    model = make_concept()
    model.structural_loads = loads
    assert model.structural_loads.snow_kN_m2 == 1.2
    assert model.structural_loads.provenance == ("project-input",)


def test_invalid_geometry_is_rejected():
    with pytest.raises(ValueError):
        BuildingConcept("x").add_level("ground", LevelKind.GROUND, 0, 8, 2.8)
