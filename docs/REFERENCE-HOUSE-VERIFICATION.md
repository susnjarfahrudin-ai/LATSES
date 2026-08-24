# Reference House verification coverage

The Reference House is the demonstration and regression project for the complete LAT-CES workflow.

| Layer | Demonstration coverage |
|---|---|
| Basic Model | storeys, dimensions, rooms, walls, openings, orientation, volume |
| Roof | roof type, support, structure, substructure, covering, insulation, pitch |
| Statics | materials, masses, loads, structural members, foundations |
| MEP | water supply/drainage, electrical, heating/cooling, ventilation |
| Acoustics | flow velocity, pressure/noise-related engineering inputs |
| Illustration | floor plans, sections, exterior/interior 3D and system overlays |
| Simulation | airflow, heating, electrical/water network and daylight inputs |
| Measurement | measured-vs-predicted comparison and provenance |

The fixture is a single building identity. Downstream models must consume the canonical upstream representation rather than recreating geometry independently.

## Acceptance gate

A Reference House verification run is green only when:

- the fixture loads successfully;
- model identity is preserved across layers;
- geometry and storey relationships remain consistent;
- quantities retain canonical units and provenance;
- roof/material choices propagate into structural inputs;
- structural outputs are available to MEP placement constraints;
- MEP networks retain source/target nodes and sizing inputs;
- illustration can consume the same canonical model;
- no GUI-only data is required to make the engineering model valid.

The fixture is a software verification instrument, not an engineering certification of a real building.
