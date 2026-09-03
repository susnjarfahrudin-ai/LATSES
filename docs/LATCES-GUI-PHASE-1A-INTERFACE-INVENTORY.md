# LAT-CES GUI Phase 1A — Interface + Physics Inventory

## Purpose

Phase 1A is an inventory and architecture checkpoint before changing production GUI code.
The reference implementation remains `280832b6` / `lat_ces/gui_complete.py` with the existing
`FloorPlanEditor`, `gui_drafting.py`, `gui_mep_engineering.py`, and canonical `BuildingModel`.

This document does **not** introduce a new GUI entrypoint, a second model, or a second Canvas.

## Design rule

**One model → one geometry → one Canvas/view family → many engineering/result overlays.**

The UI is a presentation/editor layer over SCI 1–145 and the canonical domain model.

```text
SCI 1–145 / domain contracts
          ↓
      BuildingModel
          ↓
  ┌───────┼────────┐
  ↓       ↓        ↓
 PLAN   SECTION     3D
  │       │        │
  └───────┼────────┘
          ↓
  Engineering result
          ↓
  Physics visualization
          ↓
  Measurements / validation
```

## Current source inventory

### Shell

`CompleteBuildingWorkspaceApp` currently builds on `DraftingLATCESApp`, which builds on
`EnhancedLATCESApp` and the canonical `LATCESApp`.

### Existing drafting capabilities to KEEP

The existing drafting stack already provides:

- `FloorPlanEditor` and canonical Canvas
- live wall preview
- snapping
- live dimensions
- room placement
- partition wall placement
- door/window placement on walls
- level dimension editing
- 3D zoom
- canonical `BuildingModel` / `Level` / `FloorPlan` ownership

These are not to be rewritten into a parallel editor.

### Existing engineering capabilities to KEEP

`gui_complete.py` already exposes:

- Model / Pogledi
- Omotač / Fasada
- Konstrukcija / Statika
- Proračuni
- MEP
- Fasade

These should become contextual capabilities of the same model rather than a growing collection
of independent GUI screens.

## Phase 1A screen map

### 0. Application shell

```text
┌─────────────────────────────────────────────────────────────┐
│ LAT-CES                                                     │
│ OBJECT   MODEL   ANALYSIS   SYSTEMS   ENERGY   SERVICE   AI │
├────────────┬──────────────────────────────────┬────────────┤
│ TOOLS      │                                  │ PROPERTIES │
│            │          CANVAS                  │            │
│ Select     │     PLAN / SECTION / 3D          │ selected   │
│ Wall       │                                  │ object     │
│ Room       │                                  │ geometry   │
│ Opening    │                                  │ material   │
│ Dimension  │                                  │ engineering│
│ Measure    │                                  │ results    │
├────────────┴──────────────────────────────────┴────────────┤
│ MODEL STATUS | ANALYSIS STATUS | WARNINGS                  │
└─────────────────────────────────────────────────────────────┘
```

**Decision:** MODIFY current shell, do not replace the window class.

### 1. Model view

Primary actions:

- Krov
- Sprat
- Tlocrt
- Presjek
- 3D

**Decision:** KEEP the existing view family; simplify presentation around one persistent workspace.

### 2. Drafting view

Primary tools:

- Select
- Room
- Wall
- Opening
- Dimension
- Snap
- Measure

Existing dimension-first drafting remains the implementation base.

**Decision:** KEEP + MODIFY presentation, not geometry ownership.

### 3. Contextual properties

When an object is selected, the right-side panel should show only properties relevant to that object.

Example wall inspector:

```text
WALL-034

Geometry
  Length       12.00 m
  Height        2.80 m
  Thickness     0.25 m

Material
  Concrete / Block

Engineering
  Load bearing YES
  Tributary    3.20 m

Systems
  Thermal      …
  Acoustic     …
```

**Decision:** ADD/REWORK as the principal simplification mechanism.

### 4. Analysis view

Analysis is selected from the same model and returns results into the same workspace.

```text
BuildingModel
      ↓
Analysis engine
      ↓
validated/scientific result
      ↓
result inspector + overlay
```

**Decision:** REWORK current engineering tabs into contextual analysis modes, not separate model states.

## Physics visualization contract

The interface must be prepared for physical fields even when the corresponding solver is not yet implemented.
The UI must never animate invented physics.

