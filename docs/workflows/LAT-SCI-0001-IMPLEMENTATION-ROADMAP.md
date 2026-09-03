# LAT-SCI-0001 — Implementation Roadmap

**System:** LAT-CES — Living Adaptive Twin – Constitutional Engineering System  
**Document ID:** LAT-SCI-0001-WF  
**Revision:** A  
**Status:** Operational Development Workflow  
**Baseline:** `main @ b7d1bcb0e898c52fa6decc85d4f955dc55f98bd7`

## 1. Objective

Implement the universal Scientific Core without duplicating scientific infrastructure inside domain modules.

## 2. Locked sequence

```text
G0 Constitutional baseline
      ↓
G1 ScientificKnowledgeObject
      ↓
G2 Quantity + Units/Dimensions
      ↓
G3 Measurement / Metrology
      ↓
G4 Uncertainty / Error Analysis
      ↓
G5 Scientific Knowledge Registry
      ↓
G6 Traceability Graph
      ↓
G7 Canonical Physical Identity
      ↓
G8 BuildingModel projections
      ↓
G9 MEP pilot
```

## 3. Rules

1. Every stage is implemented in a small, independently reviewable PR.
2. Each PR must preserve the canonical `BuildingModel` physical identity.
3. Domain modules may consume Scientific Core concepts but may not redefine them.
4. GUI, Jira, email, installer and other infrastructure must remain outside Scientific Core.
5. Missing scientific inputs must remain explicit; no silent invention or fallback substitution is permitted where the selected calculation scope requires the input.
6. A stage cannot be promoted until targeted tests and the full LAT-CES Verification gate are GREEN.
7. `main @ b7d1bcb0` is the reference baseline until the first implementation PR is independently verified and merged.

## 4. PR contract

Each implementation PR must contain:

- one narrowly bounded architectural objective;
- implementation limited to that objective;
- targeted regression tests;
- no unrelated refactoring;
- updated documentation only where required to describe the new stable contract;
- Verification GREEN before merge.

## 5. Stage G1 — ScientificKnowledgeObject

### Objective

Harden the existing canonical `lat_ces.core.sko.ScientificKnowledgeObject` into the first reusable Scientific Core lifecycle boundary.

### Required capabilities

- stable internal identity;
- portable semantic identifier;
- object type;
- version and predecessor reference;
- provenance metadata;
- assumptions and limitations;
- verification/validation references;
- DRAFT → RELEASED lifecycle;
- release hash;
- release timestamp;
- released-object mutation protection.

### Non-goals

- Quantity implementation;
- Measurement implementation;
- uncertainty engine;
- registry implementation;
- BuildingModel changes;
- domain changes.

## 6. Stage G2 — Quantity + Units/Dimensions

Introduce a canonical `Quantity` boundary and connect it to the existing authoritative units/dimensions implementation. No second unit system is permitted.

Acceptance includes dimensional-safe arithmetic and regression protection for affine temperature units.

## 7. Stage G3 — Measurement / Metrology

Introduce traceable measurement records containing observation context, quantity, source/instrument metadata, timestamp and applicable uncertainty/calibration references.

## 8. Stage G4 — Uncertainty / Error

Introduce distinct representations for measurement uncertainty, model uncertainty, numerical error and engineering approximation. Add justified propagation APIs and tests.

## 9. Stage G5 — Scientific Knowledge Registry

Create a discipline-neutral registry with register, lookup, lifecycle, version/successor and provenance support.

## 10. Stage G6 — Traceability

Connect upstream observations, measurements, evidence and models to simulations, verification, validation, engineering results and decision records.

## 11. Stage G7 — Canonical Physical Identity

Create the universal physical identity contract. Every physical object gets one canonical identity that domain projections reference.

## 12. Stage G8 — BuildingModel projections

Expose discipline-specific projections from the canonical `BuildingModel` without creating duplicate authoritative geometry.

Target pattern:

```text
BuildingModel
      ↓
PhysicalIdentity
      ↓
Domain Projection
      ↓
Scientific Validation
      ↓
Engineering Calculation
      ↓
Result
```

## 13. Stage G9 — MEP pilot

Use MEP as the first domain to prove the complete architecture:

```text
BuildingModel
   ↓
MEP projection
   ↓
MEPRegistry
   ↓
HeatingZone / ventilation / water
   ↓
Scientific validation
   ↓
Engineering calculation
   ↓
Verification / result
```

MEP must not re-model building geometry.

## 14. Exit condition

The Scientific Core wave is complete only when all nine gates are independently verified and the complete chain from canonical knowledge/measurement through `BuildingModel` projection to a domain engineering result is demonstrably traceable.
