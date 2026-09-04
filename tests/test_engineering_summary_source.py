from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "test_house_115x8_model.py"
_SPEC = importlib.util.spec_from_file_location("test_house_115x8_model", _FIXTURE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load reference-house fixture: {_FIXTURE_PATH}")
_REFERENCE_HOUSE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_REFERENCE_HOUSE)
build_test_workflow_house = _REFERENCE_HOUSE.build_test_workflow_house


class _TextSink:
    def configure(self, **_kwargs):
        return None

    def delete(self, *_args):
        return None

    def insert(self, *_args):
        return None


def test_engineering_summary_uses_exact_workflow_model() -> None:
    model = build_test_workflow_house()
    workflow = SimpleNamespace(model=model)
    app = SimpleNamespace(workflow=workflow, calculation_output=_TextSink())
    app._refresh_mep_tab = lambda: None

    CompleteBuildingWorkspaceApp._calculate_building_report(app)

    assert app.workflow.model is model
    assert model.building_engineering_report is not None
    assert model.building_engineering_report.results
    assert {result.building_model_id for result in model.building_engineering_report.results} == {model.model_id}

    mep = ensure_mep_registry(model)
    assert len(model.levels) == 2
    assert sum(level.floor_plan.wall_count for level in model.levels.values()) == 8
    assert len(mep.all_ventilation_openings) == 32
    assert len(mep.all_underfloor_systems) == 2
    assert len(mep.all_underfloor_circuits) == 2
