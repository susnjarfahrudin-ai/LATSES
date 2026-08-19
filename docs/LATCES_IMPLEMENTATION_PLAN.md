# LATCES Implementation Plan

## Goal
Turn the Master Interface Codex into a real shared building model. The GUI must consume one authoritative geometry/physics model instead of maintaining independent drawing-only state.

## Phase 1 — Foundation (this branch)
1. `BuildingModelCore`: project, levels, rooms, materials and object registry.
2. `Geometry/WallOpening`: walls are volumetric; doors/windows subtract real openings from the wall envelope.
3. `Airflow`: flow, area, velocity, ACH and basic stack-effect estimate; explicit distinction between measured/calculated/declarative values.
4. `Water`: hydraulic flow/velocity/pressure-loss inputs plus water-quality evidence/status model.
5. `Heating`: room heat-load baseline and emitter selection for underfloor/radiator/wall/ceiling/air systems.
6. `AI/Recommendation`: evidence-backed recommendations with human accept/reject/edit state.
7. `Validation`: PASS/PARTIAL/FAIL/NOT_IMPLEMENTED/UNKNOWN result model and cross-module checks.

## Phase 2 — GUI integration
- Replace drafting-only state with `BuildingModelCore` objects.
- Room creation writes real rooms.
- Wall creation writes real walls.
- Door/window creation snaps to a wall and creates a real opening.
- 2D, section and 3D read the same geometry.
- Opening tests: door 0.90 x 2.10 m in wall height 2.80 m produces a void from z=0 to 2.10 m and wall above from 2.10 to 2.80 m.

## Phase 3 — Engineering integration
- Connect existing plenum/pressure/duct/fan/thermal engines instead of duplicating them.
- Add water/drainage networks.
- Add heating/cooling, daylight, electrical, solar, structural and acoustic adapters.

## Phase 4 — Evidence and AI
- Instrument registry: manufacturer, model, accuracy, range, calibration and provenance.
- Evidence registry: declared / verified / measured / user experience / unknown.
- AI research produces source-linked findings; AI recommendations never mutate the model without human approval.

## Phase 5 — Validation and release
- Unit tests for each engine.
- Geometry regression tests for wall/opening relationships.
- GUI smoke test.
- Full CI.
- Windows EXE/Installer from the tested commit.
- Functional acceptance matrix: PASS / PARTIAL / FAIL.

## Non-negotiable architecture
`Nature → science + mathematics + measurements + rules → AI research → LATCES model → analysis → optimization → recommendation → human decision`.

The current implementation is intentionally a foundation. It does not claim that every Codex feature is already implemented.
