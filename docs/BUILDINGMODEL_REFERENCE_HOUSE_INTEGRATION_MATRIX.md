# BuildingModel ↔ Reference House integration matrix

Base: `main @ c10d75a572bb630ca0055937b3f02e4729623ab6`

## Canonical decisions

| Area | Current owner | Decision | Rationale |
|---|---|---|---|
| Building geometry | `lat_ces/building_model/core.py` | KEEP | Authoritative GUI-independent `BuildingModel` / `Level` / `Room` / `Wall` / `Opening`. |
| BuildingConcept | `lat_ces/building_model/concept.py` | KEEP | Richer downstream concept; must remain an adapter/view, not a second geometry truth. |
| Concept adapter | `lat_ces/building_model/concept_adapter.py` | KEEP | One-way compatibility adapter from `BuildingModel` to `BuildingConcept`. |
| Engineering integration | `lat_ces/building_model/integration.py` | KEEP / ADAPT | Already consumes one `BuildingModel`; next step is to supply canonical Reference House geometry. |
| Reference House fixture | `lat_ces/reference_house_model.json` | KEEP | Deterministic regression/source fixture; contains engineering metadata and room areas. |
| Reference House calculator | `lat_ces/reference_house.py` | KEEP / ADAPT | Useful deterministic calculations; must not become a second geometry model. |
| Reference House → BuildingModel | `lat_ces/building_model/reference_house_adapter.py` | NEW boundary | Single future construction boundary. Current strict mode rejects missing room geometry rather than inventing it. |
| GUI | `lat_ces/gui_complete.py` | KEEP | Known-good `280832b6` foundation; no GUI redesign in this integration. |
| Scientific result → BuildingModel | `lat_ces/scientific/core/building_adapter.py` | KEEP | Canonical validated/approved scientific-result boundary already exists. |
| Legacy `modules.pipeline` | `lat_ces/modules/pipeline.py` | LEGACY / AUDIT | Uses older module engines; no RETIRE until repository-wide zero-import evidence. |

## SCI requirements applied to the boundary

1. One physical building model remains the geometry source of truth.
2. Reference House remains a deterministic fixture, not a second geometry implementation.
3. Derived engineering results retain provenance and units.
4. Missing geometry is a GAP, not an invitation to synthesize dimensions.
5. GUI state is not required to make the engineering model valid.
6. The scientific-to-BuildingModel bridge accepts only validated/approved scientific artifacts.

## Current factual gap

The Reference House fixture stores level envelope dimensions and per-room area/height, but does not store room length/width or explicit wall-line geometry for all rooms. Therefore a complete `BuildingModel` room graph cannot be constructed without adding explicit source geometry.

The integration adapter intentionally exposes this gap:

- `strict_geometry=True` → fail with `ReferenceHouseGeometryError`.
- `strict_geometry=False` → map only explicit level/envelope geometry and leave room graphs empty.

This is a verification guard against silently inventing geometry.

## Next integration tranche

Add explicit room/wall/opening geometry to the Reference House source, then extend the adapter to populate canonical `Room`, `Wall`, and `Opening` objects. After that, run the complete Reference House → BuildingModel → engineering analysis → GUI regression chain.
