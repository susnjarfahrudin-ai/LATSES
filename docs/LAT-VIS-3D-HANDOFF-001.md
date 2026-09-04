# LATSES — 3D Renderer Backend Handoff Contract

**Document ID:** `LAT-VIS-3D-HANDOFF-001`  
**Status:** Proposed  
**Parent Architecture:** `LAT-ARCH-3D-001`  
**Scope:** `BuildingScene3D` → external 3-D renderer/backend

## Purpose

This contract closes the boundary between the canonical LATSES 3-D scene representation and an external renderer backend.

```text
Canonical BuildingModel
        ↓
BuildingScene3D
        ↓
Visualization3DBackendEnvelope
        ↓
Blender / ParaView
```

The handoff is a representation transfer only. The external backend does not receive ownership of the physical model or engineering truth.

## Contract

`Visualization3DBackendEnvelope` contains:

- `backend` — selected renderer target: `blender` or `paraview`;
- `contract_version` — stable handoff contract identifier/version;
- `building_model_id` — exact canonical `BuildingModel` identity;
- `source_ref` — canonical source reference;
- `scene` — the immutable `BuildingScene3D` object, passed through unchanged;
- `status` — propagated scene status.

The adapter function is:

```text
Visualization3DBackendEnvelope(
    scene,
    backend,
    contract_version="LAT-VIS-3D-HANDOFF-1",
)
```

## Invariants

1. The `building_model_id` is copied from `BuildingScene3D` and cannot be replaced by a renderer-owned identity.
2. The `source_ref` is copied unchanged.
3. The `scene` is passed by identity; no geometry translation occurs at this boundary.
4. The envelope is immutable.
5. No serialization format is prescribed by this contract.
6. No renderer process is launched by this adapter.
7. No engineering calculation, solver execution, meshing, boolean operation, or geometry repair occurs here.
8. `openfoam` is not a valid target for this 3-D renderer handoff; CFD remains a separate adapter boundary.
9. Empty contract versions are rejected.

## Renderer Responsibility

After handoff, the external backend may interpret the neutral scene for its own rendering pipeline. Backend-specific conversion, scene construction, meshing, procedural geometry, camera setup and rendering belong outside LATSES's canonical model boundary.

```text
LATSES authority
────────────────────────────
BuildingModel
BuildingScene3D
Handoff Envelope
────────────────────────────
        ↓
External backend
────────────────────────────
Blender / Geometry Nodes
ParaView
```

## Explicit Non-goals

- No Blender integration in this change.
- No Geometry Nodes integration in this change.
- No ParaView execution in this change.
- No GUI integration.
- No mutation of `BuildingModel` or `BuildingScene3D`.
- No new physical-object identity.
- No engineering-result ownership transfer.
- No CFD/OpenFOAM integration.

## Acceptance

The boundary is accepted when tests demonstrate:

- Blender and ParaView targets are accepted;
- canonical identity and source reference are preserved;
- the exact `BuildingScene3D` object is carried through unchanged;
- the handoff envelope is immutable;
- unsupported backends are rejected;
- an empty contract version is rejected.

## Next Boundary

Once this contract is GREEN, the next independent change may implement a renderer-specific adapter:

```text
Visualization3DBackendEnvelope
        ↓
Blender adapter
        ↓
Blender / Geometry Nodes scene
```

That future adapter must not modify this contract or introduce a second canonical model identity.
