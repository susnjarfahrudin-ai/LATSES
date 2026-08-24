"""Functional packaged LAT-CES desktop entrypoint.

This layer keeps CompleteBuildingWorkspaceApp as the canonical GUI/model owner,
while adding real module actions and the deterministic ReferenceHouse showcase.
"""
from __future__ import annotations

import math
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from lat_ces.building.model import BuildingModel, Level, Roof
from lat_ces.building.orientation import BuildingOrientation
from lat_ces.building.workflow import BuildingWorkflow, make_envelope_floor_plan
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.reference_house import ReferenceHouse


class FunctionalLATCESApp(CompleteBuildingWorkspaceApp):
    """Packaged LAT-CES GUI with functional module navigation and reference house."""

    def __init__(self) -> None:
        self.reference_house: ReferenceHouse | None = None
        self.module_actions: ttk.Frame | None = None
        super().__init__()
        self.after_idle(self._install_functional_layer)

    def _install_functional_layer(self) -> None:
        if self.module_actions is not None:
            return
        shell = getattr(self, "shell_body", None)
        if shell is None:
            return
        action_bar = ttk.Frame(shell.master, padding=(14, 4))
        action_bar.pack(fill="x", before=shell, padx=0, pady=(2, 0))
        self.module_actions = action_bar
        self._wire_top_navigation()
        self._route_module("object")

    def _all_widgets(self, parent):
        for child in parent.winfo_children():
            yield child
            yield from self._all_widgets(child)

    def _wire_top_navigation(self) -> None:
        for widget in self._all_widgets(self):
            if not isinstance(widget, ttk.Button):
                continue
            label = widget.cget("text")
            key = {"OBJECT": "object", "MODEL": "model", "ANALYSIS": "analysis", "SYSTEMS": "systems", "ENERGY": "energy", "SERVICE": "service", "AI": "ai"}.get(label)
            if key:
                widget.configure(command=lambda selected=key: self._route_module(selected))

    def _clear_actions(self) -> None:
        if self.module_actions is None:
            return
        for child in self.module_actions.winfo_children():
            child.destroy()

    def _action(self, text: str, command) -> None:
        ttk.Button(self.module_actions, text=text, command=command).pack(side="left", padx=3)

    def _route_module(self, key: str) -> None:
        super()._select_nav(key)
        self._clear_actions()
        if key == "object":
            self._action("Referentna kuća", self.load_reference_house)
            self._action("Novi objekat", self.new_project)
            self._action("Učitaj projekat", self.load_project)
            self._action("Sačuvaj projekat", self.save_project)
            self._show_reference_card()
        elif key == "model":
            for text, step in (("Krov", 1), ("Sprat", 2), ("Tlocrt", 3), ("Presjek", 4), ("3D", 5)):
                self._action(text, lambda value=step: self._set_view_step(value))
            self._activate_complete_tab("model")
        elif key == "analysis":
            self._action("Statika", self._calculate_structure)
            self._action("Engineering Report", self._calculate_building_report)
            self._action("Provjeri model", self.validate_model)
            self._activate_complete_tab("calc")
        elif key == "systems":
            self._action("MEP editor", self._open_mep_editor)
            self._action("Izračunaj MEP", self._calculate_building_report)
            self._action("Osvježi MEP", self._refresh_mep_tab)
            self._activate_complete_tab("mep")
        elif key == "energy":
            self._action("Omotač", lambda: self._activate_complete_tab("envelope"))
            self._action("Krov", lambda: self._activate_complete_tab("model"))
            self._action("Engineering Report", self._calculate_building_report)
            self._activate_complete_tab("envelope")
        elif key == "service":
            self._action("Engineering Report", self._calculate_building_report)
            self._action("Provjeri model", self.validate_model)
            self._action("Sačuvaj projekat", self.save_project)
            self._activate_complete_tab("calc")
        elif key == "ai":
            self._action("Engineering Mentor", self._show_ai_panel)
            self._action("Explainability", self._show_ai_panel)
            self._activate_complete_tab("calc")
            self._show_ai_panel()

    def _show_reference_card(self) -> None:
        target = self.calculation_output
        if target is None:
            return
        house = self.reference_house or ReferenceHouse.default()
        summary = house.summary()
        text = (
            "LAT-CES REFERENTNA KUĆA\n"
            "=======================\n"
            f"Model: {house.data['model_id']}\n"
            f"Naziv: {house.data['name']}\n"
            f"Etaže: {len(house.levels)}\n"
            f"Površina: {summary.floor_area_m2:.1f} m²\n"
            f"Volumen: {summary.volume_m3:.1f} m³\n"
            f"Krov: {house.data['roof']['type']} · {house.data['roof']['slope_deg']:.0f}°\n"
            f"Grijanje: {summary.heating_load_w:.1f} W\n"
            f"Ventilacija: {summary.ventilation_m3_h:.1f} m³/h\n"
            f"Rasvjeta: {summary.lighting_w:.1f} W\n\n"
            "Klikni 'Referentna kuća' da se model učita u BuildingModel."
        )
        self._set_text(target, text)

    def load_reference_house(self) -> None:
        house = ReferenceHouse.default()
        data = house.data
        dimensions = data["dimensions"]
        model = BuildingModel(name=data["name"])
        model.set_orientation(BuildingOrientation(north_azimuth_deg=0.0))
        for level_data in data["levels"]:
            level = Level(
                name=level_data["name"],
                elevation=0.0,
                height=dimensions["level_height_m"],
                length_m=dimensions["length_m"],
                width_m=dimensions["width_m"],
                facade_finish=data["envelope"]["exterior_wall"]["facade_finish"],
                insulation_material=data["envelope"]["exterior_wall"]["insulation"],
                insulation_thickness_m=data["envelope"]["exterior_wall"]["insulation_thickness_m"],
                interior_plaster_material=data["envelope"]["exterior_wall"]["interior_finish"],
                interior_plaster_thickness_m=data["envelope"]["exterior_wall"]["interior_finish_thickness_m"],
                dead_load_kpa=level_data["loads"]["dead_kpa"],
                live_load_kpa=level_data["loads"]["live_kpa"],
                floor_plan=make_envelope_floor_plan(level_data["name"], dimensions["length_m"], dimensions["width_m"], 0.20),
            )
            previous = list(model.levels.values())[-1] if model.levels else None
            level.elevation = previous.top_elevation if previous else 0.0
            model.add_level(level)
        roof = data["roof"]
        model.roof = Roof(
            roof_type=roof["type"],
            covering=roof["covering"],
            length_m=dimensions["length_m"],
            width_m=dimensions["width_m"],
            slope_deg=roof["slope_deg"],
            height_m=(dimensions["width_m"] / 2.0) * math.tan(math.radians(roof["slope_deg"])),
        )
        self.workflow = BuildingWorkflow(model=model)
        self.workflow.active_level_id = next(iter(model.levels))
        self.reference_house = house
        self.model_path.set("LAT-CES-REFERENCE-HOUSE-001")
        self._refresh_complete_tabs()
        self.level_box["values"] = [level.name for level in model.levels.values()]
        self.level_var.set(next(iter(self.level_box["values"])))
        self.refresh_view()
        self._show_reference_card()
        self.status_var.set("Referentna kuća učitana u canonical BuildingModel")

    def _show_ai_panel(self) -> None:
        text = (
            "ENGINEERING MENTOR / EXPLAINABILITY\n"
            "==================================\n"
            "• GUI ne čuva naučnu istinu.\n"
            "• BuildingModel je canonical izvor geometrije i inputa.\n"
            "• Analize čitaju model i vraćaju provjerljive rezultate.\n"
            "• Svaki rezultat treba vezati za model, modul i status validacije."
        )
        self._set_text(self.calculation_output, text)


def _run_gui_identity_smoke() -> None:
    app = FunctionalLATCESApp()
    try:
        app.update_idletasks()
        expected = ("OBJECT", "MODEL", "ANALYSIS", "SYSTEMS", "ENERGY", "SERVICE", "AI")
        actual = tuple(
            widget.cget("text")
            for widget in app._all_widgets(app)
            if isinstance(widget, ttk.Button) and widget.cget("text") in expected
        )
        missing = [item for item in expected if item not in actual]
        if missing:
            raise RuntimeError(f"Missing canonical navigation: {missing}; actual={actual}")
        app.load_reference_house()
        if app.workflow.model.name != ReferenceHouse.default().data["name"]:
            raise RuntimeError("Reference house was not loaded into BuildingModel")
        print(f"GUI functional identity OK: {type(app).__name__}; navigation={actual}")
    finally:
        app.destroy()


def main() -> None:
    if __import__("os").environ.get("LATCES_GUI_SMOKE") == "1":
        _run_gui_identity_smoke()
        __import__("os")._exit(0)
    FunctionalLATCESApp().mainloop()


if __name__ == "__main__":
    main()
