# LAT-SCI-0001 — Scientific Core Foundation Workflow

**Document ID:** LAT-SCI-0001-WF  
**Parent:** LAT-SCI-0001  
**System:** LAT-CES — Living Adaptive Twin – Constitutional Engineering System  
**Revision:** A  
**Status:** Active Development Workflow  
**Baseline:** `main @ b7d1bcb0e898c52fa6decc85d4f955dc55f98bd7`

---

## 1. Objective

Build the universal Scientific Core foundation required by LAT-SCOPE-0001 Rev B and LAT-CES-0001 CAR before adding further domain complexity.

The workflow closes the following chain:

```text
ScientificKnowledgeObject
        ↓
Quantity
        ↓
Units & Dimensions
        ↓
Measurement
        ↓
Uncertainty / Error
        ↓
Scientific Knowledge Registry
        ↓
Traceability
        ↓
Canonical Physical Identity
        ↓
BuildingModel projections
        ↓
Domain modules
```

---

## 2. Constitutional Gates

No phase may bypass the following gates:

```text
G0 Constitutional alignment
        ↓
G1 Scientific object contract
        ↓
G2 Mathematical/unit correctness
        ↓
G3 Measurement/metrology correctness
        ↓
G4 Uncertainty/error correctness
        ↓
G5 Registry/traceability correctness
        ↓
G6 Canonical physical identity bridge
        ↓
G7 Domain projection proof
```

A failed gate blocks progression.

---

## 3. Phase 0 — Constitutional Baseline

### Objective

Make the governing documents explicit references for implementation.

### Required references

- `LAT-CES-0000` — Constitutional Engineering Manifesto
- `LAT-SCOPE-0001 Rev B` — Universal Engineering Scope & Domain Architecture
- `LAT-CES-0001` — Constitutional Architecture Reference
- `LAT-SCI-0001` — Scientific Core Foundation

### Exit criteria

- repository contains canonical copies or authoritative references;
- revision/status is explicit;
- change control is defined;
- implementation backlog references these documents.

---

## 4. Phase 1 — ScientificKnowledgeObject

### Objective

Close the universal lifecycle of scientific knowledge objects.

### Work

- consolidate existing `lat_ces/core/sko.py` implementation;
- define canonical identity rules;
- define lifecycle states;
- define release/immutability behaviour;
- define successor/predecessor version relationships;
- define provenance fields;
- define verification/validation references.

### Acceptance tests

```text
create draft
→ mutate
→ verify
→ release
→ reject mutation
→ create successor
→ preserve predecessor trace
```

### Exit gate

SKO contract is canonical and reusable by domain-independent code.

---

## 5. Phase 2 — Quantity

### Objective

Introduce dimension-safe physical quantities.

### Target model

```text
Quantity
├── value
├── unit
├── dimension
├── provenance
└── uncertainty
```

### Required behaviour

- compatible arithmetic;
- incompatible-dimension rejection;
- explicit conversion;
- no silent unit assumptions;
- immutable released quantity records where applicable.

### Acceptance tests

Examples:

```text
2 m + 30 cm          → valid
2 m + 3 s            → reject
1000 W = 1 kW        → valid conversion
20 °C arithmetic     → requires explicit temperature semantics
```

---

## 6. Phase 3 — Units & Dimensions

### Objective

Consolidate the existing canonical units/dimensions implementations.

### Rule

There shall be one authoritative unit/dimension implementation.

Compatibility modules may re-export it but may not implement a second system.

### Work

- inspect `lat_ces/scientific/units/`;
- inspect `lat_ces/scientific/dimensions/`;
- preserve compatibility facades;
- close gaps in dimensional algebra;
- formalize affine-unit handling;
- integrate with Quantity.

### Acceptance tests

- base dimensions;
- derived dimensions;
- dimensional algebra;
- conversion;
- temperature offsets;
- invalid operations.

---

## 7. Phase 4 — Measurement & Metrology

### Objective

Implement the Reality → Measurement boundary from LAT-SCOPE Rev B.

### Minimum model

```text
Measurement
├── measurement_id
├── quantity
├── value
├── unit
├── method
├── instrument
├── timestamp
├── subject/reference
├── uncertainty
├── source/operator
└── traceability
```

### Required capabilities

- measurement identity;
- source/evidence;
- calibration reference when applicable;
- uncertainty representation;
- timestamp/location/context;
- immutable released measurement record;
- predecessor/version handling.

### Exit gate

A measurement can be linked to a physical quantity and traced to its source/context.

---

## 8. Phase 5 — Uncertainty & Error Analysis

### Objective

Make uncertainty a first-class scientific concept.

### Required concepts

```text
Measurement uncertainty
Input uncertainty
Model uncertainty
Numerical error
Approximation
Confidence/status
```

### Work

- define uncertainty representation;
- define basic propagation rules;
- distinguish uncertainty from deterministic error;
- define validation of uncertainty inputs;
- make uncertainty reportable in engineering results.

### Exit gate

Domain modules can carry uncertainty without inventing or hiding it.

---

## 9. Phase 6 — Scientific Knowledge Registry

### Objective

Provide one registry for canonical SKO lifecycle and lookup.

### Required operations

```text
register
lookup
version
successor
predecessor
release
status
provenance
verification link
validation link
```

### Rule

The registry is domain-neutral. It must not become an HVAC, MEP, GUI or project-management registry.

### Exit gate

