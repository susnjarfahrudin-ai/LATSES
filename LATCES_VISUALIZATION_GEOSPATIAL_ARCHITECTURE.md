# LAT-CES — Visualization, Geospatial Orientation and External-Process Architecture

**Document:** `LATCES_VISUALIZATION_GEOSPATIAL_ARCHITECTURE.md`  
**Status:** NORMATIVE — implementation boundary  
**Scope:** GUI, visualization adapters, geospatial orientation, external visualization processes  
**Authority:** LAT-CES engineering architecture / scientific-contract boundary

---

## 1. Purpose

This document defines the implementation boundary for the next LAT-CES visualization and geospatial phase.

It is normative for the work that follows. Implementation must not silently depart from these rules. If a future requirement conflicts with this document, the conflict must be identified explicitly and the document revised before implementation proceeds.

The central rule is:

> **LAT-CES owns the authoritative engineering model and the information it exports. External software consumes prepared scenes but does not become an authority over LAT-CES reality, geometry, physics, evidence, or engineering decisions.**

---

## 2. Scientific and engineering principles

### 2.1 Reality has priority

The real site, measured geometry, verified geodetic evidence, physical observations and independently supported data have priority over any model, visualization or reconstruction.

### 2.2 Evidence is not assumption

The following states remain distinct:

- `DECLARED`
- `VERIFIED`
- `MEASURED`
- `UNKNOWN`

A value must not be promoted from `UNKNOWN` to `VERIFIED` merely because a visualization, map, address service, renderer or mathematical transformation produces a plausible value.

### 2.3 Provenance remains explicit

Engineering values must retain their provenance, including where applicable:

- `MJERENO`
- `IZRAČUNATO`
- `SIMULIRANO`
- `AI PRONAĐENO`
- `PRETPOSTAVLJENO`

Visualization never changes provenance.

### 2.4 AI does not decide

LAT-CES may analyse, compare and recommend. The human remains responsible for engineering decisions:

> **LAT daje preporuke. Čovjek donosi odluke.**

This applies especially to building orientation, window area, daylight objectives, solar exposure and site placement.

---

## 3. Location is an engineering input

A building cannot be treated as an isolated abstract object when the engineering question depends on its physical environment.

The site/location provides context for, among other things:

- geographic position;
- orientation and north reference;
- terrain and elevation;
- solar position and daylight analysis;
- meteorological conditions;
- snow loading;
- wind loading;
- rain and environmental exposure;
- ventilation intake/exhaust context;
- thermal and acoustic environmental inputs.

Meteorological information is therefore not merely a map overlay. Where relevant and adequately evidenced, it becomes an engineering input to the appropriate analysis domains, including structural and environmental calculations.

---

## 4. North orientation is mandatory for geospatially meaningful building analysis

A geodetic/site representation must have an explicit orientation reference before LAT-CES can claim that building geometry is correctly oriented in the real world.

The purpose is not to impose a universal rule that a building must face a particular direction. Instead, LAT-CES must know the relationship between:

```text
geodetic reference
      ↓
north direction
      ↓
site orientation
      ↓
building orientation
      ↓
facade orientation
      ↓
window/opening orientation
```

This relationship is required for later analysis of:

- daylight;
- solar exposure;
- solar heat gains;
- window orientation;
- human daylight requirements;
- thermal consequences of orientation;
- environmental context.

LAT-CES may produce an engineering recommendation concerning orientation or opening configuration. It must not automatically make the final placement decision for the human.

---

## 5. Current geodetic evidence boundary

The current DXF evidence establishes:

```text
real geometry                         = VERIFIED
geodetic character of the drawing     = VERIFIED
official cadastral parcel identity    = UNKNOWN
CRS                                   = UNKNOWN
```

Therefore, until independent official evidence establishes the missing facts:

- do not invent a cadastral parcel identifier;
- do not assign an unverified CRS;
- do not claim official survey coordinates;
- do not create a falsely authoritative `CadastralParcel`;
- do not create a falsely authoritative `GeodeticSite`;
- do not assign building placement to an assumed official coordinate system.

A neutral mathematical transformation may exist as an adapter, but its reference/CRS status must remain explicit and `UNKNOWN` until independently verified.

### Evidence rule

```text
UNKNOWN
   │
   │ independent qualifying evidence
   ▼
VERIFIED
```

Plausibility is not verification.

---

## 6. Canonical information flow

The canonical flow is:

