# SCI 1–145 → LAT-CES implementation map

Status: active working map, Rev A
Branch: agent/scientific-contract-sci145

## Governing rule

SCI 1–145 is treated as the architectural specification. Existing implementations are not considered verified merely because a class/module exists. A layer becomes VERIFIED only when its canonical contract, integration, regression tests, and CI evidence exist.

## Canonical scientific chain

Reality → Observation → Measurement → Quantity/Unit/Dimension → Evidence/Provenance → Validation → ScientificKnowledgeObject → Ontology → Reasoning → Synthesis → Evolution → Governance → Preservation → Integrity/Trust → Lifecycle → Ecosystem/Federation → Security.

## Current repository findings

| SCI layer | Current location | Status | Action |
|---|---|---|---|
| ScientificKnowledgeObject | `lat_ces/core/sko.py` | ADAPT | Keep as canonical compatibility root; extend through explicit contract adapters rather than creating a second SKO. |
| Dimension | `lat_ces/scientific/dimensions/dimension.py` | MERGE/KEEP | This is the canonical exponent-vector implementation. `lat_ces/core/dimensions.py` is only a compatibility facade. |
| Unit | `lat_ces/scientific/units/core.py` | KEEP/ADAPT | Canonical Unit implementation already binds to Dimension. Add package exports and verification tests. |
| Measurement | `lat_ces/scientific/measurement/` | NEW | Required by SCI-0046/0047; formal object must carry quantity, value, unit, uncertainty, instrument, calibration, timestamp and evidence. |
| Provenance | `lat_ces/scientific/measurement/provenance.py` | NEW | Required traceability layer; no measurement/derived result without source metadata. |
| Validation | `lat_ces/scientific/measurement/validation.py` | NEW | Canonical scientific validation gate for measurement contract. |
| Registry | `lat_ces/scientific/measurement/registry.py` | NEW | Initial canonical registry for measurement objects; later connect to the wider SKO registry. |
| Ontology | existing/partial scientific modules | AUDIT NEXT | SCI-0062/0063 requires entity, domain, definition, relation, graph, consistency and versioning. Do not create duplicates before import map. |
| Synthesis | existing/partial modules | AUDIT NEXT | Must preserve provenance and confidence bounds; derived models cannot become facts automatically. |
| Governance | existing/partial modules | AUDIT NEXT | Must preserve authority, approval and audit trail. |
| Trust/Integrity | existing/partial modules | AUDIT NEXT | Must be evidence-based, explainable and historical. |
| Lifecycle | existing/partial modules | AUDIT NEXT | Must implement controlled state transitions and preservation. |
| Security/Federation | documented in SCI | DEFERRED | Do not claim SCI-0133 security verification for the executable until implementation is mapped and tested. |
| BuildingModel integration | `lat_ces/building_model/*` | ADAPT | Scientific quantities/results must enter the BuildingModel through the canonical contract. |
| GUI | `lat_ces/building_engineering_workspace.py` and related | KEEP | Do not redesign GUI in this phase; consume canonical BuildingModel/scientific contracts. |
| EXE/Installer | `.github/workflows/build-exe.yml`, `.github/workflows/build-installer.yml` | KEEP/EXTEND | Add SCI contract verification as a release gate before packaging. |

## Dimension decision

`lat_ces/core/dimensions.py` imports the canonical implementation from `lat_ces.scientific.units.core`; the latter imports the canonical exponent-vector model from `lat_ces.scientific.dimensions.dimension`. Therefore the apparent duplicate Dimension system is now treated as a compatibility facade, not a second scientific implementation. Any remaining direct duplicate definitions must be removed/adapted after the repository-wide import audit.

## SCI measurement contract

SCI-0046/0047 defines Measurement as a formal traceable object containing:

- Physical Quantity
- measured value
- Unit
- uncertainty
- instrument
- calibration
- timestamp
- evidence
- persistent measurement identity

The implementation must reject a value without quantity, an incompatible unit, a missing required timestamp, and missing source/provenance information. Uncertainty may be explicitly marked unavailable only when the contract records why it is unavailable.

## Verification policy

1. Map before changing.
2. One canonical implementation per scientific concept.
3. Compatibility facades may remain temporarily, but may not define competing semantics.
4. New scientific models are added only after their prerequisite contract is verified.
5. CI verification precedes EXE/installer packaging.
6. No GUI redesign until the scientific contract is closed.
