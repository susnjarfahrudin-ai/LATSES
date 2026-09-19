# LAT-CES — Forensic Reconstruction of Adaptive A/B Defense

## Scope
Evidence-first historical reconstruction. No implementation/refactoring is authorized by this document.

Required order:
1. PR #274
2. PR #275
3. PR #276
4. Only then subsequent PRs/commits such as #277/#278.

## PR #274 — forensic record

**Title:** Security/adversarial b primary 20260905  
**Branch:** security/adversarial-b-primary-20260905  
**Base SHA:** f9db4179cab2122323e9450cf10eda3d122cfbc9  
**Head / merge SHA:** c84788203482c06a85bab70de51bbccd3a133649  
**Merged:** 2026-09-05 08:05:49 UTC  
**Commits:** 36  
**Changed files:** 8  
**Diff:** +728 / -15

### Files changed
- lat_ces/security/__init__.py
- lat_ces/security/adaptive_defense.py
- lat_ces/security/cyber_fortress.py
- lat_ces/security/flow_guard.py
- lat_ces/security/secure_ipc.py
- tests/test_potpune_sigurnosti.py
- tests/test_security_adversarial.py
- tests/test_security_b_primary_adversarial.py

### Proven architectural elements

PR #274 introduces and tests an adaptive-defense boundary containing:

A failure -> DefenseRecord -> B/standby quarantine -> verification -> promotion -> verified import.

DefenseRecord is immutable and contains:
- invariant_id
- attack_class
- evidence
- source
- verification_sha
- verified

Verified records require a verification SHA.

AdaptiveDefense provides:
- observe_failure()
- quarantine()
- is_quarantined()
- promote()
- import_verified()
- records()
- export_verified()

Promotion and import are explicitly verification-gated. The implementation does not mutate production security code and does not create a second security authority.

CyberFortress coordinates:
- SignedIPCChannel
- TokenBucketRateLimiter
- ThreatScoreEngine
- AdaptiveDefense

CyberFortress.receive() records an AdaptiveDefense failure when IPC unpacking fails. CyberFortress.handoff_verified_defense() copies only explicitly verified defense records to a standby boundary.

### FlowGuard

Four dimensions:
- frequency
- volume
- concurrency
- novelty

Fixed trusted baseline.
- 12% deviation: proportional throttling begins.
- 20% deviation: admission hard stop.
- strictest dimension controls the decision.
- untrusted traffic cannot redefine the baseline.

### Adversarial evidence

test_security_adversarial.py includes a slow-drip baseline-poisoning attack using 13 samples of 100 * 1.02^step. The final sample exceeds 125%. The test requires denial, zero throttle at hard stop, deviation >20%, and unchanged baseline.

test_security_b_primary_adversarial.py contains:
test_b_primary_survives_five_minute_four_dimension_adversarial_burst

The scenario explicitly treats B as primary under attack and A as standby. Duration is 300 seconds (5 minutes). The attack phases include quiet, spike, paired, reverse zig-zag, near-limit, and recovery. Four FlowGuard dimensions are exercised.

### Important open point

The B-primary test proves the adversarial test scenario, but PR #274 alone does NOT prove automatic OS-process PID takeover, automatic recovery, or a complete production A<->B runtime handover.

The B-primary test also checks that B-side records have source=="A". This is evidence that the source label semantics require later reconstruction; do not classify this as a bug without tracing subsequent PRs.

### CI evidence

At commit c84788203482c06a85bab70de51bbccd3a133649:
- LAT-CES Verification Pipeline #1547 — SUCCESS
- LAT-CES Windows Installer #1330 — SUCCESS

### PR #274 forensic status

PROVEN:
- adaptive-defense record boundary
- immutable DefenseRecord
- quarantine
- verification-gated promotion/import
- four-dimensional FlowGuard
- 12% throttle / 20% hard stop
- slow-drip baseline-poisoning defense
- B-primary adversarial test
- five-minute four-dimensional adversarial scenario

NOT PROVEN IN #274:
- automatic process takeover
- PID handover
- automatic A recovery
- complete production A/B runtime chain
- persistent learning lifecycle

## Rule for continuation

Do not jump to PR #276.
Next required forensic target: PR #275.

All later findings must be appended to this document in chronological order.


## PR #275 — forensic record

