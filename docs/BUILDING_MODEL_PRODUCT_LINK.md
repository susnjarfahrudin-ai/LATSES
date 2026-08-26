# Building Model ↔ Product/Material foundation

The Building Model remains the authoritative physical model. Product and material records are referenced by identity; scientific modules consume the resolved technical properties.

## First-class relationships

- `Room`: id, name, plan dimensions, level-derived height, optional suspended ceiling.
- `Wall`: exterior/interior, load-bearing/partition, openings, material/product identity.
- `Material`: density, thermal conductivity, compressive strength, product identity and manufacturer.
- `Stair`: plan dimensions plus riser count/height, tread width, landing, railing and floor opening.
- `Terrace`: plan dimensions and construction type/material.
- `BuildingModel.load_bearing_mode`: `all_walls` or `exterior_only`.

## Data flow

`Reference House → Level → Room/Wall/Stair/Terrace → Product/Material → Standards → scientific modules`

The current implementation deliberately does not calculate structural or thermal results. Those modules consume this model in later, separately validated steps.
