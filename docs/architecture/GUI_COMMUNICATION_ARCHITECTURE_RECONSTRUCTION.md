# LAT-CES GUI Communication Architecture — Reconstruction Step 1

## Scope

This document records the first reconstruction step: prepare stable GUI communication boundaries without redesigning the engineering/scientific core and without inventing consumers that are not yet evidenced.

The target flow is:

```text
USER
  ↓
GUI
  ↓
GUI COMMAND / INPUT CONTRACT
  ↓
GUI ADAPTER
  ↓
INPUT CONTROL / ROUTING
  ↓
DOMAIN / MODEL ADAPTER
  ↓
LAT-CES CORE
  ↓
RESULT / EVENT / STATE CONTRACT
  ↓
PRESENTATION ADAPTER
  ↓
GUI

LAT-CES CORE
  ↓
EXTERNAL HANDOFF ADAPTER
  ↓
EXTERNAL SYSTEM
```

## Existing direct GUI communication found before this step

### `lat_ces/gui_complete.py`

The current canonical workspace contains direct calls/imports to engineering/domain owners, including:

- `build_building_engineering_report(self.workflow.model)`
- `calculate_structural_loads(self.workflow.model)`
- `ensure_mep_registry(self.workflow.model)`
- `ensure_engineering_results(registry)`
- direct mutation of `self.workflow.model` and its levels/walls/materials
- direct invocation of `MaterialInputDialog`
- direct assignment of `wall.material_id`, `wall.load_bearing`, `wall.tributary_width_m`
- direct creation of `EngineeringMEPWorkspaceApp`

These are recorded as **architectural findings**, not automatically refactored in this step. Their owners and production consumers must be traced before introducing routing that could change semantics.

### `lat_ces/gui_launcher.py`

The launcher is a presentation/compatibility layer over the canonical GUI. The current implementation adds visual presentation behavior and canonical element drawing. It must not become a hidden mutation/monkey-patch layer or a second runtime authority.

The current launcher explicitly subclasses the canonical workspace rather than mutating it at import time. This is a useful existing boundary, but its presentation responsibilities should remain separate from engineering authority.

### `lat_ces/scene1_gui_mixin.py`

Before this reconstruction step, Scene 1 GUI code directly imported and called:

- `BuildingVisualizationAdapter`
- `PresentationController`
- `write_blender_exchange`

Those direct communication points have now been moved behind `lat_ces.gui_architecture` adapters. The GUI retains only user interaction, canvas presentation, and workflow state handling.

## Historical PR #298 finding

PR #298 (`Fahro terenska aplikacija`) is treated only as historical evidence of useful communication patterns. It demonstrates a pattern where real input, test input and simulation can converge on a common processing contract, and where input can pass through an adapter/server/event path before processing.

It is **not** adopted as the LAT-CES canonical GUI architecture. In particular, its monolithic dashboard, safety/governance ownership and standalone runtime structure are not imported into the production GUI architecture.

## Stable contracts introduced

`lat_ces/gui_architecture/contracts.py` defines transport-level interfaces:

- `GUICommand`
- `GUIEvent`
- `GUIResult`
- `GUIState`
- `GUICommandAdapter`
- `DomainModelAdapter`
- `PresentationAdapter`
- `ExternalHandoffContract`
- `BoundaryStatus`

These contracts intentionally do not define `BuildingModel`, engineering rules, verification authority, governance, provenance authority, safety decisions, telemetry engines or external-tool state.

## Stable adapters introduced

`lat_ces/gui_architecture/adapters.py` introduces thin adapters which reuse existing owners:

- `Scene1Adapter` → existing `BuildingVisualizationAdapter` + `PresentationController`
- `ThreeDHandoffAdapter` → existing `write_blender_exchange`
- `PreparedGUICommandAdapter` → explicit `NOT_YET_CONNECTED` preparation point; it does not invent a production consumer

No new engineering mathematics or model authority is introduced.

## Negative architecture tests

`tests/test_gui_communication_architecture.py` checks that:

1. GUI communication contracts are transport-only.
2. Scene 1 GUI code does not directly import presentation or external handoff implementations.
3. A future command boundary explicitly refuses to invent a consumer while `NOT_YET_CONNECTED`.
4. Existing Scene 1 and 3D boundaries are explicitly marked `CONNECTED`.
5. The GUI contract module does not define or import a second `BuildingModel` authority.

## What remains deliberately unconnected

The following are **PREPARED / NOT YET CONNECTED** until a real production consumer is identified:

- general GUI command → core routing
- GUI input → canonical domain/model adapter
- core result → universal result/event contract
- evidence/provenance → GUI state contract
- MEP → 3D projection
- geodetic input → placement → BuildingModel
- production GUI → actual Blender process execution

No consumer is invented merely to make an interface appear complete.

## Owner rule

If an audit encounters:

> Which layer is the real owner?

the correct action is an **ARCHITECTURAL FINDING** containing:

1. boundary description,
2. existing consumer,
3. existing owner,
4. evidence that is proven,
5. evidence that is not proven.

No ownership is assigned by assumption.

## Reconstruction criterion

The first-stage GUI criterion is:

> **GUI knows what the user wants, but does not need to know how LAT-CES performs the internal engineering operation.**

The reconstruction is therefore a preparation layer, not a claim that the complete future adapter architecture is already implemented.
