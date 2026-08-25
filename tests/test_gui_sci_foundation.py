from __future__ import annotations

import pathlib
import subprocess


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def test_gui_complete_matches_known_good_reference() -> None:
    root = _repo_root()
    actual = (root / "lat_ces" / "gui_complete.py").read_text(encoding="utf-8")
    expected = subprocess.run(
        ["git", "show", "280832b68eb157d84fb45f294a9c87cc79013ec8:lat_ces/gui_complete.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert actual == expected, "Production GUI drifted from the known-good 280832b6 interface baseline"


def test_production_entrypoint_is_canonical_gui_complete() -> None:
    root = _repo_root()
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    installer = (root / ".github" / "workflows" / "build-installer.yml").read_text(encoding="utf-8")

    assert 'lat-ces-gui = "lat_ces.gui_complete:main"' in pyproject
    assert "lat_ces/gui_complete.py" in installer
    assert "gui_functional.py" not in installer
    assert "gui_release.py" not in installer
    assert "gui_master.py" not in installer


def test_reference_house_enters_canonical_building_model_path() -> None:
    from lat_ces.building.reference_house_factory import load_reference_house_model

    model, data = load_reference_house_model()

    assert model.name == data["name"]
    assert model.levels
    assert any(level.floor_plan is not None for level in model.levels.values())
    assert any(level.floor_plan.walls for level in model.levels.values() if level.floor_plan is not None)
