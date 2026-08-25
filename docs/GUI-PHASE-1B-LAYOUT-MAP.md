# LAT-CES GUI — Phase 1B Current Layout Map

## Purpose

This is a source-derived map of the current `gui_complete.py` interface and its direct inheritance layers. It is an inventory, not a redesign and not a screenshot replacement.

The authoritative implementation baseline remains `280832b6` / `CompleteBuildingWorkspaceApp` over `FloorPlanEditor` and the existing Canvas.

## 1. Actual inheritance chain

```text
LATCESApp
  ↓
EnhancedLATCESApp
  ↓
DraftingLATCESApp
  ↓
CompleteBuildingWorkspaceApp
  ↓
production gui_complete.py
```

`CompleteBuildingWorkspaceApp` adds the engineering notebook, while `DraftingLATCESApp` and `EnhancedLATCESApp` already provide the live drafting behavior, snapping, room/partition/opening placement, and 3D zoom.

## 2. Actual shell topology

```text
┌─────────────────────────────────────────────────────────────┐
│ Tk root / application shell                                 │
├─────────────────────────────────────────────────────────────┤
│ inherited navigation / stage controls                       │
├─────────────────────────────────────────────────────────────┤
│ CompleteBuildingWorkspaceApp notebook                       │
│ [Model/Pogledi][Omotač][Statika][Proračuni][MEP][Fasade]   │
├─────────────────────────────────────────────────────────────┤
│ inherited body / stage area                                 │
│                                                             │
│   main engineering/model Canvas area        │ side panel   │
│                                             │              │
│                                             │ tools        │
│                                             │ drafting     │
│                                             │ engineering  │
│                                             │ Reference    │
│                                             │ House        │
├─────────────────────────────────────────────────────────────┤
│ status / model / analysis feedback                          │
└─────────────────────────────────────────────────────────────┘
```

The current code uses a fixed sequence of `pack()` and `grid()` calls across inheritance layers. The rendered window, rather than source order alone, is the final authority for the visual coordinate audit.

## 3. Current functional zones

### A. Model / view navigation

Existing controls:

- Krov
- Sprat
- Tlocrt
- Presjek
- 3D

Decision: **KEEP**.

Target: make these view modes operate as views of one `BuildingModel`, not separate model states.

### B. Drafting tools

Already present in `DraftingLATCESApp` / `EnhancedLATCESApp`:

- room creation
- partition-wall creation
- wall creation
- door/window placement
- snapping
- live dimensions
- floor-plan resizing
- 3D zoom

Decision: **KEEP + REORGANIZE**.

The capability exists; the main UX problem is discoverability and density rather than missing drafting logic.

### C. Engineering tabs

Current tabs:

- Model / Pogledi
- Omotač / Fasada
- Konstrukcija / Statika
- Proračuni
- MEP
- Fasade

Decision: **KEEP AS CURRENT BASELINE; REWORK LAYOUT LATER**.

Do not create additional top-level tabs for every scientific discipline.

### D. Side panel

The inherited side panel accumulates controls from multiple layers:

1. base GUI controls
2. drafting palette
3. wall editor
4. Reference House box

Decision: **MODIFY**.

Primary issue: vertical stacking can place lower controls outside the immediately visible region. This is the concrete visibility failure discovered with the Reference House button.

Long-term target: context-sensitive panel showing only the tools/properties relevant to the current mode or selected object.

### E. Properties

Current implementation is distributed across engineering tabs and side controls rather than one coherent object inspector.

Decision: **ADD / REWORK**.

Target:

```text
Selected object
  ├─ Identity
  ├─ Geometry
  ├─ Material
  ├─ Engineering
  ├─ MEP
  └─ Scientific evidence / provenance
```

## 4. Visibility / coordinate risks

The current implementation is primarily layout-flow driven (`pack()` plus notebook placement). That means a widget can exist and pass a callback test while being visually below the fold.

Required manual Windows audit fields:

| Region | Record |
|---|---|
| Window size | actual rendered pixels |
| Main Canvas | x/y/width/height |
| Left/central controls | x/y/width/height |
| Right panel | x/y/width/height |
| Notebook | x/y/width/height |
| Reference House control | x/y/width/height + visible yes/no |
| Status area | x/y/width/height |

No source-level coordinate should be treated as truth until confirmed on the rendered Windows application.

## 5. Simple target layout

The interface should converge toward:

```text
┌─────────────────────────────────────────────────────────────┐
│ PROJECT / MODEL / ANALYSIS / SYSTEMS / ENERGY / SERVICE  │
├──────────────┬──────────────────────────────┬───────────────┤
│ TOOLS        │                              │ PROPERTIES    │
│              │        PLAN / SECTION / 3D   │               │
│ Select       │                              │ selected      │
│ Wall         │                              │ object        │
│ Room         │                              │ geometry      │
│ Opening      │                              │ material      │
│ Dimension    │                              │ engineering   │
│ Snap         │                              │ evidence      │
├──────────────┴──────────────────────────────┴───────────────┤
│ MODEL STATUS | ANALYSIS STATUS | WARNINGS                  │
└─────────────────────────────────────────────────────────────┘
```

The target deliberately has fewer persistent controls and relies on context rather than displaying every subsystem simultaneously.

## 6. Physics visualization contract

The GUI must eventually expose physical fields on the same model and Canvas:

```text
BuildingModel
  ↓
validated physical calculation
  ↓
result field
  ↓
Canvas overlay
```

Required future modes include:

- airflow: volume flow, velocity, pressure, pressure loss, directionality
- thermal: temperature and heat flux
- cooling: cooling load and temperature field
- acoustics: predicted acoustic level / noise field
- measurements: measured values over model geometry
- validation: calculated vs measured residuals and confidence

The Master Interface Codex already defines the airflow chain as outside air → filter → recovery/heat exchanger → coil → plenum → room → exhaust, and requires spatial flow, velocity, pressure, temperature, humidity and distribution analysis. This document reserves UI space for those results; it does not create fake animation or unvalidated visual fields.

## 7. Component decisions

| Component | Decision |
|---|---|
| `CompleteBuildingWorkspaceApp` | KEEP |
| `FloorPlanEditor` / Canvas | KEEP |
| `DraftingLATCESApp` | KEEP |
| `EnhancedLATCESApp` | KEEP |
| Model/View controls | KEEP |
| Existing engineering tabs | KEEP baseline / MODIFY later |
| Side panel stacking | MODIFY |
| Contextual property inspector | ADD |
| Model/Level navigator | ADD |
| Physics overlay layer | ADD later |
| Measurement-vs-model layer | ADD later |
| `gui_master.py` | REJECT |
| `gui_release.py` | REJECT |
| `gui_functional.py` as production entrypoint | REJECT |
| Second Canvas/editor | REJECT |
| GUI-owned duplicate BuildingModel | REJECT |

## 8. Phase 1B acceptance

Phase 1B is complete when:

1. The actual Windows application screenshot is captured.
2. The coordinates of the major zones are recorded.
3. The Reference House control is visibly reachable without scrolling or hidden overflow.
4. PLAN / SECTION / 3D remain the same model views.
5. Drafting tools remain reachable and functional.
6. The map identifies the first low-risk UI change for Phase 2.

## 9. Important boundary

This document does not change `gui_complete.py` or any production GUI code. It only records what exists and what the next UI change must respect.
