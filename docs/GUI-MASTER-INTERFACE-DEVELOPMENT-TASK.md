# LAT-CES Master Interface Development Task

## Status

**PLANNED — separate UI development track**

This task implements the functional UI/interface defined by `docs/LATCES_MASTER_INTERFACE_CODEX.md` on top of the proven `280832b6` GUI foundation.

This is a UI task only. Scientific/domain work and Reference House geometry remain separate tracks.

## Normative sources

1. `docs/LATCES_MASTER_INTERFACE_CODEX.md` — Master Interface / functional specification.
2. `docs/GUI-SCI-FOUNDATION-PLAN.md` — current GUI foundation and integration boundary.
3. GUI reference baseline: `280832b68eb157d84fb45f294a9c87cc79013ec8`.

## Baseline that must remain intact

### KEEP

- `lat_ces/gui_complete.py` / `CompleteBuildingWorkspaceApp`
- `lat_ces/gui.py` / canonical `FloorPlanEditor` + Canvas
- `lat_ces/gui_drafting.py`
- `lat_ces/gui_mep_engineering.py`
- direct canonical `BuildingModel` / `FloorPlan` ownership
- `Krov → Sprat → Tlocrt → Presjek → 3D` workflow
- existing engineering tabs

### REJECT

- `lat_ces/gui_functional.py` as a production layer
- `gui_release.py` as a permanent architecture layer
- `gui_master.py` as a replacement production entrypoint
- duplicated GUI/model construction
- a second packaged GUI identity or lifecycle

## Master Codex target

The long-term interface must implement the Codex principle:

**Draw once → model once → measure reality → calculate → optimize → recommend → human decides.**

The GUI is the presentation/editor layer over the authoritative BuildingModel.

### Main navigation

Target top-level areas:

`OBJEKT | MODEL | ANALIZA | SISTEMI | ENERGIJA | SERVIS | AI`

The central workspace must provide the same authoritative geometry through:

`TLOCRT | PRESJEK | 3D`

A persistent status region must expose:

`STATUS MODELA | STATUS ANALIZE | UPOZORENJA`

### Drafting interaction contract

Use the Codex interaction sequence:

`PARAMETAR → KREIRAJ → PREVIEW → LIVE DIMENSION → SNAP → KLIK → OBJEKT`

For rooms, walls, doors and windows:

- dimensions are explicit model data;
- previews follow the cursor;
- snapping is deterministic;
- placed elements become real BuildingModel objects;
- later edits mutate the same objects;
- plan, section and 3D render the same geometry.

### Engineering integration

UI analysis views must consume the same BuildingModel used by drafting. No GUI-local engineering model may be introduced.

Domains in the Codex include, progressively:

- materials and quantities
- airflow / IAQ
- water / drainage
- heating / cooling
- electrical
- daylight / solar
- structure
- energy
- acoustics
- measurements / sensors
- evidence / sources
- serviceability / maintenance
- AI research / engineering advice
- optimization
- validation

The UI may expose a domain before its engine is complete, but its state must be explicit rather than implied by appearance.

## Phase 1 — interface architecture audit

Before changing layout or behavior:

1. Map the current `gui_complete.py` against the Master Codex.
2. Identify `KEEP / MODIFY / MISSING / DEFER` for every visible interface area.
3. Produce a screen/layout map for the current baseline.
4. Identify which widgets already mutate canonical model state.
5. Identify where UI state is currently duplicated or only decorative.

No broad redesign is allowed before this audit exists.

## Phase 2 — shell and navigation

Implement the Codex navigation and workspace structure while keeping the existing Canvas/editor intact.

Acceptance:

- navigation is deterministic;
- switching views does not create another BuildingModel;
- PLAN / SECTION / 3D remain views of the same geometry;
- model status and warnings remain visible;
- existing engineering tabs continue to work.

## Phase 3 — drafting UX

Bring the existing drafting primitives into the Codex interaction contract:

- Room
- Partition wall
- Door
- Window

Acceptance for each object:

- parameter entry;
- live preview;
- live dimensions;
- snap;
- click placement;
- real BuildingModel mutation;
- re-render in the same Canvas;
- persistence/load compatibility.

## Phase 4 — engineering presentation

Expose analysis domains progressively without inventing completion.

Every segment must carry an explicit state:

- `PASS`
- `PARTIAL`
- `FAIL`
- `NOT IMPLEMENTED`
- `UNKNOWN`

The interface must never use the existence of a widget as evidence that the underlying engineering capability is complete.

## Phase 5 — visual/material semantics

3D and model views should represent actual material assignments where the underlying model supports them. Decorative colours must not be presented as physical material truth.

## Testing and release gate

Every major UI slice requires:

1. unit/integration tests where applicable;
2. GUI interaction test against the canonical BuildingModel;
3. full Verification GREEN;
4. packaged EXE smoke GREEN;
5. Windows Installer GREEN;
6. manual Windows confirmation against the reference interface and requested workflow.

The UI development branch must continue to use the single production entrypoint:

`lat_ces/gui_complete.py`

and the bounded packaged-EXE semantics already established by the GUI foundation.

## Explicit non-goals

This task does **not**:

- rewrite SCI 1–145;
- replace the Scientific Core;
- replace BuildingModel;
- replace FloorPlanEditor;
- invent Reference House room geometry;
- restore `gui_master.py`, `gui_release.py`, or `gui_functional.py` as production layers;
- redesign the application in one uncontrolled patch.

## Definition of done

The Master Interface Codex has a traceable implementation matrix against the actual GUI; each implemented UI capability has an explicit acceptance state; the canonical BuildingModel/FloorPlan remains the single source of truth; and the installed Windows application passes the complete GUI → EXE → Installer acceptance chain.
