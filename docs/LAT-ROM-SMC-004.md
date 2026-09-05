# LAT-ROM-SMC-004 — Restart Reconstruction Contract

**Status:** Proposed  
**Revision:** Rev A  
**System:** LAT  
**Subsystem:** LAT-ROM / SMC-ROM

## Purpose

Define the neutral boundary for reconstructing permitted SMC-ROM operational
state after restart from preserved evidence.

## Contract

```text
preserved decision history + current registry/evidence
                         |
                         v
              restart reconstruction
                         |
                         v
             bounded immutable state
```

Restart reconstruction restores only permitted operational state. It does not
rewrite historical decisions and does not automatically activate a candidate.

## Required inputs

Reconstruction may consume:

- preserved decision identifiers/history;
- current registry version;
- applicability evidence;
- contract evidence;
- selector version.

The reconstruction boundary carries neutral evidence only. It does not contain
model implementation objects, peer-model references, `BuildingModel`, or a
selector instance.

## Safety invariants

1. Historical decision records are read-only evidence.
2. Duplicate decision identifiers are rejected.
3. Failed applicability or contract evidence blocks reconstruction.
4. Successful reconstruction produces a bounded state that is not `ACTIVE`.
5. Reconstruction does not execute a scientific model.
6. Reconstruction does not mutate the decision record store.
7. Human decision authority remains outside the reconstruction mechanism.

## Recovery relationship

Recovery and replacement remain distinct. Reconstruction restores permitted
operational state from preserved evidence; it does not decide which scientific
model should become active.

## Non-goals

- no selector integration;
- no candidate activation;
- no model execution;
- no scientific validation;
- no deletion or rewriting of history;
- no automatic leader election;
- no replacement of LAT-ROM supervisory authority.
