# SCI 1–145 / LATSES Consolidation Map

**Baseline:** `main` @ `144be937d485762b7c202e37e8eff93cd49099c6`
**Source specification:** `SCI 1-145 LAT SES.docx`
**Purpose:** map the SCI scientific architecture against the actual LATSES implementation before adding new scientific modules.

## 1. SCI architecture map

| SCI range | Scientific scope | Actual architectural role | Current disposition |
|---|---|---|---|
| 0001–0009 | ScientificKnowledgeObject foundation, verification, hardening | Core scientific identity/traceability foundation | KEEP / CANONICAL target |
| 0010–0015 | Dimension Engine | `lat_ces.scientific.units.core.Dimension`; legacy `lat_ces.core.dimensions` is a compatibility facade | KEEP / CANONICAL = scientific |
| 0016–0028 | Unit Engine + Unit Registry + hardening/formal verification | `lat_ces.scientific.units.*` | KEEP / MERGE around scientific canonical layer |
| 0029–0037 | Derived Units Engine + hardening/verification | Scientific unit-expression/derived-unit layer | KEEP / ADAPT; verify exact implementation coverage |
| 0038–0045 | Physical Quantity Engine + hardening | `lat_ces.scientific.quantity` package; top-level `lat_ces.scientific.quantity.py` is a shim | KEEP / CANONICAL = scientific quantity package |
| 0046–0053 | Measurement Engine + hardening | Measurement specification is broader than currently visible domain modules; implementation coverage requires explicit audit | ADAPT / NEW where SCI contract is missing |
| 0054–0061 | Scientific Data Provenance + Validation | SCI-defined provenance/validation governance layer | ADAPT / NEW unless matching implementation is proven |
| 0062–0073 | Scientific Knowledge Ontology + Synthesis | SCI-defined ontology/synthesis ecosystem layer | ADAPT / NEW unless matching implementation is proven |
| 0074–0085 | Knowledge Evolution + Governance | lifecycle/evolution/governance architecture | ADAPT / NEW unless matching implementation is proven |
| 0086–0093 | Integrity & Trust + Assurance | trust/integrity/assurance layer | ADAPT / NEW unless matching implementation is proven |
| 0094–0101 | Knowledge Lifecycle + Ecosystem Management | system-level scientific knowledge lifecycle | ADAPT / NEW unless matching implementation is proven |
| 0102–0121 | Scientific Knowledge Ecosystem Intelligence | analysis/pattern/risk/explanation layer; intelligence must not become scientific authority | ADAPT / NEW; keep separated from validation/governance |
| 0122–0125 | Ecosystem Integration + verification | integration of knowledge, governance, hardening, evolution and traceability | NEW architecture/integration work |
| 0126–0129 | Federation architecture + reference implementation | multi-ecosystem federation | NEW; not a current domain engine |
| 0130–0137 | Federation security architecture + hardening | security boundary around federation | NEW / future layer |
| 0138–0141 | Security Hardening Governance | governance of hardened security | NEW / future layer |
| 0142–0145 | Adaptive Security Governance | adaptive security under constitutional control | NEW / future layer |

**Important:** SCI 1–145 is not 145 independent domain solvers. It contains specification → implementation → verification → hardening → governance/evolution chains. Therefore the correct consolidation unit is the *capability contract*, not the document number alone.

## 2. Current canonical scientific foundation found in `main`

### Canonical

- `lat_ces.scientific.units.core` — current physical dimension/unit implementation.
- `lat_ces.scientific.quantity` package — current PhysicalQuantity hardening layer.
- `lat_ces.scientific.*` domain models — canonical scientific calculations where a legacy module explicitly delegates to them.

### Compatibility layer

- `lat_ces.core.dimensions` — compatibility facade over the scientific units layer.
- `lat_ces.modules.plenum` — compatibility facade over `lat_ces.scientific.plenum`.
- `lat_ces.modules.duct` — compatibility adapter over `lat_ces.scientific.duct_friction`.
- `lat_ces.modules.pressure` — compatibility facade over `lat_ces.scientific.pressure_drop`.
- `lat_ces.modules.quantity.py` has already been retired; callers must use the canonical scientific quantity package.

