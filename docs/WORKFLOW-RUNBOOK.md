# LAT-CES CI / Release Runbook — persistent workflow memory

This document is the persistent operational memory for CI, EXE and Windows Installer repair/release cycles.

## Canonical repository

- Repository: `susnjarfahrudin-ai/LATSES`
- Use this repository for the release workflow.
- Never substitute evidence from another repository, branch or older commit.

## Canonical Verification workflow

- **Verification:** `.github/workflows/ci.yml`
- **Core job:** `verify-core`
- An empty/non-functional workflow file must not be treated as Verification evidence.
- A workflow run with zero executable jobs is infrastructure/configuration noise, not an application test result.

## SCI development order

`SCI 1–145 → gap map → canonical scientific contract → consolidate duplicates → Unit/Dimension/Quantity/Measurement/Uncertainty/Provenance → Validation Gate → BuildingModel integration → SCI verification tests → CI Gate → EXE → Installer → GUI final evaluation`

GUI remains downstream of the scientific contract.

## Safe repair loop

1. Identify the exact `main` SHA under test.
2. Run the canonical Verification workflow for that exact SHA.
3. Require Verification to be GREEN before packaging evidence is accepted.
4. If a downstream EXE/Installer workflow fails, inspect the first real failing step.
5. Fix only the demonstrated root cause and keep the change minimal.
6. Commit the fix.
7. Re-run Verification for the new exact SHA.
8. Require Verification GREEN again.
9. Run EXE/Installer for that same SHA.
10. Repeat until the complete release chain is GREEN.
11. Do not report an artifact as release-ready until its exact source SHA, artifact name, size and SHA-256 are known.

## Evidence-first release sequence

`exact main SHA → Verification GREEN → EXE build → packaged EXE smoke → GUI identity smoke → Inno Setup → installer build → installer smoke → artifact upload → artifact evidence`

Evidence rules:

1. A green workflow from another SHA does not transfer to the current release SHA.
2. A historical Installer or EXE success is not evidence for the current release SHA.
3. An Installer failure after Verification GREEN is a packaging/release failure unless logs prove otherwise.
4. Use the first real failing step, not secondary skipped steps or warnings.
5. Node.js deprecation warnings are warnings, not the root cause of a failing build unless the workflow proves they caused the failure.
6. No artifact means no release evidence.
7. A `total_count: 0` workflow failure is not application verification evidence.

## ReferenceHouse historical checkpoint

The ReferenceHouse repair established a case-insensitive bedroom classification fix. Historical Verification evidence is not reusable for later commits.

Original repair commit:

`f03cf71df148261da159e0635d683635aa920530`

Observed original failure:

- Obtained lighting: `801.6 W`
- Expected lighting: `792.0 W`
- Difference: `9.6 W`

The fix used `casefold()` in `ReferenceHouse.lighting_w()` and was limited to `lat_ces/reference_house.py`.

## Installer repair cycle — 2026-08-25

### First real Installer failure — #658

The first downstream Installer failure occurred in `GUI identity smoke test` after these stages succeeded:

- desktop import
- pytest
- PyInstaller GUI build
- packaged EXE smoke

Root cause: runner-side Windows UI Automation could not reliably obtain the packaged Tk window.

### Repair — #683993ac

`683993ac761ce1c670829f8b271d4dc36fca4238`

`fix: make packaged GUI identity smoke test robust`

This changed only `.github/workflows/build-installer.yml` and replaced the `MainWindowHandle` lookup with a process/window AutomationElement search.

Verification #819 for this SHA: `SUCCESS`.

Installer #659 for this SHA: `FAILURE`, again at GUI identity smoke.

### Second downstream failure — #659

Exact reported failure:

`GUI identity smoke test timed out waiting for a Window AutomationElement for LATSES.exe (PID 1304)`

Conclusion: UIAutomation was unreliable for this packaged Tk application on the runner.

### Canonical application-level GUI identity hook

`lat_ces/gui_complete.py` already exposes `LATCES_GUI_SMOKE=1`. The hook instantiates the real `CompleteBuildingWorkspaceApp`, checks the concrete class and required notebook tabs, then destroys the app and exits non-zero on mismatch.

Expected GUI surface:

- `Model / Pogledi`
- `Konstrukcija / Statika`
- `MEP`
- `Fasade`

### Repair — #25e6a6ec

`25e6a6ece9895012353b915a6a06cdc6aa246463`

`fix: use packaged GUI identity smoke hook on Windows runner`

The Installer workflow switched to `LATCES_GUI_SMOKE=1` and `Start-Process -Wait`.

Problem discovered later: `Start-Process -Wait` had no explicit timeout, so a non-exiting packaged Tk process could leave the GitHub job stuck indefinitely.

### Repair — #126e8266

`126e82660517f970d957cac8ff5e0abc6d95fe12`

`fix: bound packaged GUI identity smoke test`

The Installer GUI identity step now:

