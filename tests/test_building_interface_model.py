from __future__ import annotations

import json

from lat_ces.building.model import BuildingModel, Level, Roof
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.project_spec import LevelProjectSpec, WallConstructionSpec
from lat_ces.building.workflow import BuildingWorkflow


def test_building_model_has_canonical_roof_and_level_properties() -> None:
    model = BuildingModel(name="Test objekat")
    level = model.add_level(
        Level(
            name="Prizemlje",
            elevation=0.0,
            height=2.8,
            length_m=10.0,
            width_m=8.0,
            wall_construction="Blok 25",
            insulation="Mineralna vuna 15 cm",
            cladding="Fasadni sistem",
            joinery="PVC / troslojno staklo",
        )
    )
    roof = model.set_roof(
        Roof(
            roof_type="Dvovodni",
            construction="Drvena krovna konstrukcija",
            covering="Crijep",
            substructure="Letve + kontraletve",
            support="AB serklaž",
            length_m=10.0,
            width_m=8.0,
            slope_deg=35.0,
            height_m=2.5,
        )
    )

    assert level.length_m == 10.0
    assert level.width_m == 8.0
    assert level.insulation == "Mineralna vuna 15 cm"
    assert level.cladding == "Fasadni sistem"
    assert level.joinery == "PVC / troslojno staklo"
    assert model.roof is roof
    assert model.roof.slope_deg == 35.0
    assert model.validate() == []


def test_workflow_level_and_roof_data_survive_json_roundtrip(tmp_path) -> None:
    workflow = BuildingWorkflow(model=BuildingModel(name="Roundtrip"))
    workflow.set_floor_count(1)
    spec = LevelProjectSpec(
        name="Prizemlje",
        height_m=2.9,
        length_m=10.0,
        width_m=8.0,
        construction=WallConstructionSpec(
            block_brand="Blok 25",
            wall_thickness_m=0.25,
            insulation_type="Mineralna vuna",
            insulation_thickness_m=0.15,
            exterior_cladding="Fasadni sistem",
        ),
        cladding="Glet + boja",
        finalized=True,
    )
    workflow.set_level_spec(0, spec)
    workflow.set_roof(
        "Dvovodni",
        2.5,
        construction="Drvena konstrukcija",
        covering="Crijep",
        substructure="Letve",
        support="AB serklaž",
        length_m=10.0,
        width_m=8.0,
        slope_deg=35.0,
    )

    path = tmp_path / "project.json"
    save_workflow(workflow, path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "LAT-CES-BUILDING-7"

    restored = load_workflow(path)
    level = next(iter(restored.model.levels.values()))
    assert level.height == 2.9
    assert level.length_m == 10.0
    assert level.width_m == 8.0
    assert level.insulation == "Mineralna vuna"
    assert level.cladding == "Glet + boja"
    assert restored.model.roof is not None
    assert restored.model.roof.covering == "Crijep"
    assert restored.model.roof.slope_deg == 35.0
