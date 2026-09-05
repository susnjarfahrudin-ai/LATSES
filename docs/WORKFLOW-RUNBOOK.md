# LAT-CES CI / Release Runbook — persistent workflow memory

## Current closure baseline — 2026-09-04

The production architecture is now treated as one canonical chain:

`Scientific Core → BuildingModel → canonical GUI → GUI acceptance → PyInstaller EXE → Windows Installer → artifact + SHA-256 → release evidence`

The desktop GUI entrypoint is `lat_ces.gui_complete:main`. `CompleteBuildingWorkspaceApp` is the production workspace and the floor plan is rendered from the same `BuildingModel` used by downstream structural, thermal, MEP, quantity and visualization projections.

The retired GUI authorities `gui_functional.py`, `gui_release.py` and `gui_master.py` must not be reintroduced into the production packaging path. Historical GUI baseline checks by raw Git blob SHA are not acceptance criteria; acceptance is behavioral and must verify the canonical object path and production entrypoint.

## Latest merged security foundation

### PR #252

Head SHA: `2e2e32ba597449464c0e1d6ad74dbcbc0b7cdcd8`

Merged to `main` as:

`a835f0fdcaeb4aa3829b154b52d3df30adbe98ce`

The security boundary contains the established root-of-trust, key derivation, secure mutable-buffer handling, crash-safe atomic persistence, process identity, HMAC IPC freshness/replay protection, threat scoring/CIDR allowlists, Linux/Windows process hardening, focused tests and LAT-SEC-001 documentation. fileciteturn707file0L7-L10

Pre-merge release evidence for the exact PR #252 head:

- Verification #1423: **GREEN**
- Windows Installer #1234: **GREEN**
- Installer artifact: `LAT-CES-Windows-Installer`
- Artifact ID: `9921807317`
- Artifact size: `11,062,482 bytes`
- Artifact ZIP SHA-256: `ef658788a2a798bf3bf1fe18ad5aea5c0bbecb5585ea59c332078e3240095f6e`

This security foundation is part of the existing canonical security boundary. A second parallel `cyber_fortress.py` authority using a plaintext `master.key`, independent Fernet state and ad-hoc Manager processes must not be merged as-is. New security work must reuse or extend the existing boundary rather than create competing key, evidence or replay authorities.

## Security Delta v2 — current development gate

Working branch: `agent/security-delta-v2-20260904`

Base: `main @ ed77ac73206b9ddf08fe09524bc6c2e4370dd85a`.

Scope is intentionally narrow:

1. Preserve #252 OS-keyring root secret custody; no plaintext `master.key` path.
2. Preserve the existing receiver-side nonce replay guard and make IPC freshness reject timestamps beyond an explicit future-skew allowance. The existing channel already authenticates the envelope and checks the nonce before delivery. fileciteturn709file0L2-L2
3. Add a reusable deterministic token-bucket admission primitive for per-key rate limiting. It is a boundary primitive only; threat scoring/allowlisting remains the separate policy authority.
4. Keep atomic persistence as the established write → fsync → replace → POSIX directory fsync implementation; do not introduce a second persistence path. fileciteturn710file0L2-L2
5. Extend regression tests so the new security behavior is executable under the existing Verification pipeline. The CI command must fail on pytest failure; no print-only acceptance function is allowed.

### Security Delta acceptance contract

`Security primitive → focused regression test → existing Verification pipeline → first concrete failure → minimal fix → GREEN → PR review → merge → post-merge Verification`

No GUI, engineering-model semantics, BuildingModel identity, or installer architecture changes belong in this delta.

## GUI acceptance contract

The canonical behavioral contract is:

`production entrypoint → CompleteBuildingWorkspaceApp → one BuildingModel → active Level → one FloorPlan → FloorPlanEditor/Canvas`

The automated acceptance tests must verify this behavior, not a historical source-file hash. The Windows GUI acceptance remains the release-level check that the visible sequence works coherently:

`Reference House → Tlocrt → Presjek → 3D → Provjera → Izvještaj → Materijali`

Any failure is handled by the project rule:

`first concrete failure → minimal fix → Verification → GREEN → next gate`

## Release evidence rule

A release record must always bind the exact source SHA to Verification, Installer, artifact name, artifact size and artifact SHA-256. Historical evidence from another SHA is not reusable.

A post-merge release chain on `main` is considered proven only when the current `main` commit has successful verification and successful installer packaging with the resulting artifact evidence recorded.

## Pull-request hygiene

