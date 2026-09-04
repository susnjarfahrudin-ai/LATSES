# LATSES — 3-D Renderer Handoff Contract

**Document ID:** `LAT-VIS-3D-002`  
**Status:** PROPOSED  
**Parent:** `LAT-ARCH-3D-001`  
**Depends on:** `LAT-VIS-3D-001`

## Purpose

This contract defines the exact handoff from the canonical, renderer-neutral `BuildingScene3D` representation to an external 3-D visualization backend.

```text
Canonical BuildingModel
        ↓
BuildingScene3D
        ↓
Visualization3DBackendEnvelope
        ↓
Blender / ParaView
```

The handoff is a representation boundary. It is not a renderer integration and does not execute external software.

## Envelope

`Visualization3DBackendEnvelope` contains exactly:

- `backend`: selected external renderer target (`blender` or `paraview`);
- `contract_version`: `LAT-VIS-3D-HANDOFF-1` by default;
- `building_model_id`: canonical physical-object identity;
- `source_ref`: traceable source reference from `BuildingScene3D`;
- `scene`: the original immutable `BuildingScene3D` instance;
- `status`: propagated scene status.

The scene is passed through unchanged. The envelope does not copy, reinterpret, mesh, serialize or mutate the scene.

## Backend Responsibilities

The LATSES side is responsible for producing a valid `BuildingScene3D` and preserving canonical identity.

The external renderer is responsible for interpreting the scene for visualization. It does not become the owner of `BuildingModel` identity or engineering truth.

```text
LATSES owns:
BuildingModel → BuildingScene3D → Handoff Envelope

Backend owns:
Envelope → renderer-specific scene
```

## Geometry Boundary

`SceneBox3D`, `SceneObject3D` and `BuildingScene3D` remain renderer-neutral. Renderer-specific mesh formats, node graphs, materials, cameras, lighting, scene files and process execution are outside this contract.

## Backend Scope

The first supported visualization targets are:

- **Blender** — 3-D rendering / Geometry Nodes interpretation;
- **ParaView** — scientific visualization / inspection.

`OpenFOAM` is not a 3-D renderer target for this handoff. Its role remains the external CFD solver boundary defined by `LAT-ARCH-3D-001`.

## Invariants

1. `building_model_id` must remain identical across the chain.
2. `source_ref` must remain traceable to the canonical model.
3. `scene` must remain immutable.
4. The handoff must not calculate engineering quantities.
5. The handoff must not infer missing physical geometry.
6. The handoff must not import or execute renderer libraries.
7. A renderer replacement must not require a new `BuildingModel` identity.

## Explicit Non-Goals

This contract does not define:

- Blender Python/API integration;
- Geometry Nodes graphs;
- ParaView pipeline construction;
- mesh generation or triangulation;
- materials/shaders/cameras/lights;
- GUI integration;
- CFD, thermal, structural or acoustic calculation;
- renderer-specific file exchange.

## Acceptance

The boundary is accepted when a `BuildingScene3D` can be wrapped for a supported backend while preserving canonical identity, source provenance, scene object identity and immutability, without importing or executing the backend.
