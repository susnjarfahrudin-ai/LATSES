# Scientific Model Layer — Additional Module Plan

The SCI document defines a four-wave implementation order: Scientific Core, Engineering Core, Physics Engines, then Domain Modules. It explicitly identifies SKO, Units & Dimensions, Quantity & Measurement, Scientific Validation and Scientific Knowledge Registry as the first five components.

## Canonical scientific package additions

- `lat_ces/scientific/core/` — SKO identity, lifecycle, metadata, relationships, contracts
- `lat_ces/scientific/units/` — canonical units and dimensions
- `lat_ces/scientific/quantities/` — physical quantities
- `lat_ces/scientific/uncertainty/` — uncertainty/error propagation
- `lat_ces/scientific/registry/` — scientific object registry
- `lat_ces/scientific/models/` — scientific model metadata, applicability, registry and reason codes
- `lat_ces/scientific/validation/` — scientific validation contract
- `lat_ces/scientific/provenance/` — provenance contract and ledger adapters
- `lat_ces/scientific/reasoning/` — evidence-bound reasoning interfaces
- `lat_ces/scientific/synthesis/` — evidence-bound synthesis interfaces
- `lat_ces/scientific/lifecycle/` — scientific knowledge lifecycle
- `lat_ces/scientific/preservation/` — preservation/integrity interfaces
- `lat_ces/scientific/trust/` — trust/assurance interfaces
- `lat_ces/scientific/governance/` — scientific governance interfaces
- `lat_ces/scientific/ecosystem/` — knowledge ecosystem interfaces
- `lat_ces/scientific/intelligence/` — intelligence/analysis interfaces
- `lat_ces/scientific/security/` — security governance interfaces
- `lat_ces/scientific/smc/` — SMC-001..004 consolidation and acceptance gate

## Existing main evidence

`main` already contains substantial scientific infrastructure including `lat_ces/scientific/models`, `lat_ces/scientific/units`, `lat_ces/scientific/quantity`, `lat_ces/scientific/registry`, measurement, uncertainty, equations and multiple engineering/scientific models. The consolidation branch therefore adds contracts and control artifacts first, and migrates/reuses existing implementations instead of duplicating them.

## Rule

A planned package is **NEW** only when no existing implementation can satisfy its contract. Otherwise it is **ADAPT/MERGE/MOVE**. No scientific formula is invented merely to fill a missing module.