```text
REAL SITE / VERIFIED EVIDENCE
             │
             ▼
      CANONICAL MODEL
       BuildingModel
             │
             ▼
BuildingVisualizationAdapter
             │
             ▼
          scene.v1
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
    SCENE 1     SCENE 2
      2D           3D
       │           │
       │           ▼
       │      neutral export
       │           │
       │           ▼
       │      external process
       │           │
       │           ▼
       │        Blender
       │
       ▼
 PyQt / PyQtGraph
```

There is exactly one authoritative geometry source: `BuildingModel`.

There must not be a second independently editable geometry model hidden inside a renderer, GUI canvas or external process.

---

## 7. Scene 1 — native 2D visualization

Scene 1 is the native 2D visualization inside the Python application.

The intended rendering technology is:

- PyQt;
- PyQtGraph where appropriate for high-performance 2D line/scene rendering.

Scene 1 consumes the prepared visualization scene. It does not redefine engineering geometry.

Its responsibilities are limited to presentation, navigation and visualization of the supplied scene.

Scene 1 must not:

- modify `BuildingModel` geometry directly;
- calculate authoritative engineering physics;
- determine CRS;
- invent geodetic coordinates;
- become a second source of truth;
- silently correct source geometry.

If a geometric correction is required, it belongs at the authoritative model/adapter boundary and must be traceable.

---

## 8. Scene 2 — external 3D process

Scene 2 uses an external 3D program as an independent process.

For the current implementation, that external program is **Blender**.

Blender is not being removed. It is deliberately kept outside the LAT-CES application and Scientific Core.

The relationship is:

```text
LAT-CES
   │
   │ prepared neutral scene/export
   ▼
Blender process
   │
   ▼
3D visualization / rendering result
```

The information flow is intentionally one-directional from LAT-CES toward the external visualization process.

Blender does not become the authoritative source of:

- building geometry;
- engineering quantities;
- material properties;
- physical laws;
- engineering confidence;
- evidence status;
- geodetic identity;
- CRS identity;
- engineering decisions.

Blender is a consumer of a LAT-CES-prepared scene.

---

## 9. External-process boundary

The adapter is the architectural boundary between LAT-CES and Blender.

The preferred model is:

```text
LAT-CES BuildingModel
        │
        ▼
visualization adapter
        │
        ▼
neutral scene / export
        │
        ▼
external Blender process
```

LAT-CES must not embed Blender's implementation into the Scientific Core.

LAT-CES must not make Blender a runtime authority.

LAT-CES must not require Blender for scientific calculations.

The GUI may use Blender when available for Scene 2, but the absence or failure of Blender must be represented as an external-process availability/result state, not as a corruption of the Scientific Core.

The application must therefore preserve architectural separation even when the Scene 2 window/process is unavailable.

---

## 10. Adapter contract

The visualization adapter is responsible for transforming authoritative model information into a renderer-neutral representation.

Conceptually:

```text
BuildingModel
     │
     ▼
BuildingVisualizationAdapter
     │
     ▼
scene.v1
```

The adapter must preserve:

- object identity;
- dimensions;
- levels;
- walls;
- openings;
- placements available in the authoritative model;
- relevant evidence/provenance metadata where defined by the scene contract.

The adapter must not silently invent physical properties that do not exist in the authoritative model.

---

## 11. GUI controller boundary

A future GUI controller may orchestrate presentation, but it is not an engineering authority.

Its responsibilities may include:

- receiving user presentation actions;
- requesting a fresh visualization snapshot;
- dispatching the same `scene.v1` snapshot to Scene 1 and Scene 2;
- starting/stopping or monitoring an external visualization process;
- reporting process availability/results to the GUI.

It must not:

- become a second BuildingModel;
- modify authoritative engineering geometry behind the model's API;
- calculate engineering truth merely for display;
- decide the CRS;
- decide the cadastral identity;
- make engineering decisions on behalf of the user.

The correct dependency direction is:

```text
GUI/controller
      ↓
application/model interfaces
      ↓
BuildingModel
      ↓
visualization adapter
      ↓
scene.v1
```

not:

```text
GUI
  ↓
independent geometry
  ↓
Scientific Core
```

---

## 12. One snapshot — multiple consumers

Scene 1 and Scene 2 must consume the same authoritative visualization snapshot for a given update.

Required invariant:

> **One BuildingModel state produces one `scene.v1` snapshot. All visualization consumers receive that same snapshot.**

Example:

```text
wall length = 4.00 m
        │
        ▼
    scene.v1 #A
      /     \
     /       \
    ▼         ▼
 Scene 1    Scene 2
   2D       Blender
```

After an authoritative change:

