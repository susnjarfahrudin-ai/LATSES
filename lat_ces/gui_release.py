"""Release GUI entrypoint with an explicit editable Reference House workflow.

This thin wrapper keeps the existing FunctionalLATCESApp and BuildingModel as
canonical sources while making the first-use path deterministic for packaged
Windows builds: the Reference House is loaded immediately and the user gets a
single visible action to open the editable floor-plan step.
"""
from __future__ import annotations

import os

from lat_ces.gui_functional import FunctionalLATCESApp, _run_gui_identity_smoke


class ReleaseLATCESApp(FunctionalLATCESApp):
    """Packaged GUI with an explicit Reference House -> Tlocrt entry path."""

    def __init__(self) -> None:
        super().__init__()
        self._install_functional_layer()

    def _route_module(self, key: str) -> None:
        super()._route_module(key)
        if key == "object":
            self._action("edit_floor_plan", "Otvori tlocrt", self._open_floor_plan)

    def _open_floor_plan(self) -> None:
        if self.reference_house is None:
            self.load_reference_house()
        self._route_module("model")
        self._set_view_step(3)
        self.status_var.set(
            "Tlocrt spreman za unos · BuildingModel = Referentna kuća"
        )


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
            app.module_action_commands["edit_floor_plan"]()
            if app.current_nav.get().lower() != "model":
                raise RuntimeError("Release GUI did not route to MODEL")
            print("Release GUI first-use path OK: Reference House -> Tlocrt")
        finally:
            app.destroy()
        os._exit(0)
    ReleaseLATCESApp().mainloop()


if __name__ == "__main__":
    main()
