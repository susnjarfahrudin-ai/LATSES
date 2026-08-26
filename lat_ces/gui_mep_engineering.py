"""LAT-CES MEP Engineering entrypoint."""
from __future__ import annotations

from lat_ces.gui_mep_workspace_ux import EngineeringMEPWorkspaceApp
from lat_ces.gui_mep_room_zone_runtime import install as install_room_zone_runtime

install_room_zone_runtime(EngineeringMEPWorkspaceApp)

__all__ = ["EngineeringMEPWorkspaceApp"]


def main() -> None:
    EngineeringMEPWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
