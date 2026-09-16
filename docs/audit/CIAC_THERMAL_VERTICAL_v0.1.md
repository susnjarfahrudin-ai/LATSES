# CIAC Thermal Property Vertical v0.1

## Scope

One isolated proof vertical for `thermal_conductivity`:

`PropertyInstance → CalculationContext → Admission → CAP → Result lineage`

## Boundary

- `PropertyInstance` remains the evidence-bearing identity object.
- `CalculationContext` defines property, subject, unit and calculation purpose.
- Admission is context-bound and rejects property/subject/unit/value mismatches.
- `ACCEPTED_FOR_CALCULATION` is computational admission, not epistemic verification.
- The admitted value enters the thermal formula at the consumer function; that point is the isolated CAP.
- The result retains property, subject, context and formula lineage.

## Explicitly not included

- `Material` mutation
- `BuildingModel` mutation
- production `calculate_room_heat_losses()` mutation
- reconciliation
- canonical governance replacement
- solver changes
- density / Young's modulus verticals

## Current status

This is an isolated CIAC proof vertical stacked on the PropertyInstance foundation. It does not claim that the existing production thermal consumer has been migrated to CIAC admission. That migration requires a separate evidence-backed change.
