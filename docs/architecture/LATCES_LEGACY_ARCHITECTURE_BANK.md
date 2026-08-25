# LATCES Legacy Architecture Bank — Candidate Sources

## Purpose

This document is a persistent reminder and controlled candidate bank for useful architecture, scientific models, contracts, tests, and design ideas found in older LATCES development lines.

It is **not** an instruction to merge legacy branches wholesale.

Candidates may be promoted into the current canonical architecture only after architectural review, canonical ownership review, implementation, tests, and Verification/CI acceptance.

## Current release checkpoint

- Release checkpoint: `main @ 3ef25c28fa978ef591e6316e1ad725842c6ab4a8`
- Do not disturb the release checkpoint while the current Windows release chain is being verified.

## Primary legacy source reviewed

### PR #1

- Source repository: `fahrudinsusnjar-eng/LATSES`
- Source branch: `fahrudinsusnjar-eng:main`
- Source SHA: `170ec750f9aaa4ecba227bf9401674919e8abd81`
- Target repository: `susnjarfahrudin-ai/LATSES`
- Status: closed, not merged
- Role: **legacy architecture source / candidate source**

## Candidate disposition rules

Every candidate must receive exactly one of:

- `KEEP`
- `MERGE INTO CANONICAL`
- `ADAPT`
- `ALREADY IMPLEMENTED`
- `REJECT`

## PR #1 candidate inventory

| Candidate | Disposition | Notes |
|---|---|---|
| `scientific/models/metadata.py` | `ALREADY IMPLEMENTED` | Current main already has scientific model metadata. |
| `scientific/models/contract.py` | `ALREADY IMPLEMENTED` | Current main already has structural model contract validation. |
| `scientific/models/applicability.py` | `ALREADY IMPLEMENTED` | Current main already has applicability/lifecycle/evidence gating. |
| `scientific/models/registry.py` | `ALREADY IMPLEMENTED` | Current main already has model registry/version/status handling. |
| `scientific/models/reason_codes.py` | `ALREADY IMPLEMENTED` | Current main already has deterministic applicability reasons. |
| `SMC-001 / LAT-ROM-SMC-001` | `KEEP / ADAPT` | Keep as architectural source for future governance contracts; do not treat design PASS statements as runtime proof. |
| `SMC-004` | `KEEP / ADAPT` | Useful review framework; production readiness still requires executable verification. |
| Reynolds number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| Mach number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| Prandtl number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| Nusselt number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| Biot number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| Fourier number | `MERGE INTO CANONICAL` | Candidate scientific equation not present in current canonical fluids layer. |
| `MassFlowEquation` | `ALREADY IMPLEMENTED` | Current main already contains it. |
| `VolumetricFlowEquation` alias | `ALREADY IMPLEMENTED` | Current main already contains it. |
| `derived_units.py` concept | `ADAPT` | Useful abstraction, but do not create a competing unit/dimension authority. |
| physical constants registry | `ADAPT` | Keep typed-constant concept and integrate into the existing canonical scientific registry. |
| `Measurement` abstraction | `ADAPT` | Useful direction for measurement/evidence/provenance; requires canonical boundary design first. |
| alternative `Dimension` implementation | `REJECT` | Would create a second dimension semantics; current SI exponent-vector layer is canonical. |
| alternative `PhysicalQuantity` implementation | `REJECT / EXTRACT IDEAS` | Do not replace the current canonical quantity engine wholesale. |
| Python 3.12 CI migration from legacy PR | `REJECT FOR NOW` | Current Windows packaging baseline is Python 3.10; avoid destabilizing release reproducibility. |
| generated `__pycache__` / `*.pyc` | `REJECT` | Generated artifacts. |
| `*.egg-info/*` | `REJECT` | Generated packaging artifacts. |
| `WRITE_TEST_TEMP.txt` | `REJECT` | Write-test artifact, not product functionality. |

## Promotion workflow

```text
Legacy source
    ↓
Candidate inventory
    ↓
KEEP / MERGE INTO CANONICAL / ADAPT / ALREADY IMPLEMENTED / REJECT
    ↓
Canonical ownership review
    ↓
Scientific/domain review
    ↓
Implementation on controlled branch
    ↓
Focused tests
    ↓
Verification
    ↓
Packaging / installer validation when applicable
    ↓
PR review
    ↓
main
```

## Important invariant

**Never merge a legacy branch wholesale merely because it contains useful ideas.**

The goal is to recover useful scientific and architectural content while preserving the current canonical ownership model and avoiding duplicate systems.

## Next post-release candidates

After the current Windows release checkpoint is closed, the preferred order is:

1. Reynolds / Mach / Prandtl / Nusselt / Biot / Fourier into the canonical scientific equation layer.
2. Physical constants into the canonical scientific registry.
3. Measurement / Evidence / Provenance boundary design.
4. SMC-001 invariants translated into enforceable current governance contracts.
5. SMC-004 review criteria converted into executable acceptance where appropriate.
6. Legacy scientific import / pipeline cleanup.

## Release guard

Until the current release evidence is complete, this bank is **reference-only**. Do not use it as a reason to modify the active release checkpoint.