```text
wall length = 5.00 m
        │
        ▼
    scene.v1 #B
      /     \
     /       \
    ▼         ▼
 Scene 1    Scene 2
```

The test suite must demonstrate that both consumers receive the new snapshot rather than independently reconstructing the geometry.

---

## 13. GeoMapper boundary

A neutral `GeoMapper` may be introduced for mathematical transformation between local model coordinates and an explicitly declared global/reference frame.

The mathematical form may be:

```text
[Xg]   [X0]   [ cos(theta)  -sin(theta) ] [Xl]
[Yg] = [Y0] + [ sin(theta)   cos(theta) ] [Yl]
```

where:

- `Xl, Yl` are local BuildingModel coordinates;
- `X0, Y0` are explicitly supplied reference coordinates;
- `theta` is an explicitly supplied rotation;
- `Xg, Yg` are transformed coordinates.

This mathematical adapter does not itself prove that the reference coordinates are official geodetic coordinates.

Therefore every geospatial transform must retain explicit metadata describing the evidence state of its reference frame.

---

## 14. Maps and external geographic services

OpenStreetMap, Nominatim and similar services may be used later as contextual geographic services where their terms and technical constraints permit.

They must not be silently treated as:

- official cadastral evidence;
- official survey evidence;
- proof of parcel identity;
- proof of CRS;
- proof of legal property boundaries.

A contextual map and an authoritative geodetic source are different evidence classes.

If a map is displayed, its role must remain identifiable.

---

## 15. Orientation, daylight and human requirements

LAT-CES is intended to support human-centred engineering decisions.

For building placement and openings, the eventual analysis chain may include:

```text
site
  ↓
north/orientation
  ↓
solar geometry
  ↓
facade/window orientation
  ↓
daylight / solar exposure
  ↓
thermal consequences
  ↓
engineering evaluation
  ↓
recommendation
  ↓
HUMAN DECISION
```

The phrase “quantity of light needed by a human for life” must be translated into explicit engineering criteria before it becomes a computable contract. No hidden biological threshold may be invented.

Where daylight requirements are introduced, the model must state the actual metric, unit, reference condition and evidence basis.

Likewise, window size must not be prescribed from a vague rule such as “more glass is better”. It must be evaluated against the relevant daylight, solar, thermal, energy, view, privacy and structural constraints when those domains are in scope.

---

## 16. Meteorological coupling

Once a location is independently established, meteorological data may be connected to the engineering domains that require it.

Examples include:

```text
location
   │
   ├── elevation
   ├── temperature climate
   ├── wind climate
   ├── snow climate
   ├── precipitation
   └── solar conditions
          │
          ▼
   domain-specific inputs
          │
      ┌───┼────┐
      ▼   ▼    ▼
   statics thermal ventilation
```

Each external dataset must retain source, timestamp/version where relevant, spatial applicability, units and evidence/provenance state.

Meteorological data must not be silently substituted across locations merely because they are geographically nearby.

---

## 17. Blender validation role

Blender may be used as an external visualization consumer and as a verification aid for the visualization pipeline.

A Blender result can demonstrate, for example:

- that exported geometry is reconstructable;
- that object identity is preserved;
- that dimensions are represented within explicitly measured rendering tolerance;
- that the external-process path works.

Such a result does not promote Blender geometry into the canonical engineering model.

A Blender numerical discrepancy must be measured and classified. LAT-CES must not alter engineering tolerances merely to make a renderer appear correct.

The previously established Blender spatial-measurement POC remains experimental evidence, not a reason to move Blender into Scientific Core authority.

---

## 18. Failure and availability states

External-process failure must be explicit.

Examples:

```text
EXTERNAL_PROCESS_UNAVAILABLE
EXPORT_FAILED
PROCESS_START_FAILED
PROCESS_RUNTIME_FAILED
RESULT_UNAVAILABLE
RESULT_RECEIVED
```

These states describe the visualization/process boundary. They must not be confused with:

```text
ENGINEERING_MODEL_INVALID
PHYSICS_INVALID
EVIDENCE_INVALID
GEOMETRY_INVALID
```

A renderer failure is not automatically an engineering failure.

---

## 19. Implementation order

The implementation must proceed in the following order unless a documented evidence-based reason requires a change:

### Phase A — Architecture document

This document is committed first and becomes the normative implementation boundary.

### Phase B — Repository organization

Inspect and classify existing code before writing replacement architecture.

Identify:

- current `BuildingVisualizationAdapter`;
- existing `scene.v1` contract;
- current 2D adapter;
- current 3D adapter;
- current Tkinter/ttk GUI paths;
- existing visualization tests;
- existing Blender POC/external-process artifacts;
- duplicate or obsolete visualization paths.

