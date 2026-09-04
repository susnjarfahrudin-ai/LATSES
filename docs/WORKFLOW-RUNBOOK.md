# LAT-CES CI / Release Runbook — persistent workflow memory

## Current closure baseline — 2026-09-04

The production architecture is now treated as one canonical chain:

`Scientific Core → BuildingModel → canonical GUI → GUI acceptance → PyInstaller EXE → Windows Installer → artifact + SHA-256 → release evidence`

The desktop GUI entrypoint is `lat_ces.gui_complete:main`. `CompleteBuildingWorkspaceApp` is the production workspace and the floor plan is rendered from the same `BuildingModel` used by downstream structural, thermal, MEP, quantity and visualization projections.

The retired GUI authorities `gui_functional.py`, `gui_release.py` and `gui_master.py` must not be reintroduced into the production packaging path. Historical GUI baseline checks by raw Git blob SHA are not acceptance criteria; acceptance is behavioral and must verify the canonical object path and production entrypoint.

## Latest merged security foundation

### PR #252

Head SHA: `2e2e32ba597449464c0e1d6ad74dbcbc0b7cdcd8`

Merged to `main` as:

`a835f0fdcaeb4aa3829b154b52d3df30adbe98ce`

The security boundary contains the established root-of-trust, key derivation, secure mutable-buffer handling, crash-safe atomic persistence, process identity, HMAC IPC freshness/replay protection, threat scoring/CIDR allowlists, Linux/Windows process hardening, focused tests and LAT-SEC-001 documentation.

Pre-merge release evidence for the exact PR #252 head:

- Verification #1423: **GREEN**
- Windows Installer #1234: **GREEN**
- Installer artifact: `LAT-CES-Windows-Installer`
- Artifact ID: `9921807317`
- Artifact size: `11,062,482 bytes`
- Artifact ZIP SHA-256: `ef658788a2a798bf3bf1fe18ad5aea5c0bbecb5585ea59c332078e3240095f6e`

This security foundation is part of the existing canonical security boundary. A second parallel `cyber_fortress.py` authority using a plaintext `master.key`, independent Fernet state and ad-hoc Manager processes must not be merged as-is. New security work must reuse or extend the existing boundary rather than create competing key, evidence or replay authorities.

## GUI acceptance contract

The canonical behavioral contract is:

`production entrypoint → CompleteBuildingWorkspaceApp → one BuildingModel → active Level → one FloorPlan → FloorPlanEditor/Canvas`

The automated acceptance tests must verify this behavior, not a historical source-file hash. The Windows GUI acceptance remains the release-level check that the visible sequence works coherently:

`Reference House → Tlocrt → Presjek → 3D → Provjera → Izvještaj → Materijali`

Any failure is handled by the project rule:

`first concrete failure → minimal fix → Verification → GREEN → next gate`

## Release evidence rule

A release record must always bind the exact source SHA to Verification, Installer, artifact name, artifact size and artifact SHA-256. Historical evidence from another SHA is not reusable.

A post-merge release chain on `main` is considered proven only when the current `main` commit has successful verification and successful installer packaging with the resulting artifact evidence recorded.

## Pull-request hygiene

Historical GUI/Reference-House experiments that target superseded authorities, obsolete fixture files or fixed historical blobs are **SUPERSEDED** and should be closed rather than repaired into the current architecture.

Domain PRs that contain potentially reusable engineering work remain **ACTIVE/BLOCKED** until rebased onto current `main` and revalidated. An old PR is not a release candidate merely because its branch is technically mergeable.

## Architectural rule

`BuildingModel` is the source of truth. GUI, structural, thermal, MEP, quantity and visualization views are downstream projections and must not create competing physical models.
