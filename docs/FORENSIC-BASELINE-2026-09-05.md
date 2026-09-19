# LAT-CES Forensic Baseline — 2026-09-05

## Canonical repository state

Repository: `susnjarfahrudin-ai/LATSES`

Canonical production branch: `main`

Post-merge baseline SHA: `5fca8d9cf11a0390c9f9443b355338851c23717f`

Previous main SHA: `7873ea9515b396cce79f23cffa6de1f9973c7ece`

Merged change: PR #281, `RCI-AD: observe FlowGuard mathematics without changing limiter`.

The merge was performed only after the PR head was GREEN and mergeable. The PR head was `0722ed24cfebd371777b37e13f664768e40f315c`.

## Evidence boundary

PR #281 head evidence before merge:

- Verification #1585: GREEN (`33980931272`)
- Windows Installer #1369: GREEN (`33980931274`)
- PR #281: mergeable, 15 commits, 11 changed files, 391 additions, 4 deletions

The post-merge `main` push automatically started the Windows Executable and Windows Installer workflows for `5fca8d9cf11a0390c9f9443b355338851c23717f`. Post-merge verification is therefore a separate gate and must not reuse the pre-merge evidence.

## Security architecture decision

`lat_ces/security/secure_ipc.py` is canonical for authenticated IPC and replay protection.

The merged ReplayGuard hardening preserves active nonces for the replay TTL instead of evicting active entries merely because the bounded-cache capacity is reached. The security invariant is therefore not weakened by cache-pressure eviction.

`lat_ces/security/flow_guard.py` is the canonical mathematical FlowGuard owner.

FlowGuard has exactly four dimensions:

- `frequency`
- `volume`
- `concurrency`
- `novelty`

The trusted baseline is fixed after construction. Observed traffic cannot rewrite the baseline. Throttling starts above 12% deviation and the hard stop is at 20%; the strongest dimension controls the decision.

The RCI-AD observation bridge is downstream of FlowGuard:

`FlowGuard.evaluate()` → `observe_flow()` → caller-supplied observer

The observer receives an immutable observation and has no return path into the guard. It does not own the baseline, decision, admission policy, replay state, or security keys.

## Building / GUI architecture decision

`BuildingModel` remains the single physical source of truth.

The canonical production GUI path remains:

`lat_ces.gui_complete:main` → `CompleteBuildingWorkspaceApp` → one `BuildingModel` → active `Level` → one `FloorPlan` → visual/editor projections.

Structural, thermal, MEP, quantity and visualization layers remain downstream projections and must not create competing physical models.

The production GUI acceptance sequence remains:

`Reference House → Tlocrt → Presjek → 3D → Provjera → Izvještaj → Materijali`

## Branch forensics

The fork contains a large number of historical development branches. Several are exact duplicates at the same commit SHA, especially recovery/session-log branches and repeated visualization/UFH branches. These are historical pointers, not separate implementations.

Examples of exact duplicate pointers observed during the audit:

- `agent/building-model-drafting-geometry` and `agent/building-model-editor-fix` → `7ff9dd0...`
- `feat/structural-production-building-model-bridge` → same SHA as `feat/structural-production-analysis-bridge`
- `feat/thermal-room-heat-loss-v1` and `feat/thermal-room-heat-loss-v1-checkpoint` → `2818fca...`
- several `feat/visualization-3d-blender-scene-spec-*` branches → `1611d928...`
- several `recovery/session-log-*` branches → `33e6c28...`
- several UFH PR branches point to repeated historical checkpoints.

These duplicate refs should be treated as archive/history until a deliberate branch-retention cleanup is performed. They must not be merged merely because they exist.

## Pull-request history classification

The PR history contains several explicit revert/supersede cycles. The canonical rule is to follow the resulting `main` tree, not the existence of an old PR.

Examples:

- #22 structural truss solver was reverted by #23.
- #30 compatibility export fix was followed by revert #31.
- #44 fitting validation test was reverted and later corrected through subsequent canonical work.
- #69 unified workspace prototype was reverted by #72.
- #75 unified Building Model foundation was reverted by #76 and later architectural work was rebuilt through the canonical BuildingModel path.
- #96 preliminary structural load-path work was reverted by #97 and later reconsidered through subsequent isolated structural work.
- #213 thermal input contract was accidentally merged and then explicitly reverted by #280; current main is the post-revert state.
- #276 security runtime instrumentation was reverted by #278 and is not a canonical production authority.

Historical PRs remain useful evidence. They are not release candidates unless their exact current head is rebased onto `main` and independently verified.

## Two-repository boundary

The active fork is `susnjarfahrudin-ai/LATSES`.

The original repository `fahrudinsusnjar-eng/LATSES` remains a separate historical source repository whose `main` was observed at `170ec750f9aaa4ecba227bf9401674919e8abd81`.

No wholesale synchronization from the original repository is permitted. Any code recovered from that repository must be treated as historical material and reintroduced only through an explicit, reviewable, independently verified change on the active fork.

## History branch

`history` was created as an archival pointer and moved to the post-merge baseline `5fca8d9cf11a0390c9f9443b355338851c23717f`.

The existing feature/recovery branches are intentionally preserved. Their refs are the historical record. The `history` branch is the stable archival snapshot, not a second production authority.

## Release and verification rule

The exact source SHA must always be bound to its own Verification result, Installer result, artifact identity and artifact SHA-256. Evidence from a different SHA is historical evidence only.

After this merge, the next authoritative state is:

`main @ 5fca8d9cf11a0390c9f9443b355338851c23717f`

It becomes a fully proven release baseline only after post-merge Verification and post-merge Installer/GUI evidence are GREEN for this exact SHA.

## Residual architecture risk

ReplayGuard now refuses unsafe active-nonce eviction, but `max_entries` is no longer a security eviction mechanism. This avoids replay-cache correctness failure at the cost of potential memory growth under sustained unique-nonce load. This is recorded as a monitoring/pressure concern, not changed speculatively in this baseline. Any future capacity policy must preserve the replay invariant and be introduced as a separate measured security delta.

No other architectural correction is authorized by this forensic pass without a concrete failing assertion, reproducible behavior, or explicit new contract.

## Working rule from this baseline

`main` = known-good candidate baseline.

New work = isolated feature branch.

Acceptance = exact SHA → focused test → Verification → Installer/GUI where applicable → evidence → merge → post-merge Verification.

Failure handling = first concrete failure → smallest canonical fix → same gate again.
