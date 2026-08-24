# LAT-CES CI / Release Runbook — persistent workflow memory

This file is the persistent operational memory for future maintenance of LATSES. Read it before continuing a CI/EXE/installer repair cycle.

## Canonical repository

- Working repository: `susnjarfahrudin-ai/LATSES`
- Do not switch to `fahrudinsusnjar-eng/LATSES` for this workflow.
- Codex/GitHub connector has write access to the canonical repository.

## SCI development order

`SCI 1–145 → gap map → canonical scientific contract → consolidate duplicates → Unit/Dimension/Quantity/Measurement/Uncertainty/Provenance → Validation Gate → BuildingModel integration → SCI verification tests → CI Gate → EXE → Installer → GUI final evaluation`

GUI is not the next target while the scientific contract is open.

## Safe repair loop

1. Read SCI 1–145 and the current implementation map.
2. Inspect the latest failing Actions run; use the **first real failing test/error**, not secondary failures.
3. Fix the smallest canonical source/API problem.
4. Preserve compatibility facades when they are still required by existing imports; compatibility code must not become a second scientific implementation.
5. Commit to the active feature branch.
6. Wait for a new Actions run for the exact commit.
7. If red, inspect logs, fix, commit, and repeat.
8. Do not call a build GREEN from a previous commit.
9. Do not merge until verification and required security checks are GREEN.
10. After merge, verify the new `main` commit through the same chain.

## Evidence-first release sequence

The required sequence for a repair/release checkpoint is:

`failure → first real failing test → smallest canonical fix → exact repair commit → clean PR diff → PR Verification → merge → exact main commit verification → EXE smoke → Installer build/smoke → artifact evidence`

Rules:

1. The repair commit must contain only the intended application fix; CI marker commits are not release evidence and must be removed from the release branch.
2. Before opening the PR, compare the repair head against the current `main` and verify the changed-file list. A clean repair PR must show only the intended file(s).
3. Verification evidence must be tied to the exact commit under test. A green run from another commit does not transfer to the release commit.
4. A workflow run with `total_count: 0`, no executable job, or equivalent infrastructure-only failure is **not** a Verification failure of the application and is not Verification evidence.
5. After merge, identify the exact `main` SHA and verify that the application change is actually present in the merged tree.
6. Only after the exact `main` commit has a valid Verification GREEN may EXE/Installer packaging be treated as the next release stage.
7. Installer/EXE success from an older commit, another branch, or an unrelated merge is not evidence for the current release commit.
8. If Installer fails after Verification is GREEN, analyze the first real Installer failure and repair only the packaging/release cause; do not reinterpret a packaging failure as a scientific/Verification failure unless the logs prove that.
9. Do not report a downloadable artifact until the Installer artifact is successfully uploaded and its exact name, size, SHA-256, and source commit are known.

## Current ReferenceHouse evidence chain — 2026-08-25

### 1. First real failure

PR #146 exposed the first real Verification failure in:

`tests/test_reference_house_showcase.py::test_reference_house_is_complete_and_deterministic`

Observed result:

- Obtained lighting: `801.6 W`
- Expected lighting: `792.0 W`
- Difference: `9.6 W`

The root cause was case-sensitive room-name classification in `ReferenceHouse.lighting_w()`. `Glavna spavaća soba` was not matched by the bedroom classifier because the comparison expected `Spavaća` with an uppercase initial character.

### 2. Canonical fix

Commit:

`f03cf71df148261da159e0635d683635aa920530`

Message:

`fix: classify reference-house bedrooms case-insensitively`

Scope verified from the commit diff:

- `lat_ces/reference_house.py` only
- `5` additions / `4` deletions
- normalization uses `casefold()` before room classification

The fix did not intentionally modify BuildingModel, GUI, or the physical model.

### 3. CI marker-commit incident and cleanup

Temporary CI trigger commits were created on the repair branch while trying to force workflow execution. They were not application changes and are not release evidence.

The repair branch was subsequently reduced so that its intended application state was the single `f03cf71` repair commit. PRs that did not carry a clean application diff were closed rather than merged as release evidence.

### 4. Clean-main verification outcome

The repair content was subsequently observed in the canonical `main` tree. Current `main` commit at this checkpoint:

`1493e12ab843535526180ef1175e4ef823d9da9a`

`main` contains the case-insensitive lighting implementation (`name = r["name"].casefold()`).

PR #151 merged to `main` at this point; however, earlier PR inspections showed misleading zero-file diffs on some intermediate clean-branch attempts. Therefore the accepted fact is the **current `main` tree content**, not the PR title or commit count alone.

### 5. Verification evidence

A valid `verify-core` job was observed with conclusion `success` in the LAT-CES Verification Pipeline run:

