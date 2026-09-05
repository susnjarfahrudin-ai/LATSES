# LAT-VIS-3D-001 — Canonical 3D Scene Contract

**Status:** Proposed  
**Scope:** Canonical BuildingModel → neutral 3D scene representation  
**Parent architecture:** `LAT-ARCH-3D-001`

## Purpose

Define the missing read-only boundary between the production `BuildingModel` and external 3D renderers.

```text
Canonical BuildingModel
        ↓
3D Scene Adapter
        ↓
Immutable BuildingScene3D
        ↓
Blender / Geometry Nodes / other renderer
```

## Contract

`BuildingScene3D` is a representation of the canonical physical object. It is not a second physical model and does not own engineering truth.

Each `SceneObject3D` preserves:

- `source_element_id` — canonical source element identity;
- `visual_object_id` — stable visual identity derived from the source;
- `element_type` — room, wall or opening in the initial architectural layer;
- renderer-neutral geometry in SI metres;
- optional material reference;
- visual role (`solid`, `void`, or `context`).

## Initial supported layer

Layer A — architectural context:

```text
Level
 ├── Room footprint
 ├── Floor-plan wall segments
 └── Wall openings
```

The adapter does not invent roof placement because the current canonical `Roof` record does not contain a placement/reference frame. Roof visualization is therefore a later explicit contract extension, not an inferred geometry.

## Geometry rules

- Building coordinates remain in metres.
- Wall length and direction come from the canonical `Segment2D`.
- Wall elevation and height come from the canonical `Level`.
- Opening offset, width and height come from the canonical `Opening`.
- Room geometry comes from the canonical `Room.footprint` and its level elevation.
- No meshing, boolean geometry operation, rendering, or engineering calculation occurs here.

## Safety invariants

1. exactly one canonical `BuildingModel` identity;
2. source objects are read-only from the adapter;
3. no renderer dependency;
4. no engineering result mutation;
5. no new physical-model identity;
6. no silent geometric assumptions where canonical placement is unavailable;
7. scene output is immutable;
8. provenance remains traceable to the canonical model and source element.

## Non-goals

Blender integration, Geometry Nodes execution, GUI integration, CFD/flow fields, temperature/comfort/acoustics overlays, measurement rendering, mesh generation, and engineering calculations are outside this contract.

## Acceptance

The contract is implementation-accepted when a canonical `BuildingModel` can be projected into an immutable scene while preserving model identity and exact source geometry for the initial architectural layer.
