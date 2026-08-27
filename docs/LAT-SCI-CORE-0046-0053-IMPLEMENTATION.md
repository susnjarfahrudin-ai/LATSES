# LAT-SCI-CORE-0046–0053 — Measurement Engine implementation alignment

## Normative source

This implementation is derived from the Measurement segment documented in `SCI 1-145 LAT SES.docx`, specifically:

- LAT-SCI-CORE-0046 — Measurement Engine Specification
- LAT-SCI-CORE-0047 — Measurement Engine Reference Implementation
- LAT-SCI-CORE-0048 — Measurement Engine Verification Test Specification
- LAT-SCI-CORE-0049 — Measurement Engine Verification Execution Report
- LAT-SCI-CORE-0050 — Measurement Engine Hardening Specification
- LAT-SCI-CORE-0051 — Measurement Engine Hardening Reference Implementation
- LAT-SCI-CORE-0052 — Measurement Engine Hardening Verification Test Specification
- LAT-SCI-CORE-0053 — Measurement Engine Hardening Verification Execution Report

## Canonical model

A measurement is a scientific record, not a bare number:

`M = (Q, V, U, σ, I, C, T, E)`

where `Q` is physical quantity, `V` measured value, `U` unit, `σ` uncertainty, `I` instrument, `C` calibration, `T` timestamp, and `E` evidence.

The G2 `Quantity` is the authoritative value/unit carrier. `Measurement.value` and `Measurement.unit` are compatibility views and cannot diverge from the Quantity.

## Functional layer

The package now provides:

```text
lat_ces/scientific/measurement/
├── measurement.py
├── instrument.py
├── calibration.py
├── uncertainty.py
├── provenance.py
├── validation.py
├── registry.py
├── sko_integration.py
└── compatibility.py
```

## Hardening layer

SCI-CORE-0050–0053 adds:

```text
Measurement
 ↓
Integrity Hash
 ↓
Validation
 ↓
Revision
 ↓
Audit
 ↓
Evidence
 ↓
ScientificKnowledgeObject
```

Implemented elements:

- deterministic SHA-256 measurement integrity hash;
- modification detection;
- immutable revision records preserving measurement identity;
- audit record with actor/action/revision/timestamp;
- immutable evidence linkage;
- calibration integrity hash and protection;
- hardened measurement envelope;
- SKO conversion/preservation helpers.

## Compatibility rule

Existing `PhysicalQuantity`, `MeasurementDevice`, `AccuracySpec`, and factory APIs remain available as compatibility surfaces. They are not additional authoritative Measurement models.

## Boundary rule

Acquisition technologies such as RS-485, Modbus, DAQ, PLC and Ethernet belong outside the scientific Measurement package. They should produce canonical observations/Measurements through infrastructure adapters.

## Verification mapping

The implementation test set covers the SCI functional and hardening requirements, including identity, quantity/unit consistency, uncertainty, instrument, calibration, timestamp, registry, SKO integration, hashing, modification detection, revisions, audit and evidence preservation.

A passing test suite proves software conformance to the defined contract. It is not by itself a claim that a physical instrument, calibration laboratory or engineering conclusion is universally valid.

## Architectural consequence

Measurement is the bridge between physical reality and the Scientific Knowledge lifecycle:

`Nature → Phenomenon → Physical Quantity → Measurement → Evidence → Knowledge → Preservation`

The later SCI provenance, validation, trust, assurance and lifecycle engines consume the Measurement record rather than redefining it.
