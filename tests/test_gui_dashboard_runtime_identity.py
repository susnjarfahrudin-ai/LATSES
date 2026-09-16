from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_clean_probe(code: str) -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_dashboard_import_does_not_mutate_canonical_gui_runtime_identity() -> None:
    code = """
import importlib
import json
import sys

canonical = importlib.import_module("lat_ces.gui_complete")
app_class = canonical.CompleteBuildingWorkspaceApp
before = {
    "draw_floor_plan_module": app_class.draw_floor_plan.__module__,
    "launcher_loaded": "lat_ces.gui_launcher" in sys.modules,
}

importlib.import_module("lat_ces.gui_dashboard")

after = {
    "draw_floor_plan_module": app_class.draw_floor_plan.__module__,
    "launcher_loaded": "lat_ces.gui_launcher" in sys.modules,
    "mro": [f"{cls.__module__}.{cls.__name__}" for cls in app_class.__mro__],
}

print(json.dumps({"before": before, "after": after}))
"""
    observed = _run_clean_probe(code)

    assert observed["before"]["launcher_loaded"] is False
    assert observed["after"]["launcher_loaded"] is False
    assert observed["before"]["draw_floor_plan_module"] == "lat_ces.gui_drafting"
    assert observed["after"]["draw_floor_plan_module"] == "lat_ces.gui_drafting"
    assert observed["after"]["mro"] == [
        "lat_ces.gui_complete.CompleteBuildingWorkspaceApp",
        "lat_ces.gui_drafting.DraftingLATCESApp",
        "lat_ces.gui_enhanced.EnhancedLATCESApp",
        "lat_ces.gui.LATCESApp",
        "tkinter.Tk",
        "tkinter.Misc",
        "tkinter.Wm",
        "builtins.object",
    ]
