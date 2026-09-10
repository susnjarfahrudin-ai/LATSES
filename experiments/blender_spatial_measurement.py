"""Run an actual Blender headless reconstruction measurement from LAT-CES scene data."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lat_ces.adapters import adapt_building
from tests.building_model.test_spatial_reconstruction import minimal_spatial_house


BLENDER_SCRIPT = ROOT / "experiments" / "blender_spatial_renderer.py"


def main() -> int:
    scene = adapt_building(minimal_spatial_house())

    with tempfile.TemporaryDirectory(prefix="latces-blender-") as tmp:
        tmp_path = Path(tmp)
        scene_path = tmp_path / "scene.json"
        blend_path = tmp_path / "scene.blend"
        report_path = tmp_path / "measurement.json"
        scene_path.write_text(json.dumps(scene, sort_keys=True, indent=2), encoding="utf-8")

        command = [
            "blender",
            "--background",
            "--python",
            str(BLENDER_SCRIPT),
            "--",
            str(scene_path),
            str(blend_path),
            str(report_path),
        ]
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode

        report = json.loads(report_path.read_text(encoding="utf-8"))
        print(json.dumps(report, indent=2, sort_keys=True))
        failures = [item for item in report["checks"] if item["status"] != "PASS"]
        if failures:
            print(f"Blender spatial measurement FAILED: {len(failures)} check(s)", file=sys.stderr)
            return 1

        print("Blender spatial measurement PASSED")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
