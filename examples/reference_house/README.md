# LAT-CES Reference House

The Reference House is the canonical demonstration fixture for LAT-CES.

It is not a second engineering model. It is a deterministic project instance that exercises the canonical Building Model and its downstream models.

## Purpose

The fixture demonstrates, end-to-end, that one building definition can feed:

1. Basic Model — geometry, storeys, rooms, walls and openings.
2. Roof — dimensions, support, structure, substructure, covering, insulation and pitch.
3. Statics — material/mass handoff, loads and structural calculation inputs.
4. MEP — water, drainage, electrical, heating/cooling and ventilation networks.
5. Acoustics/fluid checks — flow, velocity, pressure-loss and noise-related inputs.
6. Illustration — 2D/3D views and system overlays.
7. Simulation/measurement — predicted versus measured values when sensor data is available.

## Rules

- Keep the fixture deterministic and versioned.
- Every engineering quantity must retain unit, source/provenance and uncertainty where applicable.
- Do not silently replace calculated values with presentation-only values.
- Changes to the fixture require regression tests when they alter canonical model behaviour.

## Verification role

CI should load this fixture as a smoke/regression project. The expected result is not a construction approval; it is proof that the LAT-CES model pipeline can ingest one complete building and propagate its data through the supported model layers without losing identity, geometry, units, provenance or dependencies.
