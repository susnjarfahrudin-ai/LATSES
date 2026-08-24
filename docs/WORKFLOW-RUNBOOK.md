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
