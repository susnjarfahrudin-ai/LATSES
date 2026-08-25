# LAT-CES Restore Checkpoint — `74f96b6`

## Purpose

This document records the historical release state immediately before PR #143 introduced the new packaged-GUI identity smoke experiment.

**Reference commit:** `74f96b691165ea49baaf19443d897cbcddff6f1f`

**Reference PR lineage:** PR #142 had already documented a validated BuildingModel/Reference House integration state with Verification #762 GREEN and Windows Installer #609 GREEN. PR #143 then introduced the packaged GUI identity smoke experiment.

## 1. Production GUI at the checkpoint

`lat_ces/gui_complete.py` is the desktop entrypoint.

The class is `CompleteBuildingWorkspaceApp`, derived from `DraftingLATCESApp`, and it owns the integrated engineering notebook/tabs while using the existing `FloorPlanEditor` and Canvas underneath.

At this commit, `main()` is deliberately simple:

```python

def main() -> None:
    CompleteBuildingWorkspaceApp().mainloop()
```

There is **no packaged-GUI smoke mode** in `gui_complete.py` at this checkpoint. The later `LATCES_GUI_SMOKE` branch was introduced by PR #143 and is not part of this baseline.

The end-to-end production GUI therefore follows the normal interactive Tk lifecycle:

```text
CompleteBuildingWorkspaceApp
        ↓
DraftingLATCESApp
        ↓
canonical BuildingModel / FloorPlan
        ↓
FloorPlanEditor
        ↓
real Canvas
        ↓
Tk mainloop
```

The existing GUI includes the integrated engineering surfaces: Model / Pogledi, Omotač / Fasada, Konstrukcija / Statika, Proračuni, MEP, and Fasade.

## 2. `gui_functional.py` status at this checkpoint

A repository tree inspection of commit `74f96b6` does **not** contain `lat_ces/gui_functional.py`.

Therefore `gui_functional.py` must **not** be treated as part of the 74f96b6 historical production baseline. It was introduced later in the GUI/release sequence. Any reconstruction that claims `gui_functional.py` was the canonical entrypoint at `74f96b6` is historically incorrect.

This distinction matters because later PRs (#154–#159) made `gui_functional.py` part of the Windows release chain and then introduced `gui_release.py` on top of it.

## 3. Windows Installer workflow at the checkpoint

`.github/workflows/build-installer.yml` at `74f96b6` uses:

```text
Verify CompleteBuildingWorkspaceApp import + pytest
        ↓
PyInstaller lat_ces/gui_complete.py
        ↓
Start dist/LATSES.exe
        ↓
wait 3 seconds
        ↓
if exited with non-zero code → fail
if still running → Stop-Process -Force
        ↓
Inno Setup
        ↓
installer smoke (size + SHA256)
        ↓
artifact upload
```

The packaged smoke at this point proves **startup viability**, not GUI identity. It intentionally does not wait for the GUI to exit itself and does not inject a GUI identity environment variable.

The exact packaging command is:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name LATSES lat_ces/gui_complete.py
```

## 4. Boundary introduced by PR #143

PR #143 changed the release workflow by adding a packaged GUI identity smoke and adding `LATCES_GUI_SMOKE` handling inside `gui_complete.py`.

That experiment changed the process lifecycle from:

```text
launch → observe startup → kill test process
```

to a new model:

```text
launch packaged EXE in smoke mode → wait for application-driven completion
```

Later PRs #145, #155, #157, #159 and #160 progressively changed this again. Those changes must be treated as subsequent experiments, not as evidence that the original packaged-EXE path was wrong.

## 5. Restoration rule

Use `74f96b6` as the historical baseline when evaluating the packaged GUI path.

Do not reintroduce the later packaged identity-smoke mechanism merely to make CI GREEN.

The correct next development sequence is:

```text
74f96b6 historical release state
        ↓
verify exact historical GUI/EXE behavior
        ↓
integrate Reference House / BuildingModel changes minimally
        ↓
verify Python + GUI
        ↓
build EXE from the same canonical entrypoint
        ↓
retain the proven bounded process smoke semantics
        ↓
Installer
```

## 6. Important correction

The historical evidence shows that the last proven release architecture before the packaged-GUI identity experiment used **`gui_complete.py`**, not `gui_functional.py`.

`gui_functional.py` is a later layer and must be reconstructed from the commit/PR where it was introduced rather than projected backwards onto `74f96b6`.
