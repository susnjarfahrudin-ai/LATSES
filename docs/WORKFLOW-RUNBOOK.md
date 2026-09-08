# LAT-CES CI / Release Runbook — persistent workflow memory

## Canonical architecture

`Scientific Core → BuildingModel → canonical GUI → GUI acceptance → PyInstaller EXE → Windows Installer → artifact + SHA-256 → release evidence`

`BuildingModel` is the source of truth. GUI, structural, thermal, MEP, quantity and visualization views are downstream projections and must not create competing physical models.

## Security and release rules

- One canonical authority per responsibility.
- No parallel key, replay, persistence, evidence, GUI, or BuildingModel authority.
- Release evidence must bind the exact source SHA to Verification, Installer, artifact name, size and SHA-256.
- Never reuse stale evidence from another commit.
- Failure rule: `first concrete failure → exact assertion/log → smallest canonical fix → same gate → GREEN → continue`.

## 2026-09-08 — PR #289: independent FlowGuard falsification proof — MERGED

PR #289 is permanently retained as a **regression/falsification sentinel**, not merely a temporary experiment.

Main merge commit:

`a1f2d7cc2cf9bcd7e5120b4203eddd108a48834b`

Merged test commit:

`6cbc3349e4f2ca42a2efc55b20c07b3fec57f2b3`

The test proves that an independent mathematical witness can detect a deliberately broken FlowGuard candidate. The candidate uses `HARD_STOP = 0.21`, while the independent witness derives:

`120.0000001 / 100 - 1 = 0.200000001 > 0.20`

using exact `Decimal` arithmetic and without calling or reproducing `FlowGuard.evaluate()`.

A second test proves convergence of canonical FlowGuard with that independent witness.

Evidence for the exact merged test head:

- Verification #1627: **GREEN**
- Windows Installer #1406: **GREEN**
- PR #289: **MERGED**
- main: `a1f2d7cc2cf9bcd7e5120b4203eddd108a48834b`

### Canonical mathematical-control workflow

`physical/engineering inputs`
→ `FlowGuard raw result`
→ `independent mathematical witness`
→ `agreement / falsification`
→ `FlowObservation`
→ `DefenseRecord`
→ `provenance / digest`
→ `RCI-AD observation / governance`
→ `downstream component`

Ownership is explicit:

- **FlowGuard:** production mathematical decision.
- **Independent witness/oracle:** independent verification of the mathematical contract.
- **RCI-AD:** observation/evidence governance; no silent rewriting of mathematics.
- **A/B AdaptiveDefense:** runtime continuity, recovery and takeover; not a second mathematical authority.
- **Evidence/provenance:** immutable record of inputs, model/version, result and verification relationship.
- **Scientific governance:** evaluates disagreement and can restrict a model pending controlled replacement.

### Model evaluation and controlled evolution

For every safety-relevant mathematical/physical model:

`MODEL → RAW RESULT → INDEPENDENT CHECK → AGREEMENT?`

If **YES**:

`VERIFIED RESULT → EVIDENCE → PROVENANCE/DIGEST → DOWNSTREAM COMPONENTS`

If **NO**:

`DISAGREEMENT → FREEZE/RESTRICT MODEL AUTHORITY → RECORD EVIDENCE → DIAGNOSE → CONTROLLED REPLACEMENT CANDIDATE → INDEPENDENT CHECK → Verification → GREEN → approval/merge`

A model never establishes its own correctness solely through tests that duplicate its implementation.

### Scope boundary

#289 does **not** authorize:

- changing FlowGuard mathematics;
- allowing RCI-AD to modify FlowGuard decisions;
- creating a second security/key/replay authority;
- creating a second evidence store;
- replacing A/B AdaptiveDefense ownership;
- expanding CyberFortress;
- automatic self-modification of production models.

It establishes the missing independent mathematical falsification capability and permanent regression protection.

## Standard workflow for the next model

`candidate model → independent oracle → intentionally broken candidate → RED/detection proof → restore canonical candidate → GREEN convergence proof → integration audit → Verification → Installer → evidence`

Only after this chain is complete may the candidate become part of the canonical architecture.

## Post-merge rule

For every merged security/mathematical change:

`current main SHA → post-merge Verification → Installer → artifact + SHA-256 → release evidence`

Then proceed to the next candidate one responsibility at a time.

## 2026-09-08 handoff

Current `main` after #289:

`a1f2d7cc2cf9bcd7e5120b4203eddd108a48834b`

The independent-mathematical-control capability is now part of the persistent workflow. Future work should extend this pattern to other safety-relevant models only where a genuine independent source exists; do not create duplicate mathematics merely to satisfy the matrix.
