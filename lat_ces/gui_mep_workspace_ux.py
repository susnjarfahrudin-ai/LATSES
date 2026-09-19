"""Compatibility facade for the canonical MEP workspace.

The actual workspace implementation remains in gui_mep_system_workspace.py;
UX behavior is installed by gui_mep_workspace_ux_runtime.py at the entrypoint.
"""
from __future__ import annotations

from lat_ces.gui_mep_system_workspace import EngineeringMEPWorkspaceApp

# Preserve the historical/public class identity expected by LAT-CES tests and callers.
EngineeringMEPWorkspaceApp.__name__ = "EngineeringMEPWorkspaceApp"
EngineeringMEPWorkspaceApp.__qualname__ = "EngineeringMEPWorkspaceApp"

__all__ = ["EngineeringMEPWorkspaceApp"]
