# LAT-VIS-3D-003 — Blender Runtime Runner

## Boundary

```text
BuildingModel
  ↓
BuildingScene3D
  ↓
Visualization3DBackendEnvelope
  ↓
BlenderSceneSpec
  ↓
BlenderObjectInstruction
  ↓
Blender Runtime Runner (bpy)
```

The runner is the first executable Blender boundary. It consumes only
`BlenderObjectInstruction` values and creates Blender mesh objects.

## Invariants

- `BuildingModel` remains the engineering source of truth.
- Canonical `object_id` and `source_element_id` are copied to Blender custom properties.
- Location, dimensions, and Z rotation are applied directly from the instruction.
- `material_ref` is resolved as a Blender material name and recorded back as metadata.
- `bpy` is imported lazily, so ordinary LAT-CES test and import paths remain Blender-independent.
- The runner performs no engineering calculation and does not mutate LAT-CES model state.

Geometry Nodes remain a subsequent runtime layer; this runner establishes the concrete
Blender object boundary first.