- Verification Pipeline run: **#812**
- Job: `verify-core`
- Conclusion: **SUCCESS**
- Checkout: SUCCESS
- Python setup: SUCCESS
- Project/dependency installation: SUCCESS
- Wheel/package discovery: SUCCESS
- LAT-CES Verification tests: SUCCESS
- First failing-test reporting step: SKIPPED (no failure)

This is the accepted Verification GREEN evidence for the ReferenceHouse repair chain.

Important limitation: the connector's commit-scoped workflow lookup does not expose a stable direct association for every historical run. Therefore future release checkpoints must record the exact tested SHA and workflow run together before declaring release readiness.

### 6. Installer/EXE status

Installer/EXE must remain a separate downstream gate.

Known recent Installer failures are recorded as failures, not as release evidence. In particular, Installer runs observed around the ReferenceHouse recovery trail included failures despite Verification runs succeeding.

Do not reuse those older Installer failures or successes as evidence for the current `main` release commit.

### 7. Required next sequence

Starting from the current confirmed `main` commit:

`1493e12ab843535526180ef1175e4ef823d9da9a`

perform exactly:

1. Confirm the current `main` SHA before packaging.
2. Start a fresh Windows Installer run for that exact commit.
3. Inspect the first real Installer failure, if any.
4. If Installer fails, fix only the demonstrated packaging cause and rerun Installer on the resulting exact commit.
5. Require all relevant Installer stages to be GREEN: desktop import, pytest, GUI EXE build, packaged EXE smoke test, GUI identity smoke test, Inno Setup compilation, installer smoke test, and artifact upload.
6. Record the final Installer run number, exact source commit, artifact name, artifact size, and SHA-256.
7. Only then report the EXE/Installer as release-ready.

## Verification gate

The minimum release gate is:

- LAT-CES Verification Pipeline: `SUCCESS`
- CodeQL: `SUCCESS`
- Windows Installer: `SUCCESS`
- Wheel/package discovery: `SUCCESS`
- Full pytest suite: `SUCCESS`
- Complete desktop application import: `SUCCESS`
- PyInstaller GUI EXE created: `SUCCESS`
- Packaged EXE smoke test: `SUCCESS`
- GUI identity smoke test: `SUCCESS`
- Inno Setup compilation: `SUCCESS`
- Installer smoke test: `SUCCESS`
- Installer artifact upload: `SUCCESS`

Only after all gates are green is the EXE/installer considered ready.

## Verified successful baseline — 2026-08-24

Commit:

`41a53123a10778675b6c05984b05eeb65bf3e88c`

Successful runs:

- LAT-CES Verification Pipeline **#735** — SUCCESS
- CodeQL Advanced **#9** — SUCCESS
- LAT-CES Windows Installer **#587** — SUCCESS

Installer artifact:

- Name: `LAT-CES-Windows-Installer`
- Size: `10,993,218` bytes
- SHA-256: `4d2aae9b13f5c107daeec005dc2f7500afad621c9c43d0406e8416252a12f9d0`
- Retention: 30 days

Installer #587 completed every release step: desktop import, pytest, GUI executable build, packaged EXE smoke test, Inno Setup compilation, installer smoke test, and artifact upload.

## Known repair history — preserve these lessons

### Measurement import regression

Introducing the canonical `lat_ces.scientific.measurement` package can shadow the former `measurement.py` API. Existing public names such as `AccuracySpec`, `MeasurementDevice`, `OutOfRangeError`, and `PhysicalQuantity` must remain available through the intended compatibility import path until all consumers migrate.

### ReferenceHouse resource regression

`importlib.resources.files("lat_ces")` is unsafe when `lat_ces` is a namespace-style package in the tested environment. Reference-house bundled data must resolve through the canonical module/resource location so both source checkout and built wheel remain functional.

### ReferenceHouse test drift

Do not inflate the model to satisfy stale tests. When deterministic canonical ReferenceHouse values changed legitimately, update the stale test expectations to the canonical model and keep physical assertions meaningful.

## Current architectural rules

- One canonical implementation per scientific concept.
- Compatibility facades may re-export; they must not define competing semantics.
- Derived scientific results retain provenance, assumptions, lineage, uncertainty/confidence and validation state.
- Measurements are not conclusions; AI/heuristic suggestions are not authoritative scientific facts.
- BuildingModel consumes validated scientific contracts.
- GUI consumes BuildingModel/scientific results; it should not become the source of scientific truth.
- EXE/installer packaging is a release verification stage, not a substitute for scientific verification.

## Release evidence format

When reporting readiness, record the exact commit SHA, workflow run numbers, conclusions, artifact name, artifact size, and SHA-256. Never report “ready” from an earlier commit or from a workflow that has not completed.