No speculative rewrite is permitted during this inventory.

### Phase C — Native Scene 1

Implement the native 2D consumer around the existing canonical scene contract.

The current GUI must not be redesigned wholesale merely to introduce the visualization boundary.

### Phase D — Scene 2 external-process path

Implement the neutral export and external Blender process trigger as a separate adapter boundary.

Blender remains external.

### Phase E — Snapshot consistency tests

Prove that one authoritative model update produces one new `scene.v1` snapshot consumed by both Scene 1 and Scene 2.

### Phase F — Geospatial reference boundary

Only after the visualization boundary is stable, introduce the neutral geospatial mapping contract.

CRS and cadastral identity remain `UNKNOWN` until independently verified evidence is available.

### Phase G — Location-dependent engineering analysis

After verified site/orientation evidence exists, integrate daylight, solar and meteorological inputs according to separate scientific contracts.

---

## 20. Explicit exclusions from the immediate implementation

The following are **not** part of the immediate visualization implementation:

- changing the Scientific Core;
- replacing `BuildingModel`;
- moving Blender into the Python process;
- embedding Blender into the Scientific Core;
- making Blender authoritative;
- automatic cadastral identification;
- guessing CRS;
- treating OSM/Nominatim as cadastral proof;
- automatic building placement decisions;
- OpenFOAM integration;
- ParaView integration;
- mobile field client;
- RCI-AD changes;
- unrelated security changes;
- unrelated GUI redesign.

Each excluded item requires its own evidence and architectural boundary before implementation.

---

## 21. Required tests

At minimum, the implementation must establish tests for:

1. `BuildingModel → scene.v1` produces the expected authoritative geometry.
2. A wall/opening dimension change produces a new scene snapshot.
3. Scene 1 consumes the snapshot without creating an independent geometry authority.
4. Scene 2 receives the same snapshot/export content.
5. External Blender absence/failure is represented as an external-process state.
6. No CRS is inferred from visualization data.
7. No cadastral identity is inferred from visualization data.
8. Renderer numerical differences are measured rather than hidden by arbitrary tolerance increases.
9. Evidence/provenance state is not silently upgraded by visualization.
10. The human remains the decision authority for orientation/design recommendations.

---

## 22. Non-negotiable invariants

### V1 — Canonical geometry

`BuildingModel` is the authoritative engineering geometry source.

### V2 — Single snapshot

A model state produces one canonical `scene.v1` visualization snapshot.

### V3 — Consumer separation

2D and 3D renderers consume the snapshot; they do not become alternate sources of truth.

### V4 — Blender independence

Blender remains an external FOSS process and is not part of Scientific Core authority.

### V5 — One-way external flow

LAT-CES exports information to Blender. Blender does not write engineering truth back into LAT-CES.

### V6 — Evidence integrity

Unknown geodetic facts remain `UNKNOWN` until independently verified.

### V7 — North/reference integrity

Real-world orientation analysis requires an explicit and evidenced reference direction.

### V8 — Human responsibility

LAT-CES recommendations do not replace human engineering decisions.

### V9 — Location integrity

Meteorological and geographic inputs must correspond to an explicitly identified spatial context and retain provenance.

### V10 — No renderer-driven physics

Visualization software cannot define or modify engineering physics.

---

## 23. Definition of done for this architecture step

This architecture step is complete only when:

```text
[✓] normative architecture document committed
[ ] repository inventory completed
[ ] existing visualization paths classified
[ ] Scene 1 implementation boundary established
[ ] Scene 2 external-process boundary established
[ ] one-snapshot/multiple-consumer test exists
[ ] external-process failure state tested
[ ] no CRS/cadastral assumptions introduced
[ ] verification pipeline GREEN
[ ] installer acceptance GREEN where applicable
```

Only after this gate is green should the next implementation stage be merged.

---

## 24. Final architectural statement

LAT-CES is the authority for the engineering model and engineering meaning.

PyQt/PyQtGraph is a native presentation mechanism for Scene 1.

Blender is an independent external FOSS consumer for Scene 2.

Adapters define the boundaries.

The geodetic reference provides orientation and location context when independently evidenced.

Meteorology provides location-dependent environmental inputs when appropriately sourced.

LAT-CES analyses consequences and may recommend.

**The human decides.**

> **REALITY → EVIDENCE → CANONICAL MODEL → ANALYSIS → RECOMMENDATION → HUMAN DECISION**

No implementation may reverse this order.
