# LAT-CES Model Architecture v2

## Purpose

This document records the new product/model concept supplied for the next LAT-CES phase. It is the architectural contract for implementation; it does not itself certify structural design or replace applicable standards, manufacturer data, measurements, or engineering review.

## Core principle

The **Basic Model is the geometric and spatial source of truth**. It owns the building envelope geometry, levels, rooms, walls, openings, roof geometry/type, orientations and service nodes. Downstream models consume that model and add domain-specific attributes without silently replacing the geometry.

```text
BASIC MODEL
  geometry + levels + rooms + walls + openings + roof + orientations + service nodes
                    |
                    +--------------------+
                    |                    |
                 STATICS                 MEP
                    |                    |
             mass/materials        water/drainage
             structural loads      electrical
             foundations           heating/cooling
             members               ventilation
             construction          acoustics/flow
                    |                    |
                    +---------+----------+
                              |
                         ILLUSTRATION
                    2D / section / 3D / flows
                              |
                         SIMULATION
                    prediction ↔ measurement
```

## User-facing first tab: MODEL / PREGLED

The first tab is a compact model-builder. The upper visual area continuously shows the current object; the lower area contains the active editor. Selection should progressively build the same canonical model rather than create separate GUI state.

### Building stack

- Roof
- Floor / storey +
- Ground floor
- Basement / cellar
- Foundation / slab

The stack is ordered vertically and remains visible while editing another level.

## Roof editor contract

Selecting Roof exposes:

1. Plan dimensions: length, width and computed plan area.
2. Roof shape: flat, monopitch, hidden monopitch, gable, hip, modified/composite, dome and future catalogued types.
3. Roof support: RC slab, masonry with ring beam, timber, steel, concrete elements.
4. Roof structure: timber beams, steel profiles, concrete elements, RC sloped slab.
5. Substructure: battens; counter-battens + battens; boarded + counter-battens + battens.
6. Cover catalog: tile, sheet metal, concrete tile, sandwich panel, shingle, timber and future products.
7. Insulation: type, thickness and finish.
8. Orientation relative to support / cardinal direction.
9. Pitch: manufacturer recommendation may populate the proposal, but an explicit user pitch remains distinct from the recommendation.
10. Overhangs, future roof additions, dormers/roof openings, parapets and terraces are modeled as explicit geometry operations.

Manufacturer-derived pitch, mass and product data must carry provenance. A catalog recommendation is **not** treated as a structural approval.

## Storey editor contract

Every storey has:

- plan length, width and net height;
- external wall construction;
- partition construction;
- room graph and room names;
- wall lines with explicit dimensions;
- doors/windows with dimensions, sill heights and material;
- floor build-up and finish metadata;
- internal wall finish metadata;
- window/door material selection;
- lighting/opening analysis inputs;
- service-node locations such as boiler room, main water/electrical connection and system hubs.

Room creation is geometry-first: wall lines must be dimensioned and produce closed regions. A room name is assigned to the resulting closed region rather than being a free-floating label.

## Spatial intelligence

The Basic Model owns:

- level volume;
- room areas and volumes;
- opening geometry;
- orientation;
- adjacency and vertical alignment;
- service-node locations.

These become valid inputs to later daylight, structural, thermal, MEP and acoustic calculations. Suggestions remain suggestions and carry evidence/provenance.

## STATICS model

Statics receives a read-only handoff from the Basic Model and adds:

- actual construction/material selections;
- density and mass;
- structural member definitions;
- snow, wind, rain and imposed actions;
- applicable standard / national annex references;
- load combinations;
- structural analysis results;
- foundation / counter-slab proposal;
- beams, slabs, columns, walls and roof member sizing;
- concrete grade and reinforcement proposals;
- quantity takeoff.

The model must calculate from roof downward through all storeys to foundations. No load value is invented silently: climatic and code parameters require explicit source/provenance.

The output is a **validated engineering result**, not an unconditional construction approval.

## MEP model

MEP receives the Basic Model and selected/validated structural constraints. It adds:

- hot/cold water and drainage;
- electrical distribution and main node;
- heating and cooling;
- ventilation supply/exhaust;
- acoustic/flow constraints;
- system equipment and material choices;
- pipe/duct diameters;
- routes, lengths, elevations and junctions;
- flow velocity, pressure loss, heat output and other domain results;
- optimization alternatives.

MEP must re-calculate whenever the user changes an engineering input such as pipe/duct diameter, equipment, material, emitter type or route.

## Installation constraints

The MEP editor consumes structural wall/slab thickness and clearances to determine whether proposed routes fit. Vertical risers are connected between levels through explicit system nodes. The boiler/plant room is a canonical service hub, not a hard-coded hidden assumption.

## Acoustic and fluid checks

Each applicable MEP subsystem gets a domain check for:

- flow velocity;
- pressure loss;
- expected source/terminal noise where supported by the model;
- attenuation treatment;
- thermal/hydraulic performance;
- material/diameter alternatives.

No claim such as "20 dB" is made without a model, input assumptions and provenance supporting it.

## ILLUSTRATION model

Illustration consumes Basic + validated Statics + MEP results to render:

- floor plans;
- elevations/facades;
- longitudinal/vertical sections;
- 3D exterior;
- 3D room-by-room interior navigation;
- material and finish appearance;
- airflow/heat/water/electrical overlays;
- profile and configuration changes.

Illustration is downstream of engineering truth. It must not create a second geometry model.

## Simulation and measurement bridge

The final analysis layer compares:

```text
predicted model state
        ↕
measured sensor state
```

Measurements retain timestamp, sensor identity, units, uncertainty and provenance. Deviations can inform model calibration and optimization, but measured observations and model conclusions remain distinct.

## Implementation order

1. Canonical Basic Model contract (current tranche).
2. Roof/storey/opening/material catalogs and geometry editing.
3. Basic Model → Statics handoff.
4. Statics material/mass/load model and verification gates.
5. Basic + Statics → MEP handoff.
6. MEP water/electrical/heating/cooling/ventilation/acoustics contracts.
7. Illustration adapter over the canonical models.
8. Simulation/measurement comparison layer.
9. GUI simplification and visual workflow.
10. Verification → EXE → Installer.

## Non-negotiable architectural rules

- One physical building model; many domain views.
- No GUI-only scientific state.
- No duplicate Dimension/Quantity/Measurement semantics.
- Every derived result retains lineage and provenance.
- Manufacturer values are source data, not universal constants.
- Standards and climate actions require jurisdiction/source context.
- User overrides are explicit and auditable.
- A recommendation is never silently promoted to a validated engineering result.
