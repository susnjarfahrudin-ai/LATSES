# Renderer measurement POC — one minimal house

## Test object

The first renderer experiment uses exactly one synthetic `BuildingModel`:

- 1 level: `L1`, 10.0 m × 8.0 m × 2.8 m
- 3 rooms: living room, kitchen, bedroom
- 5 walls: 4 exterior + 1 internal partition
- 1 opening: 1.5 m × 1.2 m window in `W1`, sill 0.9 m, position 2.0 m along the wall

The model is converted through the same renderer-neutral adapter used by all candidate renderers.

## Rule

No renderer is allowed to invent geometry that is not present in the adapter output.

The current `BuildingModel` contains wall dimensions and opening dimensions, but no authoritative wall placement (`x/y/z`) or wall orientation. Therefore a renderer cannot yet reconstruct the physical floor plan without introducing an assumption.

That is an intentional **measurement result**, not a renderer failure.

## Measurement sequence

1. Adapter fidelity: confirm all known dimensions and identities survive.
2. Spatial sufficiency: determine whether the adapter contains enough authoritative facts to place geometry.
3. Renderer execution: only after spatial sufficiency is true, feed the identical scene to FreeCAD, Blender, and Godot.
4. Compare measured output, not appearance:
   - object count;
   - wall/opening dimensions;
   - identity preservation;
   - placement/orientation fidelity;
   - missing-data handling;
   - generation time;
   - process memory;
   - reproducibility in headless mode.

## Current decision

**STOP renderer ranking at the spatial-sufficiency gate.**

The adapter POC is proven for the supplied facts, but the source model does not yet contain authoritative placement/orientation facts. Adding coordinates inside a renderer adapter would violate LAT-CES reality primacy.

The next engineering question is therefore not "which renderer looks best?" but:

> What is the smallest authoritative spatial representation that can be added to `BuildingModel` so that the same physical house can be reconstructed by every renderer without renderer-specific assumptions?