Every physics overlay must have this lineage:

```text
BuildingModel input
      ↓
calculation / simulation
      ↓
validated or explicitly classified result
      ↓
visual layer
```

### Airflow — priority

The Master Interface Codex defines the spatial chain:

```text
outside air
 → filter
 → recovery / exchanger
 → heating / cooling coil
 → plenum
 → room
 → exhaust
 → recovery
 → outside
```

The UI must be able to display, on the same geometry:

- volume flow `Q`
- local velocity `v`
- pressure `p` / pressure loss `Δp`
- temperature
- humidity
- directionality
- distribution
- occupied-zone information
- acoustic indicators where available

Visualization layers:

```text
VECTOR      → velocity arrows
STREAMLINE  → flow paths
SCALAR      → pressure / velocity / temperature field
NUMERIC     → Q, v, Δp, T, RH, SPL, etc.
```

### Heating / cooling

Use the same model and view system:

```text
BuildingModel
    ↓
thermal calculation
    ↓
temperature / heat-flux / load result
    ↓
visual overlay
```

### Acoustics

Acoustic display remains an engineering result layer tied to actual fan, duct, velocity,
pressure-loss and room/system assumptions. It is not a decorative colour field.

### Measurements / validation

Later measurements must be visible without replacing the model result:

```text
CALCULATED / SIMULATED
          ↕
MEASURED
          ↓
comparison / residual / validation
```

Every value keeps its provenance/status as defined by SCI/domain contracts.

## Reference House

Reference House must appear as a **built-in project/fixture action**, not as an arbitrary JSON file the user must find.

```text
PROJECT
  └── Reference House
        ↓
     BuildingModel
        ↓
   existing Canvas
```

The Reference House must not create a second model or a second editor.

## KEEP / MODIFY / ADD / REJECT

| Area | Decision | Reason |
|---|---|---|
| `gui_complete.py` | KEEP | current functional production baseline |
| `FloorPlanEditor` / Canvas | KEEP | canonical editor and geometry view |
| `gui_drafting.py` | KEEP + MODIFY UX | existing snap/live dimensions are valuable |
| `gui_mep_engineering.py` | KEEP | existing engineering capability |
| BuildingModel ownership | KEEP | canonical domain owner |
| Model/Pogledi | KEEP + SIMPLIFY | same model, fewer navigation layers |
| Engineering tabs | MODIFY | become contextual analysis modes |
| Properties inspector | ADD / REWORK | primary simplification mechanism |
| Level/model tree | ADD | direct model navigation |
| Physics overlays | ADD | airflow/thermal/acoustic/energy visualization |
| Measurement comparison | ADD LATER | calculated vs real-system evidence |
| `gui_master.py` | REJECT | experimental parallel shell |
| `gui_release.py` | REJECT | release workaround, not architecture |
| `gui_functional.py` | REJECT | duplicate GUI/model path |
| heuristic Reference House mapper | REJECT | cannot invent engineering geometry |
| second Canvas/model state | REJECT | breaks single-model principle |

## Coordinate / layout map status

This Phase 1A document contains a **source-level component map**. Exact pixel coordinates and screenshots are
not yet normative because they must be measured from the rendered Windows application, not guessed from Tk
packing code.

The next audit must capture:

1. actual window size at startup
2. bounds of top navigation
3. bounds of tool/sidebar area
4. bounds of Canvas
5. bounds of properties/engineering area
6. bounds of status/warnings area
7. visible/occluded controls
8. resize behaviour
9. Reference House action visibility

The installed Windows application remains the final visual authority for this audit.

## Acceptance for Phase 1A

Before production UI code is changed, the following must be documented and tested:

- one production entrypoint (`gui_complete.py`)
- one canonical `BuildingModel`
- one `FloorPlanEditor` / Canvas path
- visible core drafting tools
- visible Reference House action
- contextual object properties
- PLAN / SECTION / 3D on the same model
- explicit place for physics overlays
- explicit place for measured-vs-model comparison
- no `gui_master.py` / `gui_release.py` reintroduction

## Guiding principle

**Simple interface, deep model.**

The user should see only the controls needed for the current task. The complexity belongs in the
canonical BuildingModel, scientific contracts, calculation engines, evidence/provenance, and validation layers,
not in a crowded GUI.
