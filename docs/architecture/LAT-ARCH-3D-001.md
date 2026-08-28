# LATSES — Engineering Visualization & Validation Architecture

**Document ID:** `LAT-ARCH-3D-001`  
**Status:** ADOPTED  
**Decision Type:** Major Architecture Decision  
**Scope:** BuildingModel, Engineering Core, CFD, acoustics, comfort, measurements, 2D/3D visualization, illustrations and external visualization/solver backends  
**Date:** 2026-08-28

## 1. Executive Decision

LATSES uses the **Canonical BuildingModel as the sole owner of physical-object identity**, while Engineering Core owns engineering results. External tools are treated as **solver / visualization backends**, not scientific authorities.

```text
LATSES
│
├── CANONICAL BUILDING MODEL
├── ENGINEERING CORE
│   ├── Statics
│   ├── Thermal
│   ├── Fluid
│   ├── Acoustics
│   ├── Comfort
│   └── Engineering validation
├── MEASUREMENT LAYER
├── VALIDATION LAYER
├── VISUALIZATION / EXPORT ADAPTERS
│   ├── 2D
│   ├── 3D
│   ├── CFD
│   └── Illustrations
└── EXTERNAL BACKENDS
    ├── OpenFOAM → CFD solver
    ├── ParaView  → scientific visualization
    └── Blender   → 3D rendering / animation
```

## 2. Fundamental Principles

- `BuildingModel` is the only canonical identity of the physical object.
- Engineering Core owns scientific interpretation and engineering results.
- Measurements represent observations of reality and remain distinct from simulation values.
- Validation compares simulation and measurement without collapsing them into one value.
- Visualization is a representation layer and never changes engineering truth.
- External tools do not own LATSES model identity or engineering authority.

## 3. Canonical BuildingModel

All representations reference the same canonical model identity:

```text
ONE PHYSICAL OBJECT
        ↓
ONE CANONICAL IDENTITY
        ↓
MULTIPLE REPRESENTATIONS
```

There must not be independent identities for a LATSES model, Blender model, or CFD model representing the same physical object.

## 4. Engineering Core

Engineering Core covers at minimum:

```text
Structural · Thermal · Fluid Mechanics · HVAC · Acoustics · Comfort · Energy · Validation
```

An external solver may perform numerical computation, but its output returns through a defined LATSES contract and remains traceable to the canonical model, inputs, solver/version, execution context and result.

## 5. CFD / External Backend Boundary

OpenFOAM is an external CFD solver. ParaView is a scientific visualization/inspection backend. Blender is an engineering visualization interpreter/renderer. Geometry Nodes is a procedural visual layer, not an engineering calculation engine.

```text
Canonical BuildingModel
        ↓
LATSES Adapter
        ↓
External solver / visualization backend
        ↓
LATSES result / representation
```

The backend boundary must preserve model identity, inputs, boundary conditions, materials, solver/version, execution time and returned result provenance.

## 6. Common Visualization Adapter

LATSES will use a common **3D & Illustration Adapter** boundary:

```text
LATSES Results
      ↓
Visualization Contract
      ↓
3D / Illustration Adapter
      ↓
Blender / Geometry Nodes
      ↓
Engineering Scene
```

The adapter translates engineering data into visual representations; it does not alter engineering results.

## 7. Layered Visualization

Visualization is layered so architectural context, dynamic flow, scalar fields and measurements can be inspected independently:

- **Layer A — Architectural Context:** walls, floors, roofs, openings and building elements.
- **Layer B — Dynamic Flow:** velocity, direction, streamlines, particles, jets and recirculation.
- **Layer C — Fields / Acoustics / Comfort:** temperature, pressure, humidity, CO₂, VOC, acoustic level, comfort indices and other scalar fields.
- **Layer D — Measurements:** sensors, locations, measured values, timestamps, units, quality and uncertainty.

Visual effects must never change the underlying numerical values.

## 8. Measurement Layer

A measurement is a real observation, not a derived simulation value. The canonical contract is:

```text
Measurement
├── measurement_id
├── building_model_id
├── quantity
├── value
├── unit
├── timestamp
├── location
├── instrument / sensor provenance
├── uncertainty
└── quality / status
```

Measured and simulated values remain separate.

## 9. Validation Layer

The validation loop is:

```text
BUILDING MODEL
      │
 ┌────┴────┐
 ↓         ↓
SIMULATION MEASUREMENT
 │         │
 └────┬────┘
      ↓
 COMPARISON
      ↓
 DEVIATION
      ↓
 VALIDATION
      ↓
 ENGINEERING RESULT
      ↓
 VISUALIZATION
```

A validation record must preserve quantity, measured value, simulated value, delta, relative error where applicable, tolerance, status, timestamp and provenance.

## 10. Provenance Contract

Every visual engineering element must be traceable:

```text
visual_object_id
      ↓
engineering_result_id
      ↓
simulation_id / measurement_id
      ↓
building_model_id
      ↓
source data
```

For simulation, provenance includes solver/version and input/model context. For measurements, provenance includes sensor/instrument identity and timestamp.

## 11. Engineering Truth vs Visual Representation

**Engineering truth** comes from `BuildingModel`, Engineering Core, Measurement Layer and validated results.

**Visual representation** comes from 2D/3D adapters, Blender, ParaView, Geometry Nodes and illustration adapters.

If the two conflict, engineering truth always wins.

## 12. Backend Independence and Compliance

External backends are replaceable adapters. Replacing Blender, ParaView or OpenFOAM must not require a new BuildingModel identity or a second engineering authority.

Third-party software remains independently licensed and must be represented through appropriate third-party notices and compliance documentation.

## 13. Development Priority

```text
1. Canonical BuildingModel
2. Engineering Result Contracts
3. Measurement Contract
4. Validation Contract
5. Visualization Contract
6. 2D Adapter
7. 3D Adapter
8. CFD Adapter
9. Blender / Geometry Nodes
10. ParaView integration
11. Engineering illustrations
12. Interactive GUI integration
```

No GUI rewrite is authorized by this architecture decision.

## 14. Acceptance Criteria

The architecture is implementation-accepted when the repository can demonstrate:

- one canonical `BuildingModel` identity;
- authoritative engineering results;
- CFD results linked to the canonical model;
- measurements linked to sensor/instrument, location and time;
- simulation ↔ measurement validation;
- the same engineering result represented through 2D, 3D and illustrations;
- traceability from displayed engineering values back to source data.

## 15. Adoption Rule

New modules must comply with this architecture unless an explicit Architecture Decision changes it. A new module must not introduce another BuildingModel identity, engineering-result authority, renderer-owned engineering model, measurement source of truth or CFD result authority.

## 16. Final Decision

**DECISION: ADOPT**

LATSES will use the Canonical BuildingModel, Engineering Core, Measurement Layer, Validation Layer and Visualization Contracts as explicit architectural boundaries. OpenFOAM, ParaView and Blender remain external specialized backends.

> **LATSES računa i zna. Vanjski alati rješavaju specijalizovane zadatke i prikazuju.**

> **Mjerenje zatvara krug između modela i stvarnog objekta.**
