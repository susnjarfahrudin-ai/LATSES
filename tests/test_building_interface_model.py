from __future__ import annotations

import json

from lat_ces.building.model import BuildingModel
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.project_spec import LevelProjectSpec, WallConstructionSpec
from lat_ces.building.workflow import BuildingWorkflow


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
    assert payload["schema"] == "LAT-CES-BUILDING-8"
    assert payload["model"]["product_bindings"] == []

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
    assert restored.model.product_bindings.all() == ()
