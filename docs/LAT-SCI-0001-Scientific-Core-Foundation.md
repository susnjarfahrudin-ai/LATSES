# LAT-SCI-0001 — Scientific Core Foundation

**System:** LAT-CES — Living Adaptive Twin – Constitutional Engineering System  
**Document ID:** LAT-SCI-0001  
**Revision:** A  
**Status:** Draft for Acceptance  
**Classification:** Scientific / Foundational Architecture  
**Normative References:** LAT-CES-0000, LAT-SCOPE-0001 Rev B, LAT-CES-0001 CAR

---

## 1. Purpose

LAT-SCI-0001 defines the first implementation boundary of the universal Scientific Core of LAT-CES.

Its purpose is to establish a discipline-neutral scientific information lifecycle that can be reused by structural, MEP, thermal, energy, fluid, electrical, acoustic and future domains without duplicating scientific infrastructure.

This document does **not** define a domain calculation engine. It defines the scientific objects, units, measurements, uncertainty, registration and traceability foundations on which domain engines operate.

---

## 2. Constitutional Position

LAT-CES shall preserve the authority hierarchy:

```text
REALITY
   ↓
MEASUREMENT / METROLOGY
   ↓
MATHEMATICS
   ↓
NATURAL LAWS
   ↓
ENGINEERING SCIENCE
   ↓
LAT CORE
   ↓
DOMAIN MODULES
   ↓
AI ASSISTANTS
   ↓
USER INTERFACES
```

No Scientific Core component may manufacture a measurement, physical law or engineering fact merely to satisfy a calculation request.

Missing or unverified information must remain explicitly represented and may block a calculation according to the selected calculation scope.

---

## 3. Core Principle — Knowledge Before Calculation

All durable scientific and engineering knowledge entering the LAT-CES information lifecycle shall have:

- a stable identity;
- a defined type;
- provenance or source information where applicable;
- assumptions and limitations where applicable;
- lifecycle state;
- traceability to predecessor or source objects where applicable;
- verification/validation state where applicable.

The Scientific Core must remain independent of GUI, MEP, HVAC, Jira, email, installer and other application infrastructure.

---

## 4. ScientificKnowledgeObject (SKO)

`ScientificKnowledgeObject` is the common knowledge identity/lifecycle boundary.

The existing implementation in `lat_ces/core/sko.py` already provides a foundation consisting of identity, object type, definition, assumptions, limitations, creation metadata, approval metadata, hashing and a one-way release/immutability boundary.

LAT-SCI-0001 formalizes the intended extension of that concept across the Scientific Core.

### Required conceptual SKO types

```text
Observation
Measurement
Evidence
Quantity
Unit
Constant
ScientificLaw
ScientificModel
EngineeringModel
Algorithm
Simulation
Verification
Validation
DecisionRecord
KnowledgeReference
```

A type may be implemented as a specialized object, a typed record or a validated projection, but it must retain canonical identity and traceability.

---

## 5. Immutable Scientific Records

Released scientific records shall not be overwritten in place.

When a scientific fact, measurement, model or verification record is corrected:

```text
previous released object
        ↓
new version / successor
        ↓
explicit predecessor reference
```

This preserves the historical evidence chain.

Mutable draft state is allowed before release.

---

## 6. Universal Identity

Every scientific object shall have a stable machine identity.

The implementation may continue to use UUIDs internally, but the architecture should also support a portable semantic identifier such as:

```text
LAT-SKO-MEAS-2026-00000001
LAT-SKO-LAW-00000015
LAT-SKO-MODEL-00000102
LAT-SKO-VERIFY-00000087
```

The public identifier must not depend on a database implementation or programming language.

---

## 7. Units and Dimensions

The Scientific Core shall treat dimensions and units as first-class scientific infrastructure.

Required capabilities:

- SI base and derived units;
- dimension algebra;
- dimensional consistency checking;
- unit conversion;
- explicit handling of affine units such as temperature scales;
- rejection of invalid dimensional operations;
- release/immutability lifecycle for unit definitions.

The existing canonical implementation under `lat_ces/scientific/units/` and `lat_ces/scientific/dimensions/` shall remain the authoritative direction. Compatibility facades must not introduce duplicate unit systems.

---

## 8. Quantity

`Quantity` shall bind a numerical value to a unit/dimension context.

Conceptually:

```text
Quantity
├── value
├── unit
├── dimension
├── provenance
└── uncertainty (optional / applicable)
```

Domain code should prefer quantities over untyped floating-point values when the value represents a physical quantity.

A quantity must not permit dimensionally invalid arithmetic.

---

## 9. Measurement and Metrology

A measurement is not merely a number. It is an observation associated with a measurement context.

The Measurement layer should ultimately support:

```text
Measurement
├── observed quantity
├── value
├── unit
├── instrument / method
├── timestamp
├── location / subject
├── calibration reference (when applicable)
├── uncertainty
├── operator / source
└── traceability metadata
```

