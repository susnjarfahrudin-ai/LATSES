# Post-#276 Security History Ledger

## Purpose

PR #276 is the frozen forensic security/runtime baseline selected for reconstruction. This ledger preserves the post-#276 chronology as evidence for later analysis and selective re-application. It is historical data, not an instruction to blindly restore every later change.

## Baseline

- PR: #276 — Agent/security runtime instrumentation
- Exact #276 HEAD: efc44786cbb7e079349da05ff1d3e5aabaa6aef7
- Baseline validation branch: baseline/276-clean-health-check
- Baseline validation: Verification #1896 GREEN; Windows Installer #1659 GREEN on snapshot commit 0b98718edf1f19f1ea908e2a7ccb35da5803a34e

## Chronology after #276

| PR | Event | Recorded purpose / reason | Evidence state |
|---|---|---|---|
| #277 | RCI-AD layer | Observation-only host telemetry foundation; no limiter/security decision authority | Verification #1550 GREEN; Installer #1333 GREEN |
| #278 | Revert #276 | Explicitly removed the #276 security/runtime instrumentation | Historical revert; not selected as target baseline |
| #279 | RCI-AD runtime boundary | Observation seam for HostTelemetry; limiter/policy/throttling kept out; included ReplayGuard bounded-cache fix required by a concrete security failure | Merged; later security chain continued |
| #280 | Thermal contract revert | Thermal-domain change, not the selected security baseline | Merged; recorded, not part of security restoration |
| #281 | FlowGuard observation | Observation-only bridge around fixed-baseline four-dimensional FlowGuard; 12% throttle / 20% stop mathematics preserved | Merged; manual long-run profile documented |
| #282 | A/B role rotation test | Test-only candidate; unmerged draft | Not main |
| #283 | A/B PID isolation test | Test-only candidate; unmerged draft | Not main |
| #284 | AdaptiveDefense restore | Restored AdaptiveDefense runtime boundary from pre-#278; did not restore the full #276 suite | Merged |
| #285 | Automatic bidirectional A/B handover | Test-only proof of A→B→A and B→A→B with verified evidence/checkpoint crossing only | Verification #1596 GREEN; Installer #1380 GREEN |
| #286 | RCI-AD ↔ AdaptiveDefense ↔ A/B contract | Narrow candidate integration: OBSERVE→EVIDENCE→VERIFY→HANDOVER→RECOVER→OBSERVE | Verification #1603 GREEN; Installer #1382 GREEN |
| #287 | Documentation baseline | Post-#286 documentation/reference snapshot | Verification #1604 GREEN |
| #288 | Integrated RCI-AD/AdaptiveDefense/A/B runtime test | Test-only integrated chain using isolated processes, authenticated IPC, FlowGuard, observation/binding, verified handover and recovery | Verification #1610 GREEN; Installer #1389 GREEN |
| #322 | Receive-path takeover proof | Test-only separation of capability from actual receive-path takeover; direct parent B attack does not activate B; verified handover through peer receive path does | Verification #1765 GREEN; Installer #1528 GREEN |
| #327 | Later security-adjacent work | Recorded as later history, not used to redefine the #276 baseline | Verification #1773 GREEN; Installer #1536 GREEN |
| #350 | GUI runtime launcher identity repair | Later runtime/GUI repair; not part of #276 security baseline | Historical post-baseline change |
| #355 | Controlled attack against main | Test-only adversarial audit; first concrete CI failure was ThreatScore 24.999997... vs exact 25.0 due decay timing | Audit branch; not merged |
| #356 | Disable obsolete #273 fail-safe workflow | Removed the contradictory old reminder workflow from main | Merged; Verification/Installer GREEN |
| #357 | Restore four #276 test files | Attempted partial restoration; blocked at collection by missing ModelRecoveryRecord | Not merged |
| #358 | Clean #276 baseline validation | Marker + snapshot only; proves exact #276 tree can pass current Verification/Installer without production edits | Draft/forensic |
| #359 | Security baseline restoration | Restores ten #276 security/runtime files to current main; target is to reverse #278's security/runtime removal | Pending CI before merge |

## Rules for later analysis

1. Historical GREEN means the referenced commit/PR passed its then-run CI; it does not prove today's main contains the same tree.
2. A merged PR is not evidence that every original file still exists on current main.
3. #276 is the selected reference baseline. Later work is preserved here so it can be compared and selectively re-applied after the baseline is stable.
4. Do not silently convert test-only capability into production runtime wiring.
5. First concrete CI failure only; minimal canonical fix; re-run the same gate.
6. No baseline learning from unverified observations.
7. No speculative production security changes merely to satisfy a historical test.

## Open evidence deliberately preserved

- The exact five-minute four-dimensional attack outputs need later runtime analysis.
- The exact live receive-path relationship between CyberFortress, FlowGuard/RCI-AD observation, AdaptiveDefense and A/B handover needs later proof.
- The old ModelRecoveryRecord contract was deleted/superseded in later architecture; its missing security semantics must be mapped explicitly before any restoration.
