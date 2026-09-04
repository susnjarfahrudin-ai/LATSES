# LAT-ROM-SMC-003 — Independent Decision Record Contract

**Status:** Proposed  
**Revision:** Rev A  
**System:** LAT  
**Subsystem:** LAT-ROM / SMC-ROM

## Purpose

Define the independent historical record boundary for SMC-ROM operational
lifecycle decisions.

## Contract

```text
SMC-ROM operational decision
          |
          v
  immutable DecisionRecord
          |
          v
 independent append-only store
```

The record store preserves decision evidence independently from bounded
selector state. Operational cleanup, bench eviction, replacement, and
reconstruction must not delete historical records.

## Required provenance

Each record carries:

- decision identifier;
- timestamp;
- session identifier;
- model/candidate identifier and version;
- previous and resulting lifecycle state;
- reason;
- evidence/provenance;
- applicability result;
- contract result;
- optional superseded decision identifier;
- selector version.

These fields describe an operational decision and do not constitute a claim
of scientific truth.

## Append-only invariant

A decision identifier is unique. An existing record cannot be replaced through
the store. The store exposes records in append order and preserves them after
operational state changes.

## Information isolation

The record store must not contain model implementation objects, peer-model
references, `BuildingModel`, or selector instances. It is an evidence store,
not an execution coordinator.

## Recovery relationship

Restart reconstruction may use preserved decision history, current registry,
applicability, contract evidence, and versions to rebuild permitted operational
state. Reconstruction must not rewrite historical records.

## Non-goals

- no model execution;
- no candidate activation;
- no scientific validation;
- no automatic blame assignment;
- no deletion or rewriting of historical decisions;
- no replacement of LAT-ROM supervisory authority.