### Confirmed legacy/application domain modules

Current `lat_ces/modules` contains legacy/application-facing engines including:

- `acoustics.py`
- `duct.py`
- `fan_laws.py`
- `fittings.py`
- `fluid_network.py`
- `pipeline.py`
- `pipeline_v3.py`
- `plenum.py`
- `pressure.py`
- `psychrometrics.py`
- `thermal.py`

These are **not automatically removable**: several are compatibility facades that preserve old APIs. They must remain only while callers/tests require them.

## 3. First concrete defect exposed by the map

`lat_ces/modules/pipeline.py` and `lat_ces/modules/pipeline_v3.py` still import:

```text
lat_ces.modules.quantity.PhysicalQuantity
```

The legacy quantity implementation has already been retired while the canonical implementation is `lat_ces.scientific.quantity`. This creates a stale dependency in the old pipeline layer.

Decision:

- `pipeline.py` → ADAPT to canonical quantity import, retain only as compatibility/integration wrapper until callers are migrated.
- `pipeline_v3.py` → ADAPT to canonical quantity import; evaluate whether it becomes the single legacy network integration facade after tests/callers are checked.
- Do **not** create another quantity implementation.

## 4. Consolidation decision matrix

| Component family | Decision | Canonical source |
|---|---|---|
| Dimension | KEEP + MOVE consumers | `lat_ces.scientific.units` |
| Unit | KEEP | `lat_ces.scientific.units` |
| PhysicalQuantity | KEEP | `lat_ces.scientific.quantity` |
| Legacy dimension imports | KEEP temporarily as facade | `lat_ces.core.dimensions` |
| Plenum | KEEP facade / canonical scientific model | `lat_ces.scientific.plenum` |
| Duct friction | KEEP facade / canonical scientific model | `lat_ces.scientific.duct_friction` |
| Pressure/fan power | KEEP facade / canonical scientific model | `lat_ces.scientific.pressure_drop` |
| Acoustics | ADAPT after side-by-side contract check | scientific + legacy facade |
| Thermal | ADAPT after side-by-side contract check | scientific + legacy facade |
| Fittings | KEEP facade / canonical quantity | scientific fitting model |
| Old pipeline v2 | ADAPT; remove stale quantity dependency | canonical quantity + existing facades |
| Pipeline v3/network | ADAPT; candidate canonical integration facade | canonical scientific engines |
| SCI provenance/validation/ontology/synthesis/governance/etc. | NEW/ADAPT only after repository evidence | SCI contracts |
| Federation/security/adaptive governance | NEW; do not mix with HVAC domain code | future scientific governance layer |

## 5. Canonicality rule

A module is **CANONICAL** only when it owns the scientific implementation and is the source used by higher layers.

A module is **FACADE/ADAPTER** when it exists only to preserve a stable legacy API and delegates to the canonical implementation.

A module is **DUPLICATE** when it independently implements the same scientific law/model already owned by the canonical layer.

A module is **RETIRE** only after callers/tests have been migrated and the compatibility contract is no longer required.

A module is **NEW** only when the SCI contract has no existing implementation with equivalent semantics.

## 6. SCI-to-code development order

1. Stabilize canonical units/dimensions/quantity.
2. Remove stale imports and duplicate scientific implementations.
3. Preserve legacy APIs through explicit facades while callers migrate.
4. Verify the domain engines against the SCI scientific contracts.
5. Implement missing Scientific Core governance/provenance/ontology/evolution layers only where the repository lacks them.
6. Only then add new physics/domain modules.
7. Build/rebuild the Windows EXE and installer from the consolidated canonical entry point.

## 7. Explicit HOLD points

- Do not add new scientific modules merely because an SCI document describes them.
- Do not delete compatibility modules before import/caller/test inventory is complete.
- Do not create a second `PhysicalQuantity`, `Dimension`, `Unit`, or equivalent scientific primitive.
- Do not treat AI/intelligence/federation layers as replacements for scientific validation or governance.