**Title:** Security: one-dimensional limiter load analysis  
**Head SHA:** 0ec96c8a0d9ecb50642687893f7c6a9cc4bfd9be  
**Merged:** 2026-09-05 08:05:49 UTC  
**Commits:** 37  
**Changed files:** 9  
**Diff:** +851 / -15

PR #275 is measurement-only adversarial testing. It adds 5-minute sustained frequency profiles at +24.9%, +19.9%, +14.9%, +12.9%; mathematical throttle verification; baseline immutability; and a 500-thread malformed-payload concurrency test through the real CyberFortress.receive() boundary. No new production security architecture is introduced.

**PROVEN:** deterministic FlowGuard load-profile test; sustained one-dimensional measurements; 500-thread malformed-input concurrency test; CI at #275 head: Verification Pipeline #1548 SUCCESS and Windows Installer #1331 SUCCESS.

**NOT PROVEN:** universal production ingress enforcement; automatic A/B takeover; PID handover; recovery lifecycle.

## PR #276 — forensic record

**Title:** Agent/security runtime instrumentation  
**Base SHA:** c1ec30f9cdf47ec4fe850cc998fbaeafe9ab11a4  
**Head SHA:** efc44786cbb7e079349da05ff1d3e5aabaa6aef7  
**Merge SHA:** ce220509385537a01628310088889663d8ca0309  
**Merged:** 2026-09-05 08:05:47 UTC  
**Commits:** 40  
**Changed files:** 10  
**Diff:** +1088 / -15

### Critical chronology observation

PR #276 base SHA is c1ec30f9..., while PR #275 head SHA is 0ec96c8a.... Therefore PR metadata does **not** prove direct #275-head -> #276-base ancestry. This remains **OPEN** and is not silently reconciled.

### What #276 adds

The material new test file is `tests/test_security_runtime_instrumentation.py`. Its module description explicitly identifies it as read-only runtime instrumentation for security load experiments and states that it does not alter production security logic, limiter parameters, baselines, payloads, or decision rules.

It measures Python/OS/kernel identity, CPU, logical CPUs, total and available memory, load average, RSS where supported, process CPU time, normalized CPU percentage, elapsed time, memory before/after, load and security-error counts. It repeats the earlier 5-minute FlowGuard profiles and 500-thread malformed-payload stress boundary.

**PROVEN:** read-only host/process runtime instrumentation test; host/process measurements around adversarial experiments; explicit separation from production security logic; final head Windows-compatible measurement path; final-head CI: Verification Pipeline #1553 SUCCESS and Windows Installer #1336 SUCCESS.

**NOT PROVEN:** runtime telemetry making security decisions; telemetry causing throttling; telemetry causing takeover/recovery; PID handover; A/B authority transfer; production failover; instrumentation feeding AdaptiveDefense.

### Architectural distinction

Evidence proven at #276 is:

`Adversarial workload -> FlowGuard/CyberFortress test -> runtime measurement -> CI evidence`

The causal production chain:

`Runtime measurement -> Defense Controller -> enforcement -> takeover/recovery`

is **NOT PROVEN** by #276.

### Current #274 -> #276 status

- #274 adaptive-defense/B-primary foundation — **PROVEN**
- #275 measurement/load analysis — **PROVEN**
- #276 read-only runtime instrumentation — **PROVEN**
- direct #275 -> #276 ancestry — **OPEN**
- automatic runtime A/B takeover/recovery across these three PRs — **NOT PROVEN**

## Continuation

The forensic sequence through #276 is now recorded. Any subsequent PR analysis must preserve this chronology and distinguish test evidence from production causality.


## PR #277 — forensic record

**Title:** Feature/rci ad layer  
**Base SHA:** f9db4179cab2122323e9450cf10eda3d122cfbc9  
**Head SHA:** 4273c7b1a510bda1202f9ddf160c5d5f33fb86fb  
**Merge SHA:** c1ec30f9cdf47ec4fe850cc998fbaeafe9ab11a4  
**Merged:** 2026-09-05 04:14:55 UTC  
**Commits:** 3; changed files: 3; +248/-0.

#277 introduces the RCI-AD telemetry foundation: `HostTelemetry` plus `collect_host_telemetry()`. The module explicitly says it only observes and does not make security decisions, throttle work, or modify the existing limiter. It gathers platform-neutral host data, with Linux `/proc` paths and Windows API paths, and represents unavailable metrics explicitly as `None` rather than fabricating them. Tests verify the telemetry object and explicit unavailable metrics.

