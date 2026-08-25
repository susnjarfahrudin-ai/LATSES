"""Functional packaged LAT-CES desktop entrypoint.

The canonical CompleteBuildingWorkspaceApp remains the GUI owner. This layer
adds real module routing, the canonical ReferenceHouse showcase, and a smoke
test that exercises navigation/action wiring without invoking potentially
blocking interactive or long-running engineering commands.
"""
from __future__ import annotations

import math
import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Room, Roof
from lat_ces.building.orientation import BuildingOrientation
from lat_ces.building.workflow import BuildingWorkflow, make_envelope_floor_plan
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.reference_house import ReferenceHouse


class FunctionalLATCESApp(CompleteBuildingWorkspaceApp):
    """Packaged LAT-CES GUI with functional module navigation and reference house."""

    MODULES = {
        "OBJECT": "object",
        "MODEL": "model",
        "ANALYSIS": "analysis",
        "SYSTEMS": "systems",
        "ENERGY": "energy",
        "SERVICE": "service",
        "AI": "ai",
    }

    def __init__(self) -> None:
        self.reference_house: ReferenceHouse | None = None
        self.module_actions: ttk.Frame | None = None
        self.module_action_commands: dict[str, object] = {}
        super().__init__()
        self.after_idle(self._install_functional_layer)

    def _install_functional_layer(self) -> None:
        if self.module_actions is not None:
            return
        shell = getattr(self, "shell_body", None)
        if shell is None:
            raise RuntimeError("Canonical LAT-CES shell body is missing")
        action_bar = ttk.Frame(shell.master, padding=(14, 4))
        action_bar.pack(fill="x", before=shell, padx=0, pady=(2, 0))
        self.module_actions = action_bar
        self._wire_top_navigation()
        self.load_reference_house()
        self._route_module("object")

    def _all_widgets(self, parent):
        for child in parent.winfo_children():
            yield child
            yield from self._all_widgets(child)

    def _wire_top_navigation(self) -> None:
        for widget in self._all_widgets(self):
            if not isinstance(widget, ttk.Button):
                continue
            label = str(widget.cget("text"))
            key = self.MODULES.get(label)
            if key:
                widget.configure(command=lambda selected=key: self._route_module(selected))

    def _clear_actions(self) -> None:
        if self.module_actions is None:
            return
        for child in self.module_actions.winfo_children():
            child.destroy()
        self.module_action_commands.clear()

    def _action(self, key: str, text: str, command) -> None:
        if self.module_actions is None:
            raise RuntimeError("Functional action bar is not installed")
        self.module_action_commands[key] = command
        ttk.Button(self.module_actions, text=text, command=command).pack(side="left", padx=3)

    def _route_module(self, key: str) -> None:
        super()._select_nav(key)
        self._clear_actions()
        if key == "object":
            self._action("reference_house", "Referentna kuća", self.load_reference_house)
            self._action("new", "Novi objekat", self.new_project)
            self._action("load", "Učitaj projekat", self.load_project)
            self._action("save", "Sačuvaj projekat", self.save_project)
            self._show_reference_card()
        elif key == "model":
            for action_key, text, step in (("roof", "Krov", 1), ("level", "Sprat", 2), ("plan", "Tlocrt", 3), ("section", "Presjek", 4), ("3d", "3D", 5)):
                self._action(action_key, text, lambda value=step: self._set_view_step(value))
            self._activate_complete_tab("model")
        elif key == "analysis":
            self._action("structural", "Statika", self._calculate_structure)
            self._action("report", "Engineering Report", self._calculate_building_report)
            self._action("validate", "Provjeri model", self.validate_model)
            self._activate_complete_tab("calc")
        elif key == "systems":
            self._action("mep_editor", "MEP editor", self._open_mep_editor)
            self._action("mep_calc", "Izračunaj MEP", self._calculate_building_report)
            self._action("mep_refresh", "Osvježi MEP", self._refresh_mep_tab)
            self._activate_complete_tab("mep")
        elif key == "energy":
            self._action("envelope", "Omotač", lambda: self._activate_complete_tab("envelope"))
            self._action("energy_report", "Engineering Report", self._calculate_building_report)
            self._activate_complete_tab("envelope")
        elif key == "service":
            self._action("service_report", "Engineering Report", self._calculate_building_report)
            self._action("service_validate", "Provjeri model", self.validate_model)
            self._action("service_save", "Sačuvaj projekat", self.save_project)
            self._activate_complete_tab("calc")
        elif key == "ai":
            self._action("mentor", "Engineering Mentor", self._show_ai_panel)
            self._action("explainability", "Explainability", self._show_ai_panel)
            self._activate_complete_tab("calc")
            self._show_ai_panel()

    def _show_reference_card(self) -> None:
        if self.calculation_output is None:
            return
        house = self.reference_house or ReferenceHouse.default()
        summary = house.summary()
        active_name = self.level_var.get() if hasattr(self, "level_var") else ""
        text = (
            "LAT-CES REFERENTNA KUĆA\n"
            "=======================\n"
            f"Model: {house.data['model_id']}\n"
            f"Naziv: {house.data['name']}\n"
            f"Etaže: {len(house.levels)}\n"
            f"Aktivna etaža: {active_name}\n"
            f"Prostorije: {sum(len(level.rooms) for level in self.workflow.model.levels.values())}\n"
            f"Površina: {summary.floor_area_m2:.1f} m²\n"
            f"Volumen: {summary.volume_m3:.1f} m³\n"
            f"Krov: {house.data['roof']['type']} · {house.data['roof']['slope_deg']:.0f}°\n"
            f"Grijanje: {summary.heating_load_w:.1f} W\n"
            f"Ventilacija: {summary.ventilation_m3_h:.1f} m³/h\n"
            f"Rasvjeta: {summary.lighting_w:.1f} W\n"
        )
        self._set_text(self.calculation_output, text)

    def load_reference_house(self) -> None:
        house = ReferenceHouse.default()
        data = house.data
        dimensions = data["dimensions"]
        model = BuildingModel(name=data["name"])
        model.set_orientation(BuildingOrientation(north_azimuth_deg=0.0))

        for level_data in data["levels"]:
            level = Level(
                name=level_data["name"], elevation=0.0, height=dimensions["level_height_m"],
                length_m=dimensions["length_m"], width_m=dimensions["width_m"],
                facade_finish=data["envelope"]["exterior_wall"]["facade_finish"],
                insulation_material=data["envelope"]["exterior_wall"]["insulation"],
                insulation_thickness_m=data["envelope"]["exterior_wall"]["insulation_thickness_m"],
                interior_plaster_material=data["envelope"]["exterior_wall"]["interior_finish"],
                interior_plaster_thickness_m=data["envelope"]["exterior_wall"]["interior_finish_thickness_m"],
                dead_load_kpa=level_data["loads"]["dead_kpa"], live_load_kpa=level_data["loads"]["live_kpa"],
                floor_plan=make_envelope_floor_plan(level_data["name"], dimensions["length_m"], dimensions["width_m"], 0.20),
            )
            previous = list(model.levels.values())[-1] if model.levels else None
            level.elevation = previous.top_elevation if previous else 0.0

            for room_index, room_data in enumerate(level_data["rooms"]):
                if room_data["height_m"] <= 0:
                    continue
                room_area = float(room_data["area_m2"])
                room_length = math.sqrt(room_area * 1.25)
                room_width = room_area / room_length
                room_x = 0.5 + (room_index % 3) * 3.8
                room_y = 0.5 + (room_index // 3) * 3.1
                level.add_room(Room(name=room_data["name"], footprint=Box3D(Point3D(room_x, room_y, 0.0), room_length, room_width, room_data["height_m"])))
            model.add_level(level)

        roof = data["roof"]
        model.roof = Roof(
            roof_type=roof["type"], construction="drvena konstrukcija", covering=roof["covering"],
            substructure="letve + kontra-letve", support="krovna ploča / vijenci",
            length_m=dimensions["length_m"], width_m=dimensions["width_m"], slope_deg=roof["slope_deg"],
            height_m=(dimensions["width_m"] / 2.0) * math.tan(math.radians(roof["slope_deg"])),
        )

        self.workflow = BuildingWorkflow(model=model)
        self.workflow.active_level_id = next(iter(model.levels))
        self.reference_house = house
        self.model_path.set("LAT-CES-REFERENCE-HOUSE-001")
        self.level_box["values"] = [level.name for level in model.levels.values()]
        self.level_var.set(next(iter(self.level_box["values"])))
        self._refresh_complete_tabs()
        self.refresh_view()
        self._show_reference_card()
        self.status_var.set(f"Referentna kuća učitana · {len(model.levels)} etaže · {sum(len(level.rooms) for level in model.levels.values())} prostorija")

    def _show_ai_panel(self) -> None:
        self._set_text(
            self.calculation_output,
            "ENGINEERING MENTOR / EXPLAINABILITY\n==================================\n"
            "• BuildingModel je canonical izvor geometrije i inputa.\n"
            "• Analize čitaju model i vraćaju provjerljive rezultate.\n"
            "• GUI ne duplicira naučnu istinu.\n"
            "• Svaki rezultat mora biti vezan za model, modul i status validacije.\n",
        )


def _run_gui_identity_smoke() -> None:
    app = FunctionalLATCESApp()
    try:
        app._install_functional_layer()
        app.update_idletasks()
        expected = tuple(FunctionalLATCESApp.MODULES.keys())
        actual = tuple(widget.cget("text") for widget in app._all_widgets(app) if isinstance(widget, ttk.Button) and widget.cget("text") in expected)
        missing = [item for item in expected if item not in actual]
        if missing:
            raise RuntimeError(f"Missing canonical navigation: {missing}; actual={actual}")

        model = app.workflow.model
        room_count = sum(len(level.rooms) for level in model.levels.values())
        reference = ReferenceHouse.default()
        if model.name != reference.data["name"]:
            raise RuntimeError("Reference house model identity mismatch")
        if len(model.levels) != len(reference.levels):
            raise RuntimeError("Reference house level count mismatch")
        if room_count < 10:
            raise RuntimeError(f"Reference house room mapping incomplete: {room_count}")
        if model.roof is None or model.roof.slope_deg <= 0:
            raise RuntimeError("Reference house roof was not loaded into BuildingModel")

        # Route every module and verify that its functional actions are wired.
        # Do not execute calculation/report actions here: those are validated by
        # pytest/Verification and may be interactive or long-running on Windows.
        for key in FunctionalLATCESApp.MODULES.values():
            app._route_module(key)
            if not app.module_action_commands:
                raise RuntimeError(f"No functional actions registered for module: {key}")
        app.update_idletasks()

        print(
            "GUI functional identity OK: "
            f"navigation={actual}; levels={len(model.levels)}; rooms={room_count}; "
            f"roof={model.roof.roof_type}/{model.roof.slope_deg:g}deg"
        )
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_SMOKE") == "1":
        _run_gui_identity_smoke()
        os._exit(0)
    FunctionalLATCESApp().mainloop()


if __name__ == "__main__":
    main()
