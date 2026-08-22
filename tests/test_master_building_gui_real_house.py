import tkinter as tk

from lat_ces.gui_master import MasterBuildingWorkspaceApp


def test_master_gui_loads_reference_house_and_runs_engineering_report(monkeypatch):
    """Exercise the real desktop callback chain without blocking CI on modal dialogs."""
    monkeypatch.setattr("lat_ces.gui.messagebox.showwarning", lambda *args, **kwargs: "ok")
    monkeypatch.setattr("lat_ces.gui.messagebox.showinfo", lambda *args, **kwargs: "ok")

    app = MasterBuildingWorkspaceApp()
    try:
        app._load_reference_house()

        model = app.workflow.model
        assert model.name
        assert len(model.levels) == 3
        assert sum(len(level.rooms) for level in model.levels.values()) > 0
        assert model.roof is not None
        assert len(model.materials) >= 2

        # These are the actual GUI commands wired to the BuildingModel.
        app._show_view("plan")
        app._show_view("section")
        app._show_view("3d")
        app._run_master_validation()
        app._show_engineering_report()

        assert "Building Model" in app.status_var.get() or "Model" in app.status_var.get()
        report = model.building_engineering_report
        assert report.result_count > 0
        assert report.calculated_count > 0
        assert report.quantities.floor_area_m2 > 0.0
        assert report.structural.status
        assert report.thermal.status
        assert report.electrical.status
        assert report.total_ventilation_flow_m3_h > 0.0
        assert report.total_heating_load_w > 0.0
        assert report.total_water_pressure_drop_pa > 0.0

        # Verify that the GUI actually rendered the engineering command result.
        output = app.calculation_output.get("1.0", "end")
        assert "Status:" in output
        assert "Rezultata:" in output
        assert "Ventilacija:" in output
        assert "Grijanje:" in output
        assert "Voda:" in output
    finally:
        app.destroy()
        try:
            tk._default_root = None
        except Exception:
            pass
