# LAT-ROM-SMC-001 — SMC-ROM Constitutional Boundary & Replacement Contract

**Status:** Proposed  
**Revision:** Rev A  
**System:** LAT  
**Subsystem:** LAT-ROM / SMC

## 1. Purpose

This contract defines the constitutional boundary between LAT-ROM, SMC-ROM, and individual SMC scientific models.

SMC-ROM is the operational selector and coordinator. It is not a source of constitutional truth, does not redefine scientific truth, and does not replace human decision authority.

## 2. Constitutional hierarchy

```text
LAT Constitution
      |
      v
   LAT-ROM
      |
      v
   SMC-ROM
      |
      v
SMC scientific models
```

The dependency direction is one-way: constitution -> contract -> implementation. Implementation must not redefine constitutional authority.

## 3. Information isolation

### Individual SMC model

An individual model receives only permitted execution context and returns only contractually permitted results. It does not need to know the existence or implementation of LAT-ROM or SMC-ROM.

### SMC-ROM

SMC-ROM selects and coordinates models through neutral contracts. It does not inspect private LAT-ROM decisions and may not bypass LAT-ROM authority.

### LAT-ROM

LAT-ROM supervises SMC-ROM through independently preserved evidence. LAT-ROM may determine whether SMC-ROM violated its contract and may authorize replacement. LAT-ROM private decisions remain private.

## 4. SMC-ROM responsibilities

SMC-ROM may:

1. select applicable models;
2. reject models that fail applicability or contract requirements;
3. remove models from active execution;
4. replace permitted models;
5. maintain bounded operational state;
6. preserve decision provenance;
7. reconstruct permitted operational state after restart;
8. initiate controlled takeover through a neutral signal when active execution is degraded or unavailable;
9. support recovery of an inactive role from the last verified checkpoint.

SMC-ROM shall not:

- redefine scientific truth;
- modify LAT constitutional axioms;
- erase historical evidence;
- silently expand its authority;
- bypass the human decision-maker;
- require an individual model to know the identity or implementation of a peer model.

## 5. Model lifecycle

Operational lifecycle states may include:

```text
CANDIDATE -> ACTIVE -> BENCHED -> RETIRED
                     \-> INVALID
                     \-> SUPERSEDED
```

These states describe operational applicability and lifecycle only. They do not establish scientific truth.

## 6. Recovery and replacement boundary

Replacement and recovery are distinct operations.

```text
ACTIVE role failure
      |
      v
TAKEOVER
      |
      v
STANDBY
      |
      v
ACTIVE replacement

failed role
      |
      v
RECOVERING
      |
      v
CHECKPOINT_VERIFIED
      |
      v
READY
```

The replacement role becomes active without receiving the failed role's private implementation state. The failed role may recover independently from the last verified checkpoint while the replacement continues operating.

## 7. Neutral ROM coordinator boundary

The current implementation contract exposes `ROMCoordinator` as a read-only, immutable coordinator record. It contains only:

- current active role;
- last verified recovery checkpoint;
- neutral health input;
- role-local takeover output.

It shall not contain a `BuildingModel`, `peer_model`, implementation reference, or mutable execution state.

Its output is a `TakeoverSignal` containing only the recipient role, failure/degradation cause, verified checkpoint, and provenance.

## 8. Provenance and history

Every significant selection, rejection, replacement, retirement, supersession, or recovery decision must remain reconstructable from independent evidence. Operational cleanup may bound active state but shall not delete historical records.

A later decision supersedes or corrects an earlier decision; it does not rewrite the historical record.

## 9. Bounded operational bench

The SMC-ROM operational bench is bounded. The constitutional capacity is:

```text
BENCH_CAPACITY = 10
```

The operational eviction policy is FIFO. Eviction affects operational state only; historical evidence remains preserved.

## 10. Human decision principle

LAT provides analysis, evidence, applicability, confidence, disagreement, alternatives, warnings, and provenance. The human remains responsible for the final decision.

## 11. Current `role_handover` mapping

The existing implementation is classified against this contract as follows.

| Existing element | Classification | Constitutional interpretation |
|---|---|---|
| `ExecutionRole` | KEEP | Neutral operational role vocabulary. |
| `HealthState` | KEEP | Neutral trigger evidence for controlled takeover. |
| `RoleHealth` | KEEP | Immutable health evidence. |
| `RecoveryCheckpoint` | KEEP | Immutable last-verified recovery anchor. |
| `HandoverRequest` | KEEP | Coordinator-side transfer request; implementation-neutral. |
| `HandoverDecision` | KEEP | Immutable acceptance record with revision identity preservation. |
| `TakeoverSignal` | KEEP | Role-local signal with no peer-model identity. |
| `RecoveryStateMachine` | ADAPT | Retain as implementation of the lifecycle contract, but make SMC-ROM the formal owner of selection/lifecycle semantics. |
| `ROMCoordinator` | ADAPT | Retain as read-only/immutable coordination mechanism; it must remain model-free and must not become a scientific or constitutional authority. |
| hard-coded `_other_role()` pairing | REJECT | Final SMC architecture must select candidates through neutral applicability/contract evidence, not a fixed peer identity. |
| direct model references | REJECT | Forbidden by the information-isolation boundary. |
| automatic leader election | REJECT | Leadership/activation must remain an explicit contract decision, not emergent from model internals. |
| history deletion during recovery/eviction | REJECT | Operational cleanup must never erase provenance or evidence. |

## 12. Architectural invariants

The following must remain true:

```text
LAT-ROM
   |
   | supervises
   v
SMC-ROM
   |
   | selects
   v
SMC models
```

and:

```text
SMC model  X  bypasses SMC-ROM
SMC-ROM     X  bypasses LAT-ROM
SMC model  X  identifies or depends on peer model implementation
```

## 13. Acceptance criteria for subsequent implementation work

A change is constitutionally acceptable only when:

1. model implementations remain isolated;
2. operational authority remains inside the defined SMC-ROM boundary;
3. recovery can return an inactive role to a verified checkpoint without making it active automatically;
4. replacement can occur without deleting history;
5. operational state remains bounded;
6. provenance remains reconstructable;
7. human decision authority is preserved.

## 14. Status

This document is the formal contract boundary for subsequent SMC implementation work. It does not itself execute selection, recovery, or scientific analysis.