**PROVEN:** observation-only host telemetry foundation; platform-specific collection paths; explicit unavailable-metric semantics; CI: Verification Pipeline #1550 SUCCESS and Windows Installer #1333 SUCCESS.

**NOT PROVEN:** telemetry-driven policy; telemetry-driven throttling; telemetry-driven takeover/recovery; causal connection to AdaptiveDefense or FlowGuard.

## PR #278 — forensic record

**Title:** Revert "Agent/security runtime instrumentation"  
**Base SHA:** ce220509385537a01628310088889663d8ca0309  
**Head SHA:** 6b39d1193954b44c38810bc17ab845fd0117dd30  
**Merge SHA:** 0ffd4af1ef6e655e70a0b668a192592fab199abc  
**Merged:** 2026-09-05 08:08:23 UTC  
**Commits:** 1; changed files: 10; +15/-1088.

PR #278 body explicitly says it reverts #276. The patch removes the runtime instrumentation test file and the #276-carrying security/test changes. The observed effect is a rollback of #276 from the mainline state at its base. It does **not** revert #277: #277 is a separate merge into main and is not among #278's changed files.

**PROVEN:** #276 is reverted by #278; #277 telemetry foundation is not reverted by #278; merge completed with CI: Verification Pipeline #1555 SUCCESS and Windows Installer #1338 SUCCESS.

**NOT PROVEN:** that #276 instrumentation was unsafe or architecturally wrong merely because it was reverted. The reason for the revert is not established by the PR metadata/patch alone.

## PR #279 — forensic record

**Title:** RCI-AD Runtime Observation Boundary  
**Base SHA:** 7873ea9515b396cce79f23cffa6de1f9973c7ece  
**Head/Merge SHA:** e54031c5ba325fd277feead50205f3021ce87264  
**Merged:** 2026-09-05 18:08:20 UTC  
**Commits:** 9; changed files: 6; +72/-4. Draft at metadata time.

PR #279 body states: add one observation-only runtime seam for existing HostTelemetry; collect one snapshot and forward it to an optional observer; keep limiter/policy/throttling out of this layer; preserve application behavior when no observer is supplied; add targeted regression tests; include the minimal ReplayGuard bounded-cache fix required by the first concrete security failure. It also explicitly says it does not modify #277 telemetry implementation or revive #276.

Production changes in the patch:
- `lat_ces/rci_ad/observation.py`: `observe_host_telemetry()` collects one immutable `HostTelemetry` snapshot, forwards that exact snapshot to an optional observer callback, and returns it.
- `lat_ces/application/service.py`: `analyze_config()` accepts an optional `telemetry_observer`; if supplied, it calls `observe_host_telemetry()` before canonical analysis. Without an observer, existing behavior remains unchanged.
- `lat_ces/security/secure_ipc.py`: removes capacity-based eviction of active replay nonces, preserving the same security fix already seen in #274.
- `pytest.ini`: adds `pythonpath = .`.
- tests verify exact snapshot forwarding and absence of limiter/throttle behavior.

**PROVEN:** an application-level observation seam exists; one immutable host snapshot can be forwarded to an observer; explicit no-policy/no-throttle boundary is tested; ReplayGuard bounded-cache fix is present; CI: Verification Pipeline #1582 SUCCESS and Windows Installer #1366 SUCCESS.

**NOT PROVEN:** observer implementation that makes security decisions; telemetry-to-policy causality; telemetry-driven throttling; telemetry-driven A/B takeover/recovery; PID handover; recovery controller.

### Critical chronology/architecture point

#279 is not a revival of #276. Its body explicitly says it does not revive #276, and its implementation is a narrower observation seam around the #277 `HostTelemetry` foundation. It therefore represents a new path:

`HostTelemetry -> observation seam -> optional observer`

The observer is an extension point, not itself a proven policy authority.

## Consolidated #274 -> #279 status

**PROVEN:** #274 adaptive-defense foundation; #275 adversarial/load measurement; #276 read-only runtime instrumentation; #277 RCI-AD host telemetry foundation; #278 explicit revert of #276; #279 observation seam around HostTelemetry.

**OPEN:** direct #275 -> #276 ancestry (PR base/head mismatch); exact reason #278 reverted #276; exact downstream identity/role of any #279 observer.

**NOT PROVEN:** a production causal chain from host telemetry to enforcement, A/B takeover, PID handover, or recovery.
