# SMC-004 — Consolidation Acceptance Gate

A module is accepted only when:
1. canonical import path resolves;
2. unit/dimension contracts are satisfied;
3. reference tests pass;
4. provenance/identity is preserved;
5. no legacy import regression remains;
6. SCI-to-code traceability is recorded;
7. CI passes.

This gate prevents documentation-only modules from being represented as implemented.
