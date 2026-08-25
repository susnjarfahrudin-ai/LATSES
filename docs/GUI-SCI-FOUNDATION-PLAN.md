# LAT-CES GUI + SCI Foundation Plan

## Reference GUI baseline

**GUI reference:** `280832b68eb157d84fb45f294a9c87cc79013ec8`
(PR #144 / merge of the revert of packaged GUI identity smoke)

This baseline is the functional GUI reference, not a whole-repository rollback.

### KEEP — GUI foundation
- `lat_ces/gui_complete.py` → `CompleteBuildingWorkspaceApp`
- `lat_ces/gui.py` → canonical `FloorPlanEditor` / Canvas
- `lat_ces/gui_drafting.py` → canonical drafting workspace
- `lat_ces/gui_mep_engineering.py` → existing MEP engineering editor
- direct `BuildingModel` / `FloorPlan` ownership
- existing `Krov → Sprat → Tlocrt → Presjek → 3D` navigation
- existing engineering tabs: Model / Pogledi, Omotač / Fasada, Konstrukcija / Statika, Proračuni, MEP, Fasade

### RESTORE — release behavior
- direct `gui_complete.py` production entrypoint
- bounded Windows EXE startup smoke
- package the same entrypoint for Installer
- do not introduce a second packaged GUI identity smoke lifecycle

### REJECT — experimental GUI layers
- `lat_ces/gui_functional.py`
- `gui_release.py`
- `gui_master.py`
- duplicated GUI/model construction
- packaged GUI identity experiments that bypass the historical bounded smoke

### KEEP / VALIDATE — later domain and scientific work
The repository work added after the GUI baseline is not discarded:
- SCI 1–145 consolidation and contracts
- Scientific Core governance / ontology / reasoning / synthesis
- `building_adapter.py`
- BuildingModel / MEP / structural developments
- Reference House data and loading logic

These must be integrated into the existing GUI baseline, not used to create a new GUI shell.

## Canonical target path

```text
SCI / domain contracts
        ↓
validated BuildingModel/domain result
        ↓
Reference House canonical loader/factory
        ↓
BuildingModel
        ↓
Level.floor_plan
        ↓
CompleteBuildingWorkspaceApp
        ↓
existing FloorPlanEditor + Canvas
        ↓
gui_complete.py
        ↓
PyInstaller
        ↓
bounded EXE smoke
        ↓
Installer
```

## Required end-to-end acceptance

1. SCI acceptance remains GREEN.
2. Reference House loads into the canonical BuildingModel path.
3. Existing `CompleteBuildingWorkspaceApp` opens without a parallel GUI layer.
4. Existing Canvas renders the canonical FloorPlan.
5. FloorPlanEditor mutates the same canonical FloorPlan.
6. Existing engineering tabs operate on the same BuildingModel.
7. PyInstaller packages `gui_complete.py`.
8. Historical bounded EXE smoke succeeds.
9. Installer builds and installer smoke succeeds.
10. Final manual Windows test confirms the installed GUI matches the reference interface and the requested user workflow.

## SCI rule

SCI 1–145 work is **KEEP / VALIDATE**, not rollback. The GUI is the presentation/editor layer over the canonical domain/scientific contracts; SCI/domain development must not force a replacement GUI entrypoint.

## External historical issue/failure reference

A specific historical `susnjarfahrudin-eng` failure is referenced in project history but was not uniquely locatable from the connected public repository search during this checkpoint. It remains an explicit validation input before the next domain/GUI integration PR.
