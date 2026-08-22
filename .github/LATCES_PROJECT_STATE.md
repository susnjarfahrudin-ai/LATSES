# LAT-CES Project State / Working Checkpoint

**Purpose:** Persistent hand-off point for LAT-CES engineering work. Do not restart analysis from zero.

## Current working line

- **Repository:** `susnjarfahrudin-ai/LATSES`
- **Default integration branch:** `main`
- **Active engineering branch:** `agent/building-engineering-completion`
- **Active PR:** `#125 — feat: complete Building Engineering integration over canonical BuildingModel`
- **Latest source SHA:** `72f0d58ca2fce87135b72409ef8ab77bb4ca9d9d`

## Architectural rule

`BuildingModel` remains the single source of truth. GUI code must not become the owner of engineering formulas. Missing engineering inputs remain explicit `INPUT_REQUIRED` / `CHECK` states.

## Current release gate

For source SHA `72f0d58ca2fce87135b72409ef8ab77bb4ca9d9d`:

`source SHA → Verification GREEN → master GUI EXE → EXE smoke GREEN → Windows Installer GREEN → installer smoke GREEN → artifact`

All steps above are now **GREEN** in the fresh release cycle:

- Verification Pipeline **#722 — SUCCESS**
- Windows Executable **#329 — SUCCESS**
- Windows Installer **#575 — SUCCESS**
- Windows executable was built from `lat_ces/gui_master.py`, smoke-tested, packaged and uploaded.
- Windows installer was compiled, smoke-tested for artifact integrity and uploaded.

The software release is **not yet accepted as a user release** until the downloaded installer is actually installed on Windows and the packaged GUI commands are exercised end-to-end.

## Failure-workflow — mandatory from this point forward

When any Verification, EXE, smoke test, Installer, or artifact step fails:

1. **Freeze the failing source SHA.** Do not jump to another branch or restart the architecture.
2. **Identify the exact failing workflow, job, step and log/traceback.** No guessing from duration or symptoms.
3. **Classify the failure:** source/application logic, GUI/runtime, packaging/PyInstaller, installer/Inno Setup, environment/dependency, or CI workflow.
4. **Trace the failure to the owning source file/function and dependency path.**
5. **Make the smallest targeted repair on `agent/building-engineering-completion`.** Do not modify unrelated engineering domains.
6. **Add or strengthen a regression test for the exact failure when feasible.**
7. **Run the narrowest relevant verification first.** Only after it passes, run the full release chain again.
8. **Compare the new result against the frozen failing SHA** so the repair is attributable.
9. **Do not declare success until the same source SHA passes the entire required proof chain and the packaged GUI is exercised.**
10. **Record the failure, root cause, repair commit, verification result and next action in this checkpoint.**

### Latest resolved release-gate failure

- **Failing ref:** PR #125 merge ref tested by the failed Windows release run.
- **Failure:** Windows EXE / Installer verification failed in `tests/gui_fullscreen_viewport_smoke_test.py` because the smoke test asserted obsolete `workflow.model.envelope`.
- **Root cause:** stale test contract; the canonical `BuildingModel` no longer exposes `envelope` as a public attribute.
- **Repair commit:** `72f0d58ca2fce87135b72409ef8ab77bb4ca9d9d`
- **Repair:** smoke test now checks the actual canonical reference-house model surface instead of the retired `model.envelope` attribute.
- **Verification after repair:** Verification #722 GREEN; Windows EXE #329 GREEN; Windows Installer #575 GREEN.

### What we must not do on failure

- Do not invent a failing test when logs are unavailable.
- Do not change `BuildingModel` because a packaging step failed unless the traceback proves a model defect.
- Do not reopen resolved 338 m² / 360 m² semantics.
- Do not create parallel `reference-house` hotfix branches for an already solved problem without a new reproducible failure.
- Do not let a long-running workflow become the diagnosis; timeout is a protection, not a root-cause conclusion.

## Already completed Building Engineering work

PR #125 contains the current integration layer for:

- geometry-driven QTO including openings, envelope areas, roof surface/perimeter, gutters, railings and roof/timber counts;
- canonical envelope thermal take-off;
- canonical electrical design-intent registry/reporting;
- unified Building Engineering Report aggregating MEP, QTO, structural, thermal and electrical domains;
- reference-house workflow materialized into canonical BuildingModel;
- master GUI with Tlocrt / Presjek / 3D / Provjera / Izvještaj / Reference House / Materijali paths;
- master GUI callback and catalog-tab regression repairs;
- Windows EXE and Windows Installer release workflow proven GREEN on the current source SHA.

## Remaining implementation after release proof

Once the downloaded installer is exercised successfully, continue with:

1. fuller structural engineering: load path, structural model, RC design and detailing;
2. layered envelope/thermal assemblies;
3. windows/glazing model: wood/PVC/aluminium, 1–4 panes, gas fill, Low-E and spacer;
4. roof timber, coverings, sheet metal, gutters/downpipes and railings as integrated engineering objects;
5. electrical and plumbing objects under BuildingModel ownership;
6. manufacturer-material catalog adapter/migration between manufacturer schema and parameterized Building Material catalog;
7. complete `SCI 1–145` traceability matrix: SCI requirement → implementation → test → status (`KEEP/ADAPT/MERGE/NEW`);
8. remaining scientific-layer implementation identified by that SCI matrix.

## Historical decisions — do not reopen without a new reproducible contradiction

- Gross floor area: `360 m²` (`12 × 10 × 3`).
- Conditioned floor area: `338 m²`.
- `floor_area_m2` remains the backward-compatible alias for conditioned floor area.
- Reference-house JSON loads adjacent to `reference_house.py` using the accepted path-based implementation.
- Earlier GUI regressions: missing master callbacks and wrong catalog notebook parent were repaired and regression-tested.

## Session rule

After every meaningful change, update this checkpoint with: active branch/PR, latest source SHA, CI run status, completed work, current blocker, exact next action, and any failure/root-cause evidence. Future sessions must start from this checkpoint and the active PR instead of reconstructing history from conversation.
