# RCI-AD ↔ AdaptiveDefense ↔ A/B canonical direction

Status: candidate contract; acceptance requires GREEN Verification.

## Canonical responsibility

```text
untrusted input
    -> CyberFortress security boundary
    -> FlowGuard / Secure IPC / Replay protection
    -> RCI-AD observation
    -> AdaptiveDefense evidence + quarantine + verification
    -> verified DefenseRecord only
    -> A/B handover and recovery
    -> verified checkpoint
    -> next observation
```

### RCI-AD
Observation and analysis evidence plane. It may record immutable observations, but it does not change FlowGuard thresholds, make admission decisions, verify defenses, or transfer runtime/model state.

### AdaptiveDefense
Defense-evidence authority. It creates `DefenseRecord`, quarantines unverified evidence, and is the only layer in this chain that promotes/imports verified defense evidence.

### A/B
Execution and recovery redundancy. It consumes verified defense/checkpoint evidence and controls takeover/recovery. It does not consume or copy peer runtime/model state.

## Canonical contract

`bind_flow_observation_to_defense(...)` is the single narrow seam from a `FlowObservation` to an unverified `DefenseRecord`.

Rules:

1. One immutable RCI-AD observation produces one evidence record.
2. The binding never changes the FlowGuard decision or baseline.
3. Evidence is unverified until AdaptiveDefense promotes it with a verification SHA.
4. Only verified `DefenseRecord` objects may cross the AdaptiveDefense -> A/B boundary.
5. A/B remains the execution/recovery authority; it does not become an observation or defense-learning authority.
6. No new limiter, threat engine, parallel baseline, or second A/B coordinator is introduced by this contract.
7. BuildingModel and engineering modules remain outside the security/evidence/recovery state path.

## Direction lock

Future security work must extend this direction rather than create a parallel chain:

```text
OBSERVE -> EVIDENCE -> VERIFY -> HANDOVER -> RECOVER -> OBSERVE
```

Any proposal that changes FlowGuard mathematics, duplicates AdaptiveDefense authority, introduces a second handover mechanism, or transfers peer runtime/model state requires a separate architectural decision before implementation.
