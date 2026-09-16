"""Clean-process proof for the canonical production GUI runtime identity."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_production_gui_entrypoint_and_runtime_identity_in_clean_process():
    root = Path(__file__).resolve().parents[1]
    code = """
import importlib
import json
import sys
from pathlib import Path

text = Path("pyproject.toml").read_text(encoding="utf-8")
entry = next(
    line.split("=", 1)[1].strip().strip('\\\"')
    for line in text.splitlines()
    if line.strip().startswith("lat-ces-gui =")
)
module_name, function_name = entry.split(":", 1)
module = importlib.import_module(module_name)
app_class = module.CompleteBuildingWorkspaceApp

print(json.dumps({
    "entry": entry,
    "module": app_class.__module__,
    "init_module": app_class.__init__.__module__,
    "build_model_tab_module": app_class._build_model_tab.__module__,
    "draw_floor_plan_module": app_class.draw_floor_plan.__module__,
    "launcher_loaded": "lat_ces.gui_launcher" in sys.modules,
    "entry_function": getattr(module, function_name).__module__,
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

    assert observed["entry"] == "lat_ces.gui_complete:main"
    assert observed["module"] == "lat_ces.gui_complete"
    assert observed["init_module"] == "lat_ces.gui_complete"
    assert observed["build_model_tab_module"] == "lat_ces.gui_complete"
    assert observed["draw_floor_plan_module"] == "lat_ces.gui_complete"
    assert observed["entry_function"] == "lat_ces.gui_complete"
    assert observed["launcher_loaded"] is False
