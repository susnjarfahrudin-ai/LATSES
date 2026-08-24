# SCI 1–145 — Ontology → Reasoning → Synthesis implementation map

Status: active working map, Rev A
Branch: agent/sci145-ontology-reasoning-synthesis

## Governing rule

SCI 1–145 is the architectural specification. Existing code is not considered verified merely because a module exists. A layer becomes VERIFIED only after its canonical contract, integration, regression tests, and CI evidence exist.

## Canonical chain

Reality → Observation → Measurement → Quantity/Unit/Dimension → Evidence/Provenance → Validation → ScientificKnowledgeObject → Ontology → Reasoning → Synthesis → Evolution → Governance → Preservation → Integrity/Trust → Lifecycle → Ecosystem/Federation → Security.

## Current tranche

| SCI layer | Existing implementation | Status | Required action |
|---|---|---|---|
| ScientificKnowledgeObject | `lat_ces/core/sko.py` | ADAPT | Keep one canonical SKO root; add explicit adapters/contracts instead of a competing object. |
| Measurement | `lat_ces/scientific/measurement/` | IMPLEMENTED | Verify integration into SKO/evidence and BuildingModel. |
| Dimension | `lat_ces/scientific/dimensions/dimension.py` | CANONICAL | Repository-wide import audit; compatibility facades must not define semantics. |
| Unit | `lat_ces/scientific/units/core.py` | CANONICAL | Verify dimensional compatibility through the public API. |
| Ontology | existing/partial scientific modules | AUDIT | Map entities, definitions, relations, graph, consistency, and versioning before adding new models. |
| Reasoning | existing/partial modules | AUDIT | Map deterministic inference, assumptions, provenance and confidence. |
| Synthesis | existing/partial modules | AUDIT | Map derived-model creation, uncertainty propagation and evidence retention. |
| Governance | existing/partial modules | NEXT | Map authority, approval, audit and conflict handling. |
| Trust/Integrity | existing/partial modules | NEXT | Map evidence-based trust, hashes/signatures and historical integrity. |
| Lifecycle | existing/partial modules | NEXT | Map controlled states, revisions, deprecation and preservation. |
| Security/Federation | documented in SCI | DEFERRED | Do not claim verification until implementation and tests exist. |
| BuildingModel | `lat_ces/building_model/*` | ADAPT | Scientific results must enter through canonical contracts, preserving units, uncertainty and provenance. |
| GUI | `lat_ces/building_engineering_workspace.py` and related | KEEP | No redesign; consume validated BuildingModel/scientific results. |
| EXE/Installer | `.github/workflows/build-exe.yml`, `.github/workflows/build-installer.yml` | KEEP/EXTEND | Scientific verification must gate packaging. |

## Ontology contract to close

An ontology object must have stable identity, entity type, domain, definition, relations, version/revision, provenance, and validation state. Relations must be explicit and machine-checkable. A graph mutation must not silently change the meaning of an existing scientific object.

## Reasoning contract to close

A reasoning result must retain: inputs, rule/model identifier, assumptions, derivation/provenance, uncertainty or confidence where applicable, validation state, and output identity. Deterministic scientific rules must remain distinguishable from heuristic/AI suggestions. A derived result must never silently become an observation or measured fact.

## Synthesis contract to close

A synthesis result combines validated inputs into a new model/result while retaining input identities, transformations, assumptions, uncertainty propagation, provenance and revision. Synthesis must not discard source evidence and must be reproducible from recorded inputs and model versions.

## Verification gate

1. No new scientific engine before prerequisite contracts are verified.
2. One canonical implementation per scientific concept.
3. Compatibility facades may remain temporarily but cannot define competing semantics.
4. Every derived scientific result carries provenance and validation state.
5. SCI verification tests must pass before EXE/installer packaging.
6. GUI remains unchanged until the scientific contract is closed.

## Planned verification matrix

- Ontology identity/version/relation consistency
- Reasoning provenance/assumption/confidence preservation
- Synthesis input lineage/uncertainty preservation
- SKO binding for ontology/reasoning/synthesis outputs
- BuildingModel acceptance/rejection of scientific results
- End-to-end scientific contract smoke test
- CI release gate before Windows EXE and installer
