# SCI 1–145 → MAIN → SMC Consolidation Matrix

**Status:** 55/55 legacy audit complete — execution baseline
**Branch:** `main`
**Governance:** SMC-001 → SMC-004

## Current consolidation state

- Quantity bridge: **RETIRED** after import migration and CI-detected dependency cleanup.
- Equation engine: **MOVED/ADAPTED** into `lat_ces/scientific/equations/legacy.py`; legacy `lat_ces/modules/equation.py` retired.
- Units/Dimensions: **MOVED** implementation ownership into `lat_ces/scientific/units/core.py`; `lat_ces/core/dimensions.py` and Scientific dimension/unit modules are compatibility facades.
- Provenance: **CANONICAL FACADE + LEGACY STORAGE ADAPTER**; no deletion of historical ledger.

## Execution rule

No RETIRE is valid without zero production imports, zero required test imports, canonical replacement, regression evidence, CI GREEN and SMC-004 acceptance.

## 55/55 matrix

| # | Responsibility | Canonical owner | Real `main` path / evidence | Decision |
|---:|---|---|---|---|
| 0001 | Axioms | `lat_ces/scientific/core` | `lat_ces/core/axioms.py` + tests | KEEP + ADAPT |
| 0002 | SKO foundation | `lat_ces/scientific/core` | `lat_ces/core/sko.py` + tests | KEEP + ADAPT |
| 0003 | SKO identity | `lat_ces/scientific/core` | `lat_ces/core/sko.py` | MERGE |
| 0004 | SKO governance | `lat_ces/scientific/core` | `lat_ces/core/sko.py` | MERGE |
| 0005 | SKO verification | `lat_ces/scientific/core/verification` | core/SKO tests | MERGE |
| 0006 | Dimensions | `lat_ces/scientific/units/core.py` | implementation moved; core facade | MOVE |
| 0007 | Dimension algebra | `lat_ces/scientific/units/core.py` | canonical Scientific Units algebra | MOVE |
| 0008 | SKO/unit bridge | `lat_ces/scientific/core` + units | compatibility bridge | MERGE |
| 0009 | Core validation | `lat_ces/scientific/core/validation` | core validation/tests | MERGE |
| 0010 | Physical quantity legacy API | `lat_ces/scientific/quantity` | canonical PhysicalQuantity; bridge retired | RETIRE |
| 0011 | Equation engine | `lat_ces/scientific/equations/legacy.py` | legacy API moved under Scientific Equations | MOVE + ADAPT |
| 0012 | Plenum | `lat_ces/scientific/models/plenum` | legacy + scientific plenum paths | MERGE + ADAPT |
| 0013 | Acoustics | `lat_ces/scientific/models/acoustics` | legacy + scientific acoustics | MERGE + ADAPT |
| 0014 | Thermal | `lat_ces/scientific/models/thermal` | legacy + scientific thermal | MERGE + ADAPT |
| 0015 | Pressure/fan | `lat_ces/scientific/models/pressure` | legacy + pressure-drop/fan paths | MERGE + ADAPT |
| 0016 | Duct/friction | `lat_ces/scientific/models/duct` | legacy + friction/loss paths | MERGE + ADAPT |
| 0017 | Unit verification spec | `lat_ces/scientific/units/verification` | unit tests/evidence | MERGE |
| 0018 | Unit implementation | `lat_ces/scientific/units/core.py` | moved implementation | MOVE |
| 0019 | Unit verification execution | `lat_ces/scientific/units/verification` | unit tests/evidence | MERGE |
| 0020 | Registry governance | `lat_ces/scientific/units/registry.py` | actual registry | KEEP + ADAPT |
| 0021 | Unit registry implementation | `lat_ces/scientific/units/registry.py` | actual registry | KEEP |
| 0022 | Registry verification specification | `lat_ces/scientific/units/verification` | registry tests | MERGE |
| 0023 | Registry verification execution | `lat_ces/scientific/units/verification` | registry evidence/tests | KEEP |
| 0024 | Registry hardening specification | `lat_ces/scientific/units/integrity` | canonical identity/integrity tests | ADAPT |
| 0025 | Registry hardening implementation | `lat_ces/scientific/units/registry.py` | actual registry | ADAPT |
| 0026 | Hardening verification specification | `lat_ces/scientific/units/verification` | hardening tests | MERGE |
| 0027 | Hardening verification execution | `lat_ces/scientific/units/verification` | evidence/tests | KEEP |
| 0028 | Formal verification | `lat_ces/smc/verification` | formal verification artifacts | MOVE |
| 0029 | Derived units specification | `lat_ces/scientific/equations` + units | equation/dimension implementation | MERGE |
| 0030 | Derived units implementation | `lat_ces/scientific/equations` | scientific equation paths | ADAPT |
| 0031 | Derived units verification spec | `lat_ces/scientific/equations/verification` | equation tests | MERGE |
| 0032 | Derived units verification | `lat_ces/scientific/equations/verification` | equation/unit tests | KEEP |
| 0033 | Derived units hardening spec | `lat_ces/scientific/quantity/integrity` | integrity concepts/tests | ADAPT |
| 0034 | Derived units hardening implementation | `lat_ces/scientific/quantity` + equations | quantity/equation paths | MERGE |
| 0035 | Hardening verification spec | `lat_ces/scientific/quantity/verification` | tests | MERGE |
| 0036 | Hardening verification | `lat_ces/scientific/quantity/verification` | tests/evidence | KEEP |
| 0037 | Formal derived-unit verification | `lat_ces/smc/verification` | formal invariants | MOVE |
| 0038 | Physical quantity engine | `lat_ces/scientific/quantity` | canonical package | MERGE |
| 0039 | Physical quantity implementation | `lat_ces/scientific/quantity/quantity.py` | actual PhysicalQuantity | KEEP + ADAPT |
| 0040 | Physical quantity verification spec | `lat_ces/scientific/quantity/verification` | quantity tests | MERGE |
| 0041 | Physical quantity verification | `lat_ces/scientific/quantity/verification` | tests/evidence | KEEP |
| 0042 | Physical quantity hardening spec | `lat_ces/scientific/quantity/integrity` | integrity/audit implementation | ADAPT |
| 0043 | Physical quantity hardening implementation | `lat_ces/scientific/quantity/quantity.py` | actual PhysicalQuantity | MERGE |
| 0044 | Hardening verification spec | `lat_ces/scientific/quantity/verification` | tests | MERGE |
| 0045 | Hardening verification | `lat_ces/scientific/quantity/verification` | tests/evidence | KEEP |
| 0046 | Measurement specification | `lat_ces/scientific/measurement.py` | actual measurement implementation/tests | MERGE |
| 0047 | Measurement implementation | `lat_ces/scientific/measurement.py` | actual measurement.py | KEEP + ADAPT |
| 0048 | Measurement verification specification | `lat_ces/scientific/measurement` verification | measurement tests | MERGE |
| 0049 | Measurement verification | `lat_ces/scientific/measurement` verification | measurement evidence | KEEP |
| 0050 | Measurement hardening specification | `lat_ces/scientific/measurement` integrity | measurement/integrity tests | ADAPT |
| 0051 | Measurement hardening implementation | `lat_ces/scientific/measurement.py` | actual measurement.py | ADAPT |
| 0052 | Measurement hardening verification spec | `lat_ces/scientific/measurement` verification | tests | MERGE |
| 0053 | Measurement hardening verification | `lat_ces/scientific/measurement` verification | tests/evidence | KEEP |
| 0054 | Scientific data provenance specification | `lat_ces/scientific/provenance.py` | canonical facade + `gov/provenance.py` storage | MERGE |
| 0055 | Scientific data provenance implementation | `lat_ces/scientific/provenance.py` | ScientificProvenance + legacy ledger adapter | ADAPT |