- starts the packaged EXE without `-Wait`
- polls for process exit
- allows a maximum of 45 seconds
- fails with an explicit timeout message if the EXE does not exit
- forcibly terminates the process in timeout/finalization cleanup

This prevents an indefinitely hung Installer run.

### Verification/configuration incident on #126e8266

After `126e8266`, `.github/workflows/main.yml` produced run **#272** with `failure` and **zero jobs**. Investigation showed `.github/workflows/main.yml` was an empty file. It was not the real Verification workflow.

The actual Verification workflow is `.github/workflows/ci.yml`, whose `verify-core` job is valid.

### Cleanup — #702d0996

`702d09964a47bb49fc6fbf73c3a14e3215822ef6`

`chore: remove empty non-functional main workflow`

The empty `.github/workflows/main.yml` was deleted so that the invalid 0-job workflow cannot be mistaken for release evidence.

A fresh Windows Installer run **#663** was automatically queued for this exact SHA.

## Final verified release checkpoint — 2026-08-25

The validated release checkpoint is:

`36ede3d8fcfa3e7d15ac10d338e592ea289f432d`

Commit message:

`fix: run GUI identity smoke in UTF-8 mode`

### Canonical Verification

- Workflow: `LAT-CES Verification Pipeline`
- Job: `verify-core`
- Run: **#829**
- Exact SHA: `36ede3d8fcfa3e7d15ac10d338e592ea289f432d`
- Result: **SUCCESS**
- Wheel/package discovery: **SUCCESS**
- Full verification test suite: **SUCCESS**

### Windows Installer

- Workflow: `LAT-CES Windows Installer`
- Run: **#673**
- Exact SHA: `36ede3d8fcfa3e7d15ac10d338e592ea289f432d`
- Result: **SUCCESS**
- Desktop import + pytest: **SUCCESS**
- PyInstaller GUI executable build: **SUCCESS**
- Packaged EXE smoke: **SUCCESS**
- Canonical GUI identity smoke: **SUCCESS**
- Inno Setup installation: **SUCCESS**
- Inno Setup compile: **SUCCESS**
- Installer artifact smoke: **SUCCESS**
- Artifact upload: **SUCCESS**

The successful GUI identity log explicitly confirmed:

`GUI identity OK: CompleteBuildingWorkspaceApp; tabs=('Model / Pogledi', 'Omotač / Fasada', 'Konstrukcija / Statika', 'Proračuni', 'MEP', 'Fasade')`

The Installer artifact was produced as:

- Artifact name: `LAT-CES-Windows-Installer`
- Artifact ID: `9542719493`
- Artifact size: `10,997,835 bytes`
- Artifact ZIP SHA-256: `cc52ebe857c19fda2b98061f17dfe1778133c67a0148205fa90d824e766c59b6`
- Retention: until `2026-09-23T23:32:39Z`

The installer executable itself was verified during the smoke step:

- File: `LAT-CES-Setup.exe`
- SHA-256: `4C901777909F5F1D26D90C31125E0E9DEA6F4539220FA1CA115ED37AF320E3F2`

This is the first complete evidence chain in this repair cycle where Verification, EXE build/smoke, GUI identity, Inno Setup, installer smoke and artifact upload are all successful for the same exact `main` SHA.

### Evidence links

- Verification #829: `https://github.com/susnjarfahrudin-ai/LATSES/actions/runs/32789740054`
- Installer #673: `https://github.com/susnjarfahrudin-ai/LATSES/actions/runs/32789740148`
- Artifact: `https://github.com/susnjarfahrudin-ai/LATSES/actions/runs/32789740148/artifacts/9542719493`
- Source commit: `https://github.com/susnjarfahrudin-ai/LATSES/commit/36ede3d8fcfa3e7d15ac10d338e592ea289f432d`

## Release gate

All of the following must be GREEN for release readiness:

- exact `main` SHA identified
- canonical LAT-CES Verification Pipeline / `verify-core`: SUCCESS
- CodeQL: SUCCESS
- wheel/package discovery: SUCCESS
- full pytest suite: SUCCESS
- complete desktop application import: SUCCESS
- PyInstaller GUI EXE build: SUCCESS
- packaged EXE smoke test: SUCCESS
- canonical GUI identity smoke test: SUCCESS
- Inno Setup compilation: SUCCESS
- installer artifact smoke test: SUCCESS
- artifact upload: SUCCESS

## Artifact reporting rule

Never report “release-ready” from a workflow that has no artifact. Never reuse an artifact from a different SHA. The final evidence record must include:

`SHA → Verification run → Installer run → artifact name → artifact size → SHA-256`

## Architectural rules

- One canonical scientific implementation per concept.
- Compatibility facades may re-export but must not create competing semantics.
- BuildingModel is the source of truth for the GUI.
- GUI does not become the source of scientific truth.
- EXE/Installer packaging is a release verification stage, not a substitute for scientific verification.
