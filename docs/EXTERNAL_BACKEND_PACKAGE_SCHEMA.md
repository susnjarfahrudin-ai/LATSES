# LATSES Neutral External Backend Package

## Status

Initial boundary schema. This is a transport contract, not an engineering solver contract.

## Required envelope

```json
{
  "schema": "latces.external_backend.package",
  "schema_version": "1.0",
  "package_id": "<stable package identity>",
  "model_id": "<canonical model identity>",
  "model_revision": "<canonical model revision>",
  "created_at": "<explicit timestamp>",
  "units": {
    "length": "<explicit unit>",
    "mass": "<explicit unit>",
    "time": "<explicit unit>"
  },
  "coordinate_system": {
    "name": "<explicit coordinate system>",
    "handedness": "<explicit handedness>"
  },
  "provenance": {
    "source": "LATSES",
    "source_kind": "CANONICAL_BUILDING_MODEL",
    "evidence_state": "VERIFIED"
  },
  "payload": {}
}
```

## Contract rules

- `schema` and `schema_version` are mandatory and explicit.
- `package_id`, `model_id`, and `model_revision` are mandatory for identity and traceability.
- Units and coordinate-system semantics are mandatory; adapters must not infer them.
- `provenance` is mandatory.
- `payload` is backend-neutral. Backend-specific fields belong in a separate adapter representation.
- The package is a snapshot/export representation. It does not grant write access to the canonical model.
- An imported external result must not be promoted to a LATSES engineering result without validation and provenance checks.
- Unknown values remain unknown; no adapter may silently substitute defaults.

## Minimal payload rule

The first implementation should carry only data required to establish the boundary. Geometry, materials, thermal fields, CFD boundary conditions, and rendering metadata are added only when their scientific contracts are independently defined.
