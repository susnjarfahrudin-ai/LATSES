from __future__ import annotations

from types import SimpleNamespace

from examples.test_house_115x8_model import build_test_house
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


class _TextSink:
    def configure(self, **_kwargs):
        return None

    def delete(self, *_args):
        return None

    def insert(self, *_args):
        return None


def test_engineering_summary_uses_exact_workflow_model() -> None:
    model = build_test_house()
    workflow = SimpleNamespace(model=model)
    app = SimpleNamespace(workflow=workflow, calculation_output=_TextSink())
    app._refresh_mep_tab = lambda: None

    CompleteBuildingWorkspaceApp._calculate_building_report(app)

    assert app.workflow.model is model
    assert model.building_engineering_report is not None
    assert model.building_engineering_report.results
    assert {result.building_model_id for result in model.building_engineering_report.results} == {model.model_id}

    assert len(model.levels) == 2
    assert sum(level.floor_plan.wall_count for level in model.levels.values()) == 8
    assert len(model.mep_registry.all_ventilation_openings) == 32
    assert len(model.mep_registry.all_heating_zones) == 2
    assert len(model.mep_registry.all_heating_circuits) == 2
