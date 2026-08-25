# LAT-CES GUI — Physics View Contract

## Purpose

The GUI is a presentation layer over the canonical `BuildingModel` and SCI/domain results. It must never invent physical fields, duplicate solver logic, or maintain a second physical model.

## Canonical chain

```text
BuildingModel
    ↓
canonical domain/scientific calculation
    ↓
validated/calculated result
    ↓
GUI presentation adapter
    ↓
Canvas overlay + numeric inspector
```

## Existing reusable physics sources

| Physical domain | Existing canonical source | GUI representation |
|---|---|---|
| Airflow flow/velocity | `building.mep_engineering` ventilation result | arrows/vectors + Q/v values |
| Pressure / pressure loss | `scientific.pressure_drop.PressureDropModel` | Δp field + numeric value |
| Reynolds / friction | `scientific.duct_friction.DuctFrictionModel` | regime/result inspector |
| Water velocity/drop | `building.mep_engineering` water result | vectors + Δp |
| Heating | `building.mep_engineering` heating result | heat-load + temperature layer when field exists |
| Building engineering aggregate | `building.engineering_report` | compact status card |
| Measurement | SCI measurement/provenance layer | measured marker with provenance |

## Result semantics

Every rendered quantity should preserve:

- value
- unit/dimension
- status (`CALCULATED`, `INPUT_REQUIRED`, `INPUT_CONFLICT`, etc.)
- provenance/evidence where available
- uncertainty where the canonical quantity carries it.

The GUI must distinguish calculated/simulated values from measured values.

## Initial airflow visualization contract

The first physical overlay should support:

```text
Q [m³/h]
v [m/s]
Δp [Pa]
```

with a future path to:

```text
streamlines
velocity field
pressure field
temperature/humidity
acoustic result
measured-vs-model residual
```

The GUI must not animate air unless a spatial result field exists. A single opening-level result may be shown as a numeric/vector indicator, but must not be represented as a false CFD field.

## Initial thermal visualization contract

Heating/cooling should first expose the canonical aggregate loads and design inputs. Spatial temperature/heat-flux fields become eligible only when an authoritative spatial calculation exists.

## Measurement overlay

Measured points must carry at least:

- timestamp
- sensor/measurement identity when available
- value + unit
- provenance/evidence status
- comparison to calculated value when a corresponding model quantity exists.

## UI rule

Physics results appear in the same PLAN / SECTION / 3D model views. They do not create separate parallel models.
