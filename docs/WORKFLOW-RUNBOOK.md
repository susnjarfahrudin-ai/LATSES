# LAT-CES CI / Release Runbook — persistent workflow memory

## Current validated engineering-GUI checkpoint — 2026-08-26

PR #188 completed the visible Engineering Summary on the canonical `BuildingModel`.

Exact source SHA: `a7af57126ff26820745a516314c301378b87d878`

Evidence:

- Verification #1016: **SUCCESS**
- Windows Installer #836: **SUCCESS**
- CodeQL #239: **SUCCESS**
- Installer artifact: `LAT-CES-Windows-Installer`
- Artifact ID: `9590321023`
- Artifact size: `11,023,789 bytes`
- Artifact ZIP SHA-256: `eeedb03110036ef835d2131b8552a5fe030c3c27cc2bc45d22c353baaf7c1fcb`
- PR merge commit: `c0fee67a16b4948fa158cc7a698fccbaa722975a`

PR #188 extends the visible GUI summary with structural load results, thermal wall inputs, room/wall/opening/stair/terrace quantities and MEP registry counts, while preserving one canonical `BuildingModel` and read-only engineering projections.

## Repair history for the current GUI chain

### PR #185

`280f0d4…` → Verification #1007 GREEN → Installer #827 GREEN → CodeQL #230 GREEN → merge `36a4484…`.

### PR #186

`51299686…` → Verification #1011 GREEN → Installer #831 GREEN → CodeQL #234 GREEN → merge `0c5dbe36b76b3f6d9584ecb57e6f0ffb83780a78`.

First-class Stair/Terrace elements were exposed in the canonical model and visible inspector.

### PR #187

`d517009fec57275c5da123f2ad269f2751a07f0e` → Verification #1014 GREEN → Installer #834 GREEN → CodeQL #237 GREEN → merge `3579f74e278da2da0188d974e10a63d1e2a59b96`.

Room labels were rendered on the floor plan and the Engineering Summary began reading Statics/Thermal data from the same model. The only failed cycle was a test naming mismatch (`Kuhinja` vs the fixture's canonical `Kuhinja + trpezarija`), repaired without weakening the model contract.

### PR #188

`a7af57126ff26820745a516314c301378b87d878` → Verification #1016 GREEN → Installer #836 GREEN → CodeQL #239 GREEN → merge `c0fee67a16b4948fa158cc7a698fccbaa722975a`.

The automated chain is GREEN through the full engineering summary. The remaining release acceptance is visual/interactive Windows confirmation of the installed GUI sequence:

`Reference House → Tlocrt → Presjek → 3D → Provjera → Izvještaj → Materijali`

with wall/room/stair/terrace/statics/thermal/MEP/quantity content visible and coherent.

## Release evidence rule

The release record must always bind the exact source SHA to Verification, Installer, artifact name, artifact size and artifact SHA-256. Historical evidence from another SHA is not reusable.

## Architectural rule

`BuildingModel` is the source of truth. GUI, structural, thermal, MEP and quantity views are downstream read-only projections and must not create competing physical models.
