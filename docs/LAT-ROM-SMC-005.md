# LAT-ROM-SMC-005 — Evidence Consistency Contract

**Status:** Proposed  
**Revision:** Rev A  
**System:** LAT  
**Subsystem:** LAT-ROM / SMC-ROM

## Purpose

Define the neutral boundary between preserved SMC-ROM decision history and
restart reconstruction.

## Contract

```text
preserved decision history
          |
          | read-only decision IDs + versions
          v
 evidence consistency check
          |
          v
consistent neutral evidence OR BLOCKED
          |
          v
restart reconstruction
```

The consistency boundary verifies that reconstruction references preserved
history that actually exists and that the supplied model and selector versions
match the referenced decision records.

## Safety invariants

1. Decision history is read-only evidence.
2. Requested decision identifiers must be unique.
3. Every requested decision identifier must exist in preserved history.
4. `model_version` must match every referenced decision record.
5. `selector_version` must match every referenced decision record.
6. Inconsistency fails closed and produces no activation signal.
7. The boundary does not mutate `DecisionRecordStore`.
8. The boundary contains no scientific model implementation or selector state.
9. Reconstruction remains separate from candidate activation and replacement.

## Non-goals

- no selector integration;
- no candidate activation;
- no model execution;
- no scientific validation;
- no modification or deletion of decision history;
- no automatic leader election;
- no replacement of LAT-ROM supervisory authority.