Historical GUI/Reference-House experiments that target superseded authorities, obsolete fixture files or fixed historical blobs are **SUPERSEDED** and should be closed rather than repaired into the current architecture.

Domain PRs that contain potentially reusable engineering work remain **ACTIVE/BLOCKED** until rebased onto current `main` and revalidated. An old PR is not a release candidate merely because its branch is technically mergeable.

## Architectural rule

`BuildingModel` is the source of truth. GUI, structural, thermal, MEP, quantity and visualization views are downstream projections and must not create competing physical models.

## Persistent handoff — next development cycle

### Completed before the Security Delta gate

- PR #252 security-hardening foundation merged.
- PR #253 canonical GUI/acceptance closure merged.
- `main @ ed77ac73206b9ddf08fe09524bc6c2e4370dd85a` verified after merge.
- Verification #1429: **GREEN**.
- Windows EXE #563: **GREEN**.
- Windows Installer #1240: **GREEN**.
- GUI visual acceptance on the installer: **GREEN**.
- Release artifacts and SHA-256 evidence recorded in the current release history.

### Security Delta v2 implemented on this branch

- `lat_ces/security/rate_limit.py`: deterministic per-key token bucket with idle cleanup.
- `lat_ces/security/secure_ipc.py`: explicit maximum future clock skew in addition to age and nonce replay checks.
- `tests/test_security_hardening.py`: regression coverage for future-skew rejection and deterministic rate limiting/refill behavior.
- No duplicate security authority, plaintext root-key file, or alternate evidence store introduced.

### Planned next steps after GREEN merge

1. Inspect the merged security delta for integration opportunities with the constitutional registry / station IPC layer; do not migrate consumers speculatively.
2. Add persistent rate-limit/threat-score policy only where a concrete caller exists and the ownership boundary is explicit.
3. Add security acceptance evidence to the release runbook, binding the exact merge SHA to the successful Verification run.
4. Only after that, return to blocked domain PRs and revalidate one candidate at a time against current `main`.

### Failure rule for future work

`first concrete failure → identify exact assertion/log → smallest canonical fix → rerun the same gate → GREEN → continue`

Never stack unrelated fixes on a red verification. Never reuse stale evidence from another commit. Never introduce a parallel source of truth for BuildingModel, security keys, replay state, persistence, GUI packaging, or release evidence.

## 2026-09-05 — RCI-AD + FlowGuard mathematical observation gate

Development branch: `feature/rci-ad-flow-observation-20260905`  
Draft PR: `#281`  
Base: `main @ 7873ea9515b396cce79f23cffa6de1f9973c7ece`  
Verified RCI-AD predecessor: `e54031c5ba325fd277feead50205f3021ce87264`

### Purpose

Connect the fixed-baseline FlowGuard mathematics to RCI-AD as an observation path only. The mathematical guard remains the decision owner; RCI-AD receives an immutable observation record and has no return path into the guard.

### Information-flow contract

`FlowGuard.evaluate()` → `observe_flow()` → caller-supplied `FlowObserver`

The observation contains the four named dimensions, trusted baseline, observed values and the exact mathematical decision. RCI-AD does not store an observer, mutate the baseline, recalculate the decision, or alter admission thresholds.

### Mathematical boundary

- dimensions: `frequency`, `volume`, `concurrency`, `novelty`
- fixed trusted baseline; no baseline learning from untrusted traffic
- proportional throttling begins above 12% deviation
- hard stop at 20% deviation
- strongest dimension determines the decision
- observation layer is read-only with respect to the mathematical guard

### Analysis workflow

`.github/workflows/rci-ad-flowguard-analysis.yml` is `workflow_dispatch` only and is intentionally outside the normal Verification path.

The manual profile runs one dimension at:

`+24.9% → +19.9% → +14.9% → +12.9%`

for 5 minutes at each level, forwards each decision through the RCI-AD observation bridge, and publishes a compact JSONL artifact. The workflow does not modify limiter code.

### Current integrity warning

The ReplayGuard fix that passed on the RCI-AD branch is **not yet present on current `main`**. Current `main` still contains the old bounded-cache eviction implementation. Therefore GREEN evidence from `#279` / `#281` must not be relabeled as post-merge `main` security evidence until the exact fix is independently merged and reverified.

### Acceptance rule

`RCI-AD observation → focused regression → mathematical profile → evidence artifact → review → only then any policy/decision integration`

No change to the existing rate limiter, no new persistence authority, no new key/replay authority, and no GUI changes are allowed in this gate.
