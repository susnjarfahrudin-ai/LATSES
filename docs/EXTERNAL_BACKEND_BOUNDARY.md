# LATSES External Backend Boundary

## Purpose

Define the architectural boundary between LATSES and third-party engineering/visualization programs.

## Canonical rule

LATSES owns the canonical building model, engineering semantics, validation state, provenance, and engineering responsibility.

Third-party programs are external processors or viewers. They are not authoritative sources of LATSES engineering truth.

## Architecture

```text
CANONICAL BUILDING MODEL
        |
        v
ENGINEERING CORE
        |
        v
VALIDATED ENGINEERING RESULT
        |
        v
NEUTRAL EXTERNAL-BACKEND PACKAGE
        |
        +---- OpenFOAM  -> CFD
        +---- ParaView  -> scientific visualization
        +---- Blender   -> rendering / animation
```

## Boundary requirements

1. The boundary uses neutral data/files and, where required, an external-process interface.
2. LATSES must not require a third-party backend for construction or validity of the canonical building model.
3. A backend must not mutate the canonical model through the boundary.
4. Backend output is external evidence/data, not automatically a validated LATSES engineering result.
5. Every exchanged package must carry sufficient identity and revision information for traceability.
6. Units and coordinate-system semantics must be explicit; they must never be inferred silently.
7. Provenance of exported and imported data must remain explicit.
8. Missing, unknown, or invalid data must remain missing/unknown/invalid rather than being fabricated by an adapter.
9. Backend availability is an operational concern and must not alter engineering semantics.
10. Backend-specific dependencies belong behind adapters and must not leak into the canonical model or Engineering Core.

## Result direction

```text
LATSES -> neutral package -> external backend
```

is an export/processing path.

```text
external backend -> imported external result -> validation/provenance checks -> LATSES
```

is an evidence-import path. It is not a trust shortcut.

## Explicit non-goals

This contract does not install, invoke, or depend on OpenFOAM, ParaView, Blender, or any other third-party program. Concrete adapters are separate implementation steps.
