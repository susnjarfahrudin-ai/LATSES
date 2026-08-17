# SMC-004 — Scientific Model Consolidation Acceptance

**Status:** ACCEPTED WITH CONTROLLED RETIREMENT
**Target:** `main`
**Gate:** CI GREEN → SMC-001 → SMC-002 → SMC-003 → SMC-004

## SMC-001 — Specification traceability

SCI 0001–0055 are represented in `SCI_1-145_MAIN_SMC_MATRIX.md` with explicit responsibility, canonical owner, real implementation/evidence path and decision.

## SMC-002 — Legacy consolidation

The 55/55 legacy sequence is consolidated by responsibility rather than by SCI-number-as-file. Quantity, Units, Equations and Provenance duplicate-resolution rules are explicit. No broad deletion is authorized.

## SMC-003 — Scientific Model contract

Canonical Scientific Quantity, Units/Registry, Measurement and Provenance paths are treated as authoritative. Legacy paths are compatibility infrastructure only where production dependencies require them.

## SMC-004 — Acceptance criteria

Accepted only for controlled retirements proven by repository-wide import search and existing CI evidence. A retirement must preserve canonical imports, provenance continuity and regression behavior.

## Controlled retirement executed

### `lat_ces/modules/quantity.py`

- The file is a compatibility-only re-export of `lat_ces.scientific.quantity.quantity.PhysicalQuantity`.
- Repository-wide search found no production or test imports of `lat_ces.modules.quantity`.
- The canonical implementation remains at `lat_ces/scientific/quantity/quantity.py`.
- Therefore this bridge is authorized for retirement, subject to the post-change CI gate.

## Protected legacy infrastructure

No deletion is authorized for `lat_ces/gov/provenance.py`, `data/provenance_ledger.jsonl`, core dimensions/SKO paths, or scientific model implementations merely because a canonical path exists. Those remain until their individual zero-import and regression gates are satisfied.

## Final gate

Post-retirement CI must be GREEN. If CI fails, restore the retired bridge and investigate before any further retirement.
