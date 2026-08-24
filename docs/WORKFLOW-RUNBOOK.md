# LAT-CES CI / Release Runbook — persistent workflow memory

This document is the persistent operational memory for CI, EXE and Windows Installer repair/release cycles.

## Canonical repository

- Repository: `susnjarfahrudin-ai/LATSES`
- Use this repository for the release workflow.
- Never substitute evidence from another repository, branch or older commit.

## SCI development order

`SCI 1–145 → gap map → canonical scientific contract → consolidate duplicates → Unit/Dimension/Quantity/Measurement/Uncertainty/Provenance → Validation Gate → BuildingModel integration → SCI verification tests → CI Gate → EXE → Installer → GUI final evaluation`

GUI remains downstream of the scientific contract.

## Safe repair loop

1. Identify the exact `main` SHA under test.
2. Run the relevant Verification workflow for that exact SHA.
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

## Current ReferenceHouse / main verification checkpoint

The historical ReferenceHouse repair chain established a case-insensitive bedroom classification fix. The old Verification evidence associated with that chain is not reusable as release evidence for later documentation or packaging commits.

Important rule: record the exact tested SHA together with the workflow run number every time.

## Installer repair cycle — 2026-08-25

### Checkpoint A — documentation commit

Target commit:

`2694a3d876b34f600b9f9b6b030793b6aa9c1635`

Message:

`docs: record ReferenceHouse verification and release evidence chain`

Verification Pipeline #818:

- `verify-core`: SUCCESS
- wheel/package discovery: SUCCESS
- LAT-CES verification tests: SUCCESS

Windows packaging runs for the same SHA:

- Windows Executable #361: SUCCESS
- Windows Installer #658: FAILURE

### Checkpoint B — first real Installer failure at #658

Installer #658 failed in:

`GUI identity smoke test`

What was proven before the failure:

- complete desktop application import: SUCCESS
- pytest: SUCCESS
- PyInstaller GUI executable build: SUCCESS
- packaged EXE smoke test: SUCCESS

What failed:

The workflow attempted to obtain the application's main window through the Windows UI Automation / process window path and timed out. In other words, the packaged EXE was built and remained alive, but the runner-side automation test did not obtain the expected window handle/AutomationElement.

The Inno Setup and artifact stages were skipped because the GUI identity stage failed.

### Repair commit 1

Commit:

`683993ac761ce1c670829f8b271d4dc36fca4238`

Message:

`fix: make packaged GUI identity smoke test robust`

This changed only `.github/workflows/build-installer.yml` and broadened the UIAutomation window lookup from `MainWindowHandle` to a root-window/process-id search.

Verification Pipeline #819 for this repair SHA:

- `verify-core`: SUCCESS / GREEN

Installer #659 for the same repair SHA:

- build-installer: FAILURE

### Checkpoint C — second real Installer failure at #659

Installer #659 again proved:

- package/dependencies: SUCCESS
- complete desktop import: SUCCESS
- pytest: SUCCESS
- GUI EXE build: SUCCESS
- packaged EXE smoke: SUCCESS

The new failure was again the `GUI identity smoke test`.

Exact error:

`GUI identity smoke test timed out waiting for a Window AutomationElement for LATSES.exe (PID 1304)`

Conclusion:

The issue is not PyInstaller, not the GUI application's class construction, and not an application crash. The runner-side UIAutomation requirement is itself unreliable for this packaged Tk application.

### Canonical test already present in the application

`lat_ces/gui_complete.py` already provides the environment-controlled smoke path:

`LATCES_GUI_SMOKE=1`

When enabled, the packaged application's `main()` calls `_run_gui_identity_smoke()`, which:

1. Instantiates the real `CompleteBuildingWorkspaceApp`.
2. Confirms the concrete class identity.
3. Reads the actual Notebook tabs from the live Tk object.
4. Requires the expected surface identities:
   - `Model / Pogledi`
   - `Konstrukcija / Statika`
   - `MEP`
   - `Fasade`
5. Raises a non-zero exit code on mismatch.
6. Destroys the application after the check.

This is the canonical application-level GUI identity check and does not depend on runner desktop/window-handle behavior.

### Repair commit 2 — current

Commit:

`25e6a6ece9895012353b915a6a06cdc6aa246463`

Message:

`fix: use packaged GUI identity smoke hook on Windows runner`

Change:

The Installer workflow `GUI identity smoke test` no longer uses UIAutomation. It now executes the packaged EXE with:

`LATCES_GUI_SMOKE=1`

and waits for the process to exit successfully. A non-zero exit code fails the workflow.

The workflow still separately retains the generic packaged EXE smoke test, so there are two distinct gates:

- EXE runtime/survival smoke
- canonical GUI identity smoke

No application source file was changed by this repair.

## Required sequence from `25e6a6ec…`

The mandatory sequence is now:

1. Verify exact `main` SHA.
2. Verification Pipeline for `25e6a6ece9895012353b915a6a06cdc6aa246463` must be GREEN.
3. Windows Installer for the same SHA.
4. Confirm package/dependency installation.
5. Confirm complete desktop application imports.
6. Confirm full pytest suite.
7. Build `LATSES.exe` with PyInstaller.
8. Confirm packaged EXE creation and size.
9. Run packaged EXE smoke test.
10. Run canonical `LATCES_GUI_SMOKE=1` identity test.
11. Install Inno Setup.
12. Compile `installer/LATSES.iss`.
13. Confirm `installer-output/LAT-CES-Setup.exe` exists and is above the minimum size.
14. Compute SHA-256.
15. Upload `LAT-CES-Windows-Installer`.
16. Accept release evidence only after the upload succeeds.
17. Record final workflow run number, exact source SHA, artifact name, artifact size and SHA-256.

## Current release gate

All of the following must be GREEN for release readiness:

- exact `main` SHA identified
- LAT-CES Verification Pipeline: SUCCESS
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
