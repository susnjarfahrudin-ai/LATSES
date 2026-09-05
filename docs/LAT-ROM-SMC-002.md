# LAT-ROM-SMC-002 — Neutral Takeover Selection Contract

**Status:** Proposed  
**Revision:** Rev A  
**System:** LAT  
**Subsystem:** LAT-ROM / SMC-ROM

## Purpose

Define the boundary between a neutral LAT-ROM takeover signal and SMC-ROM candidate selection.

## Contract

```text
LAT-ROM / ROM
     |
     | TakeoverSignal
     v
 SMC-ROM selector
     |
     | candidate evidence
     v
 eligible candidate -> ACTIVE
```

The signal identifies only the recipient operational role, failure/degradation cause, verified checkpoint, and provenance. It does not identify or expose the implementation of another model.

## Selection rule

SMC-ROM may activate a candidate only when its neutral evidence satisfies both:

- applicability;
- contract compliance.

Candidates for other roles are ignored. Ineligible candidates do not become active.

When no eligible candidate exists, takeover selection fails closed and emits no activation decision.

## Information isolation invariant

The selection boundary must not contain a `BuildingModel`, peer-model reference, model implementation object, or private LAT-ROM decision.

## Operational sequence

```text
active failure
    -> neutral ROM observation
    -> TakeoverSignal
    -> SMC-ROM filters candidates by recipient role
    -> applicability + contract check
    -> select eligible candidate
    -> ACTIVE
```

No scientific truth claim is made by selection. Activation is an operational lifecycle decision only.

## Recovery relationship

Takeover selection does not perform recovery of the failed role. Recovery remains a separate lifecycle operation using the last verified checkpoint. The failed role may recover in parallel while the selected candidate remains active.