Any released scientific object can be resolved by stable identity and traced through its lifecycle.

---

## 10. Phase 7 — Traceability Graph

### Objective

Close the proof chain between evidence, models, simulations and decisions.

### Target graph

```text
Measurement / Evidence
        ↓
Quantity / Input
        ↓
Scientific Law / Model
        ↓
Engineering Model
        ↓
Simulation / Calculation
        ↓
Verification
        ↓
Validation
        ↓
Engineering Result
        ↓
Decision Record
```

### Exit gate

A selected engineering result can answer:

- what inputs produced it;
- what model was used;
- what assumptions applied;
- what verification was performed;
- what evidence supports it.

---

## 11. Phase 8 — Canonical Physical Identity

### Objective

Formalize the one-object/one-identity rule for all domain modules.

### Rule

```text
One physical object
        ↓
one canonical identity
        ↓
multiple domain projections
```

### BuildingModel target

```text
BuildingModel
   ├── Room R01
   ├── Wall W01
   ├── Opening O01
   └── Material M01
```

Each domain references these identities rather than copying authoritative geometry.

### Exit gate

No new domain module may introduce a parallel authoritative representation of existing BuildingModel geometry.

---

## 12. Phase 9 — BuildingModel Scientific Projection

### Objective

Connect the canonical BuildingModel to the Scientific Core without making the Scientific Core dependent on BuildingModel.

### Direction

```text
BuildingModel
      ↓
projection / adapter
      ↓
scientific input objects
```

### Example

```text
Room R01
  ↓
ThermalZoneInput
  ↓
validation
  ↓
thermal calculation
```

The projection may extract geometry, construction and material properties, but it does not become a second source of truth.

---

## 13. Phase 10 — MEP / Thermal Pilot Domain

Only after the Scientific Core foundation gates are sufficiently complete:

```text
BuildingModel
      ↓
MEPRegistry
      ↓
HeatingZone
      ↓
ThermalZoneInput projection
      ↓
Validation Gate
      ↓
Heating / ventilation calculation
      ↓
Engineering Result
```

### Rule

MEP remains a pilot domain. It must consume the Scientific Core and canonical BuildingModel rather than redefine universal concepts.

---

## 14. Phase 11 — Domain Expansion

After MEP pilot validation:

```text
STRUCT
THERMAL
ENERGY
FLUID
ELECTRICAL
ACOUSTICS
CONTROL
...
```

Each domain must demonstrate:

- canonical physical identity usage;
- Scientific Core usage;
- validation/verification contract;
- traceability;
- no duplicated universal concepts.

---

## 15. Change-Control Rules

### Allowed

- additive scientific capabilities;
- bug fixes preserving contracts;
- explicit schema/version evolution;
- compatibility facades that preserve one canonical implementation;
- new domain projections.

### Not allowed without formal architectural review

- second unit/dimension engine;
- second SKO authority;
- parallel physical identity model;
- domain ownership of universal scientific concepts;
- bypassing validation to produce a result;
- hiding uncertainty;
- coupling Scientific Core to GUI or project-management tools.

---

## 16. Verification Workflow

Every phase follows:

```text
READ-ONLY ARCHITECTURAL AUDIT
        ↓
MINIMAL IMPLEMENTATION
        ↓
TARGETED TESTS
        ↓
REGRESSION TESTS
        ↓
LAT-CES VERIFICATION
        ↓
ARCHITECTURAL REVIEW
        ↓
MERGE
```

After merge:

```text
main commit
   ↓
post-merge Verification
   ↓
if GREEN → next phase
if FAIL  → first failure only
```

Installer/EXE evidence is not considered a substitute for Scientific Core verification.

---

## 17. Current State and Next Work

Baseline:

```text
main @ b7d1bcb0
```

Known existing foundations:

```text
SKO                         PARTIAL / existing implementation
Units & Dimensions         EXISTING / consolidate
BuildingModel              EXISTING / canonical foundation
MEPRegistry + HeatingZone  EXISTING / canonical MEP foundation
Thermal Input Contract     PR #213 / separate review
Measurement                NOT CLOSED
Uncertainty Engine         NOT CLOSED
Scientific Registry        NOT CLOSED
Traceability Graph         NOT CLOSED
PhysicalIdentity Contract  NOT CLOSED
BuildingModel projection   NOT CLOSED
```

### Immediate next order

```text
1. Freeze/document constitutional references
2. Close SKO contract
3. Close Quantity + Units/Dimensions
4. Implement Measurement + uncertainty
5. Implement Scientific Knowledge Registry
6. Implement traceability graph
7. Formalize PhysicalIdentity
8. Build BuildingModel projection contract
9. Re-evaluate PR #213 against the new foundation
10. Complete MEP/Thermal pilot
```

---

## 18. Completion Definition

The Scientific Core foundation is complete only when an engineering result can be followed backward:

```text
Engineering Result
      ↓
Calculation / Simulation
      ↓
Engineering Model
      ↓
Scientific Model / Law
      ↓
Quantities + Units
      ↓
Measurements / Evidence
      ↓
Physical Reality reference
```

and every step is identifiable, traceable, testable and governed by the LAT-CES constitutional hierarchy.

---

## 19. Final Rule

> **Do not add domain complexity to compensate for an unfinished universal core.**
>
> **Finish the reusable scientific infrastructure first; then use MEP as the first domain proving the architecture works.**
