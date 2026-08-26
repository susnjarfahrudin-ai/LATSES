# LAT-CES Room Heat-Loss Layer — Reference Definition

## Scope

This layer calculates conductive heat loss through canonical exterior walls for each canonical Room.

## Required inputs

- canonical wall geometry
- canonical Room identity
- canonical Product/Material identity
- verified thermal conductivity `lambda`
- wall thickness
- explicit indoor design temperature
- explicit outdoor design temperature

## Current equation

`U = 1 / (R_si + thickness / lambda + R_se)`

`Q_wall = U * A_wall * DeltaT`

`q_room = Q_wall / A_room`

Surface resistances are explicit implementation constants in the reference implementation and remain change-controlled engineering assumptions.

## Deliberate limitations

This first layer does not silently calculate:

- windows/doors without verified `Uw/Ud`
- floor losses
- roof losses
- thermal bridges
- ventilation/infiltration losses
- solar gains
- internal gains
- transient dynamics

Missing required inputs produce `INPUT_REQUIRED` rather than invented results.

## Architectural rule

The thermal layer is a read-only projection of the canonical `BuildingModel`; it does not own a second Room, Wall, Material or Product model.