The absence of a metrology implementation is a known gap on `main @ b7d1bcb0` and is a P0 foundation item for LAT-SCI-0001.

---

## 10. Uncertainty and Error

The Scientific Core shall distinguish:

```text
measurement uncertainty
model uncertainty
numerical error
input-data uncertainty
engineering approximation
```

The target architecture shall provide:

- uncertainty representation;
- propagation where mathematically justified;
- error identification;
- confidence/status records;
- traceable reporting of assumptions and limits.

No downstream domain may hide uncertainty merely because a calculation API expects a scalar.

---

## 11. Scientific Knowledge Registry

The Scientific Core shall provide a canonical registry for SKO objects.

The registry shall support, at minimum:

```text
register
lookup
version
successor/predecessor relation
lifecycle state
provenance
verification/validation references
```

The registry is a knowledge authority, not a domain database.

---

## 12. Traceability Graph

The target relation chain is:

```text
Reality / observation
      ↓
Measurement / Evidence
      ↓
Quantity / Model input
      ↓
Scientific model / Law
      ↓
Simulation / Calculation
      ↓
Verification / Validation
      ↓
Engineering result
      ↓
Decision record
```

Every domain result should be able to report which upstream objects influenced it.

---

## 13. Canonical Physical Identity

LAT-CES shall maintain exactly one authoritative physical identity for each physical object.

This applies especially to the canonical `BuildingModel`.

Example:

```text
BuildingModel
   └── Room R01
        ├── structural projection
        ├── thermal projection
        ├── MEP projection
        ├── energy projection
        └── acoustic projection
```

Domain modules must not create alternative authoritative copies of the same building geometry.

They may create discipline-specific projections, properties, scenarios, constraints and analysis results referencing the canonical physical identity.

---

## 14. BuildingModel Relationship

The canonical direction is:

```text
BuildingModel
      ↓
canonical physical identity / geometry / construction
      ↓
discipline projection
      ↓
scientific validation
      ↓
engineering calculation
      ↓
result
```

For thermal/MEP use:

```text
BuildingModel
      ↓
Thermal/MEP projection
      ↓
ThermalZoneInput / HeatingZone references
      ↓
Validation Gate
      ↓
Thermal / MEP calculation
```

`ThermalZoneInput` is an analysis input projection. It must not become a second authoritative building model.

`HeatingZone` remains a MEP domain object identified by the canonical room/physical identity.

---

## 15. Domain Neutrality

LAT-SCI-0001 must not depend on:

- HVAC;
- structural engineering;
- GUI;
- web/API frameworks;
- Jira/Trello;
- email/SMTP;
- installer/build tooling.

Domain modules consume the Scientific Core; they do not redefine its universal concepts.

---

## 16. Verification Requirements

Every LAT-SCI-0001 component shall have:

1. unit tests;
2. contract tests for invariants;
3. dimensional consistency tests where applicable;
4. lifecycle/immutability tests;
5. traceability tests;
6. regression protection for canonical identities;
7. CI Verification before merge.

A GREEN CI run is evidence of software verification, not proof of physical validity. Engineering validation remains a separate responsibility.

---

## 17. Implementation Sequence

The first implementation sequence is:

```text
1. ScientificKnowledgeObject
        ↓
2. Quantity
        ↓
3. Units & Dimensions
        ↓
4. Measurement
        ↓
5. Uncertainty / Error Analysis
        ↓
6. Scientific Knowledge Registry
        ↓
7. Traceability Graph
        ↓
8. BuildingModel physical-identity bridge
        ↓
9. Domain projections
```

The existing unit/dimension and SKO implementations should be consolidated rather than duplicated.

---

## 18. Exit Criteria for LAT-SCI-0001 Foundation

LAT-SCI-0001 foundation is considered complete only when:

- SKO lifecycle is canonical and reusable;
- Quantity is dimension-safe;
- units/dimensions have one authoritative implementation;
- Measurement has a traceable lifecycle;
- uncertainty can be represented and propagated where applicable;
- the Scientific Knowledge Registry is operational;
- traceability relations are queryable;
- `BuildingModel` physical identities can be referenced by domain projections;
- domain modules no longer need parallel physical representations;
- Verification is GREEN for the foundation test suite;
- the change is recorded against the LAT-CES constitutional architecture.

---

## 19. Non-Goals

LAT-SCI-0001 does not attempt to complete:

- HVAC system design;
- structural calculation;
- full EN ISO 52016 thermal engine;
- full ISO 10211 thermal-bridge solver;
- GUI workflow;
- installer/release automation;
- Jira/Trello automation;
- AI decision authority.

Those belong to higher layers or later milestones.

---

## 20. Constitutional Rule

> **No domain module shall become the owner of a universal scientific concept that belongs in the Scientific Core.**
>
> **No domain module shall create a second authoritative representation of an already identified physical object.**
>
> **No missing scientific input shall be silently invented to satisfy a calculation.**

These rules are mandatory design constraints for subsequent LAT-CES development.
