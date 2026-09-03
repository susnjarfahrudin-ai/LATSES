import os

import pytest

from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


def _has_canvas_content(app: CompleteBuildingWorkspaceApp) -> bool:
    app.update_idletasks()
    return bool(app.canvas.find_all())


def test_reference_house_visual_acceptance_sequence() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") != "1":
        pytest.skip("Windows packaged GUI acceptance only")

    app = CompleteBuildingWorkspaceApp()
    try:
        app.open_reference_house()
        model = app.workflow.model
        assert model.levels, "Reference House must contain at least one level"

        # 1. Reference House → 2. Tlocrt
        app.view_step.set(3)
        app.goto_step()
        assert _has_canvas_content(app), "Tlocrt must render visible BuildingModel content"
        assert app.active_level.rooms, "Tlocrt must expose canonical Room objects"

        # 3. Presjek
        app.view_step.set(4)
        app.goto_step()
        assert _has_canvas_content(app), "Presjek must render visible BuildingModel geometry"

        # 4. 3D
        app.view_step.set(5)
        app.goto_step()
        assert _has_canvas_content(app), "3D must render visible BuildingModel geometry"

        # 5. Provjera
        findings = app.workflow.validate()
        assert not findings, f"Reference House must be valid: {findings}"

        # 6. Izvještaj / Engineering Summary
        app.refresh_engineering_summary()
        summary = app.engineering_summary.get("1.0", "end").strip()
        assert "STATIKA" in summary
        assert "TERMIKA" in summary
        assert "KOLIČINE" in summary
        assert "MEP" in summary

        # 7. Materijali / canonical product-material inspector
        assert model.materials, "Reference House must expose canonical Material/Product records"
        app.show_canonical_model_inspector()
        app.update_idletasks()
        inspector_windows = [
            child for child in app.winfo_children() if child.winfo_class() == "Toplevel"
        ]
        assert inspector_windows, "Model Inspector must open for Material/Product inspection"
    finally:
        app.destroy()
