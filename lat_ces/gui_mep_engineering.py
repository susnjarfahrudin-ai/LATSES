"""LAT-CES MEP Engineering entrypoint.

The MEP environment is intentionally separate from the building drafting UI.
It consumes the canonical BuildingModel and writes only to the canonical MEP
registry owned by that model.
"""
from __future__ import annotations

from lat_ces.gui_mep_system_workspace import EngineeringMEPWorkspaceApp


__all__ = ["EngineeringMEPWorkspaceApp"]


def main() -> None:
    EngineeringMEPWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
