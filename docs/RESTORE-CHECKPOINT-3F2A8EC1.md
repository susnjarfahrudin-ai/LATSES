# LAT-CES Recovery / Foundation Checkpoint

## Frozen release foundation

- `main` merge commit: `3f2a8ec15d2ea3f7fcf9a89eb53c0ca9a0ab0671`
- Source PR: #165 — canonical Reference House → BuildingModel boundary
- GUI foundation: `gui_complete.py` restored from known-good `280832b6`
- Manual validation: installed artifact from PR #162 confirmed functional legacy interface

## Canonical layers present at this checkpoint

- SCI 1–145 contract layer
- Scientific ontology / reasoning / synthesis / governance / trust / lifecycle
- Dimensionless correlations: Reynolds, Mach, Prandtl, Nusselt, Biot, Fourier
- Physical constants canonical registry
- BuildingModel canonical boundary
- Reference House deterministic fixture
- Existing functional GUI foundation

## Rules for continuation

1. Do not modify the GUI foundation in this phase.
2. New Reference House geometry must use explicit source data only.
3. No inferred room dimensions, wall lines, or openings may be invented from area alone.
4. Every geometry change must retain the deterministic Reference House metric tests.
5. Every accepted integration change must pass Verification, Installer, and CodeQL before merge.

## Next phase

Promote Reference House from a metrics fixture to a geometry-bearing canonical BuildingModel source by adding explicit room geometry, wall topology, and openings only where the source contract provides sufficient data.
