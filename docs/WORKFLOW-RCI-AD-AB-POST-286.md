# LAT-CES Security Workflow — Post-PR #286

Status: POST-MERGE BASELINE / REMINDER

Reference main commit: `d231480720de58a135e7970b1d11fef550d97d80`
Merged PR: #286 — `INTEGRATE: RCI-AD ↔ AdaptiveDefense ↔ A/B canonical contract`
Verification: #1604 — GREEN

## 1. Purpose

This document records the accepted security/evidence workflow after PR #286 so the project does not lose the architectural direction during subsequent work.

The installed Windows build from the post-#286 installer run is a runtime reference point for interface observation. The current interface is known to need further work; that work is treated separately from the security/evidence architecture.

## 2. Canonical direction

```text
UNTRUSTED INPUT
      |
      v
CYBERFORTRESS
security boundary
      |
      +--> FLOWGUARD / SECURE IPC / REPLAY PROTECTION
      |
      v
RCI-AD OBSERVATION
immutable observation / evidence plane
      |
      v
DEFENSE EVIDENCE
      |
      v
ADAPTIVEDEFENSE
quarantine + verification authority
      |
      v
VERIFIED DefenseRecord ONLY
      |
      v
A/B HANDOVER
execution/recovery redundancy
      |
      v
RECOVERY
last-known-good / verified checkpoint
      |
      v
RCI-AD OBSERVATION
      |
      +----> next cycle
```

Canonical lifecycle:

`OBSERVE -> EVIDENCE -> VERIFY -> HANDOVER -> RECOVER -> OBSERVE`

## 3. Responsibilities — do not mix them

### FlowGuard

- Mathematical limiter/control mechanism.
- Existing limiter mathematics remains unchanged by this workflow.
- Does not become an RCI-AD learning engine.

### RCI-AD

- Observation and analysis evidence plane.
- Records immutable observations.
- May bind an observation into defense evidence.
- Does not verify/promote defenses.
- Does not change FlowGuard thresholds or admission decisions.
- Does not transfer runtime or BuildingModel state.

### AdaptiveDefense

- Canonical defense-evidence authority.
- Creates `DefenseRecord`.
- Quarantines unverified evidence.
- Promotes evidence only with explicit verification SHA.
- Imports/exports only verified defense evidence across the A/B boundary.

### A/B

- Two separate OS processes: active + standby/recovery peer.
- Owns takeover and recovery execution.
- Consumes verified defense/checkpoint evidence.
- Never copies compromised peer runtime/model state.
- Does not become a second RCI-AD or AdaptiveDefense authority.

### BuildingModel

- Engineering source of truth.
- Remains outside the security/evidence/recovery state path.
- No peer runtime/model transfer through the security workflow.

## 4. Canonical integration seam

The only intended RCI-AD -> AdaptiveDefense evidence binding is:

`bind_flow_observation_to_defense(...)`

Contract:

1. One immutable `FlowObservation` produces one unverified `DefenseRecord`.
2. Observation evidence contains deterministic provenance/digest.
3. Binding does not modify the FlowGuard decision or baseline.
4. The record remains unverified until AdaptiveDefense promotion.
5. Only a verified `DefenseRecord` may cross toward A/B handover.
6. A/B remains execution/recovery authority.

## 5. A/B operational cycle

### Attack against A

```text
A ACTIVE
  -> attack / security rejection
  -> RCI-AD observes
  -> evidence -> AdaptiveDefense
  -> quarantine / verify
  -> verified DefenseRecord
  -> B takeover
  -> A recovery from verified checkpoint
  -> B ACTIVE / A READY
```

### Attack against B

```text
B ACTIVE
  -> attack / security rejection
  -> RCI-AD observes
  -> evidence -> AdaptiveDefense
  -> quarantine / verify
  -> verified DefenseRecord
  -> A takeover
  -> B recovery from verified checkpoint
  -> A ACTIVE / B READY
```

Repeat indefinitely by rotation. The peer receives verified evidence, not the compromised process state.

## 6. Verification gate

For every future security change:

```text
candidate branch
    |
    v
exact diff / scope check
    |
    v
Verification
    |
    +-- RED --> first concrete failure only
    |             -> minimal fix
    |             -> same Verification again
    |
    +-- GREEN --> continue
                    |
                    v
                  Installer
                    |
                    v
             GUI/acceptance as applicable
```

Do not stack fixes on a red verification.

Do not declare GREEN from an old run. The evidence must correspond to the commit being accepted.

## 7. Post-#286 evidence baseline

- `main` merge commit: `d231480720de58a135e7970b1d11fef550d97d80`
- Post-merge Verification: #1604 / run `34069896065`
- Verification result: SUCCESS / GREEN
- SCI 1–145 structural acceptance: GREEN
- Package/wheel discovery: GREEN
- Verification tests 0001–0009: GREEN
- Installer #1383: installed locally as the current runtime/interface reference reported by the project owner.

The local installation is a useful runtime observation point, but it is not by itself a substitute for CI evidence.

## 8. Interface work

The installed interface is currently known to require improvement. Interface/GUI corrections are a separate workstream.

Rules:

- Do not use GUI imperfections as justification to alter the security architecture.
- Do not change FlowGuard mathematics while correcting interface behavior.
- Do not add a second state/defense/evidence authority to solve a GUI issue.
- Preserve the canonical BuildingModel and existing GUI acceptance path.

## 9. Forbidden architectural drift

Do not introduce any of the following without a separate architectural decision:

- a second limiter;
- a parallel AdaptiveDefense authority;
- a second A/B coordinator/handover mechanism;
- RCI-AD authority to verify or promote defenses;
- copying peer runtime state;
- copying compromised BuildingModel/security state;
- a security-side duplicate of the engineering source of truth.

Any proposed change must extend:

`OBSERVE -> EVIDENCE -> VERIFY -> HANDOVER -> RECOVER -> OBSERVE`

rather than creating a parallel chain.

## 10. Next work gate

Before the next architectural expansion:

1. Keep `main` at the verified post-#286 baseline.
2. Treat the local #1383 installation as the interface/runtime reference.
3. Separate GUI/interface cleanup from the security contract.
4. Design the next adversarial RCI-AD/A/B test against this exact baseline.
5. Run Verification first.
6. If GREEN, run the corresponding Windows Installer/acceptance gate.
7. Only then merge the next narrow change.
