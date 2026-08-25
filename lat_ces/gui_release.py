"""Release GUI entrypoint with an explicit editable Reference House workflow."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.gui_functional import FunctionalLATCESApp, _run_gui_identity_smoke


class ReleaseLATCESApp(FunctionalLATCESApp):
    """Packaged GUI with a visible Reference House and editing entry path."""

    def __init__(self) -> None:
        super().__init__()
        self._install_functional_layer()
        self._install_release_entry_panel()
        self.load_reference_house()
        self._open_floor_plan()

    def _install_release_entry_panel(self) -> None:
        panel = getattr(self, "module_actions", None)
        if panel is None:
            raise RuntimeError("Release action bar is missing")
        self.release_entry = ttk.LabelFrame(panel, text="LAT-CES — Referentna kuća / uređivanje objekta", padding=(8, 6))
        self.release_entry.pack(fill="x", pady=(4, 0))
        ttk.Label(
            self.release_entry,
            text="Početni model je Referentna kuća. Otvori tlocrt i unesi/uredi geometriju direktno u BuildingModel.",
        ).pack(anchor="w", pady=(0, 5))
        buttons = ttk.Frame(self.release_entry)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Referentna kuća", command=self.load_reference_house).pack(side="left", padx=2)
        ttk.Button(buttons, text="Otvori tlocrt", command=self._open_floor_plan).pack(side="left", padx=2)
        ttk.Button(buttons, text="＋ Prostorija", command=lambda: self._activate_editor("room")).pack(side="left", padx=2)
        ttk.Button(buttons, text="＋ Pregradni zid", command=lambda: self._activate_editor("partition")).pack(side="left", padx=2)
        ttk.Button(buttons, text="Vrata", command=lambda: self._activate_editor("door")).pack(side="left", padx=2)
        ttk.Button(buttons, text="Prozor", command=lambda: self._activate_editor("window")).pack(side="left", padx=2)
        self.reference_house_status = ttk.Label(self.release_entry, anchor="w")
        self.reference_house_status.pack(fill="x", pady=(5, 0))
        self._update_reference_house_status()

    def _update_reference_house_status(self) -> None:
        status = getattr(self, "reference_house_status", None)
        if status is None:
            return
        house = self.reference_house
        model = getattr(getattr(self, "workflow", None), "model", None)
        if house is None or model is None:
            status.configure(text="Referentna kuća nije učitana.")
            return
        levels = len(model.levels)
        rooms = sum(len(level.rooms) for level in model.levels.values())
        status.configure(
            text=f"Referentna kuća: {house.data['name']}  |  etaže: {levels}  |  prostorije: {rooms}  |  BuildingModel: AKTIVAN"
        )

    def load_reference_house(self) -> None:
        super().load_reference_house()
        self._update_reference_house_status()

    def _route_module(self, key: str) -> None:
        super()._route_module(key)
        if key == "object":
            self._action("edit_floor_plan", "Otvori tlocrt", self._open_floor_plan)

    def _open_floor_plan(self) -> None:
        if self.reference_house is None:
            self.load_reference_house()
        self._route_module("model")
        self._set_view_step(3)
        self.status_var.set("Tlocrt spreman za unos · BuildingModel = Referentna kuća")
        self._update_reference_house_status()

    def _activate_editor(self, tool: str) -> None:
        self._open_floor_plan()
        if tool in {"room", "partition", "door", "window"} and hasattr(self, "drag_payload"):
            self.drag_payload = tool
            self.status_var.set(
                {
                    "room": "Povuci ili klikni na tlocrt za novu prostoriju.",
                    "partition": "Povuci ili klikni na tlocrt za novi pregradni zid.",
                    "door": "Povuci vrata na postojeći zid.",
                    "window": "Povuci prozor na postojeći zid.",
                }[tool]
            )
            self.redraw_active_view()


def main() -> None:
    if os.environ.get("LATCES_GUI_SMOKE") == "1":
        _run_gui_identity_smoke()
        app = ReleaseLATCESApp()
        try:
            app.withdraw()
            app._route_module("object")
            required = {"reference_house", "new", "load", "save", "edit_floor_plan"}
            missing = required.difference(app.module_action_commands)
            if missing:
                raise RuntimeError(f"Release object actions missing: {sorted(missing)}")
            if app.reference_house is None:
                raise RuntimeError("Release GUI did not load Reference House")
            if app.workflow.model.name != app.reference_house.data["name"]:
                raise RuntimeError("Release GUI BuildingModel is not the Reference House")
            if not app.workflow.model.levels:
                raise RuntimeError("Release GUI Reference House has no levels")
            app.module_action_commands["edit_floor_plan"]()
            if app.current_nav.get().lower() != "model":
                raise RuntimeError("Release GUI did not route to MODEL")
            if app.view_step.get() != 3:
                raise RuntimeError("Release GUI did not open Tlocrt")
            print("Release GUI first-use path OK: Reference House -> Tlocrt")
        finally:
            app.destroy()
        os._exit(0)
    ReleaseLATCESApp().mainloop()


if __name__ == "__main__":
    main()
