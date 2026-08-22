# LAT-CES Building Engineering Completion Plan

Status: Active working plan

## Scope

This plan tracks the implementation path from the canonical BuildingModel to a single integrated engineering workspace and report.

## Workstreams

1. Catalog -> BuildingModel selector
2. Building Engineering shell -> CompleteBuildingWorkspaceApp
3. Quantity Take-Off -> live BuildingModel
4. Structural load path -> engineering model boundary
5. Envelope + glazing -> thermal calculations
6. Roof/timber/sheet metal/gutters/railings -> QTO
7. Electrical domain model and report integration
8. Unified Building Engineering Report

## Rules

- BuildingModel remains the single source of truth.
- Showcase/reference-house data is input data, not an engineering authority.
- GUI code does not own scientific calculations.
- Engineering outputs retain explicit input/evidence/uncertainty information.
- No duplicate domain model is introduced only to support the GUI.
- Existing scientific engines are reused through explicit adapters/services.
- Every workstream ends with regression coverage before merge.
