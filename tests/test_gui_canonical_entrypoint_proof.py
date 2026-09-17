from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_canonical_gui_entrypoint_is_self_contained_in_clean_process():
    root = Path(__file__).resolve().parents[1]
    code = """
import importlib
import json
import sys

module = importlib.import_module("lat_ces.gui_complete")
app_class = module.CompleteBuildingWorkspaceApp

print(json.dumps({
    "module": app_class.__module__,
    "init_module": app_class.__init__.__module__,
    "build_model_tab_module": app_class._build_model_tab.__module__,
    "draw_floor_plan_module": app_class.draw_floor_plan.__module__,
    "entry_function": module.main.__module__,
    "launcher_loaded": "lat_ces.gui_launcher" in sys.modules,
}))
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    observed = json.loads(result.stdout)

    assert observed["module"] == "lat_ces.gui_complete"
    assert observed["init_module"] == "lat_ces.gui_complete"
    assert observed["build_model_tab_module"] == "lat_ces.gui_complete"
    assert observed["draw_floor_plan_module"] == "lat_ces.gui_complete"
    assert observed["entry_function"] == "lat_ces.gui_complete"
    assert observed["launcher_loaded"] is False
