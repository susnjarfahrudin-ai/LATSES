# CIAC CAP Evidence Audit — MAIN(5)

**Status:** Evidence / architectural guidance only  
**Scope:** Current `main` runtime state  
**Audited base:** `2f6792fcbbc349e8cdf706eb7cd97119605865ad`  
**CIAC runtime implementation:** NOT IMPLEMENTED  
**Production runtime changes:** NONE

## 1. Audit definition

> **CAP = posljednja dokaziva runtime tačka na kojoj konkretna Property Instance može neposredno uticati na matematički proračun ili solver.**

Samo postojanje klase, validacije, adaptera, registry-ja ili verification gate-a nije CAP dokaz.

CAP se prihvata kao **PROVEN** samo kada je dokaziv stvarni runtime lanac:

`caller → property → transformation/formula → calculation/result`

Ako takav lanac nije dokazan, CAP je **UNKNOWN**.

## 2. Evidence rules

Ovaj dokument ne implementira CIAC i ne proglašava buduću canonical authority granicu. Njegova svrha je da dokumentuje trenutno stanje i tačno pokaže gdje CIAC trenutno nije dokaziv.

Za svaki property odvojeno se ispituje:

1. stvarni consumer;
2. posljednja tačka prije matematičkog uticaja (CAP);
3. kontrola prije CAP-a;
4. admission;
5. reconciliation;
6. property-level lineage;
7. alternativni ili direktni bypass putevi.

Statusi CAP-a:

- **PROVEN** — konkretna računska putanja je dokazana;
- **UNKNOWN** — consumer/calculation path nije dokazan.

Statusi CIAC-a:

- **PRESENT** — relevantni CIAC zahtjevi su dokazivi na stvarnom authority boundaryju;
- **PARTIAL** — dio zahtjeva postoji, ali authority nije kompletno dokazan;
- **GAP** — stvarni CAP postoji, ali potrebna CIAC kontrola/admission/lineage nije dokazana;
- **BYPASS** — dokaziv direktni put postoji mimo zahtijevanog authority boundaryja.

`MULTIPLE CAPs` ili `PARALLEL PATHS` nisu sami po sebi isto što i `BYPASS`; bypass se koristi kada postoji konkretan put koji zaobilazi utvrđeni authority boundary.

## 3. CAP Evidence Matrix v0.2

| Property | Stvarni CAP | Dokaz CAP-a | Kontrola prije CAP-a? | Admission? | Reconciliation? | Lineage? | CIAC stanje |
|---|---|---|---|---|---|---|---|
| `density` | **PROVEN, MULTIPLE** | `ConstructionLayer.density → LoadLedger → load_kn_m2`; `RoofLayer.density → RoofLoadModel → RoofLoadResult` | PARTIAL / nije zajednička kontrola | NOT PROVEN | NOT PROVEN | Object-level postoji; property-level nije zatvoren | **GAP / PARALLEL PATHS** |
| `thermal_conductivity` | **PROVEN** | `Material.thermal_conductivity → R → U → Q → EngineeringResult` | Validation PROVEN; zajednički authority boundary nije dokazan | NOT PROVEN | NOT PROVEN | Property-level lineage nije zatvoren | **PARTIAL / ALTERNATIVE PATH** |
| `youngs_modulus` | **PROVEN** | `SimplySupportedBeamInput.youngs_modulus_pa → BeamSolver → BeamSolverResult` | Solver input validation postoji | NOT PROVEN | NOT PROVEN | Material→solver property lineage nije dokazan | **BYPASS — DIRECT SOLVER INPUT** |
| `compressive_strength_mpa` | **UNKNOWN** | Nema dokazanog production consumer-a | N/A | N/A | N/A | N/A | **GAP / STORED ONLY** |
| `dead_load_kpa` | **UNKNOWN** za `Roof.dead_load_kpa` | Nema dokazanog consumer-a za konkretni property | Local validation postoji | NOT PROVEN | N/A | N/A | **GAP / PARALLEL REPRESENTATION** |
| `snow_load_kpa` | **UNKNOWN** | Nema dokazanog unified structural calculation path-a | Partial verification/evidence controls postoje | NOT PROVEN | NOT PROVEN | Nije zatvoren | **GAP / PARALLEL REPRESENTATIONS** |
| `thickness` | **PROVEN, MULTIPLE** | `RoofLayer.thickness_m → RoofLoadModel`; `ConstructionLayer.thickness_m → LoadLedger` | Local validation po representationu | NOT PROVEN | NOT PROVEN | Property-level lineage nije zajednički | **GAP / MULTIPLE CAPs** |
| `surface_mass` | **PROVEN, MULTIPLE** | `ConstructionLayer.mass_kg_m2 → load_kn_m2`; `RoofLayer.mass_kg_m2 → dead_load_kn_m2` | Local/domain validation | NOT PROVEN | NOT PROVEN | Property-level lineage nije zatvoren | **GAP / MULTIPLE PATHS** |
| `snow_ground_characteristic` | **UNKNOWN** za structural calculation | `EnvironmentalFact → SiteVerificationGate → EnvironmentalLoadSnapshot`; nema dokazanog mathematical consumer-a | Verification gate PROVEN | NOT PROVEN | NOT PROVEN | Evidence/object path postoji; engineering lineage nije zatvoren | **GAP / EVIDENCE PATH ONLY** |

## 4. Detailed findings

### 4.1 `density`

`Material.density` postoji u `BuildingModel.materials`, ali nije dokazana transformacija iz tog property-ja prema structural consumeru.

Dva nezavisna računska puta su dokaziva:

```text
ConstructionLayer.density
    ↓
ConstructionAssembly
    ↓
LoadLedger
    ↓
load_kn_m2
```

```text
RoofLayer.density
    ↓
RoofLoadModel
    ↓
RoofLoadResult
```

Zaključak: **CAP PROVEN, MULTIPLE** za domain representations. `Material.density → structural calculation` ostaje **UNKNOWN**. Nije dokaziv jedan zajednički CAP. Postoje paralelni računski putevi.

### 4.2 `thermal_conductivity`

Dokazan je vertikalni consumer path:

```text
Material
    ↓
BuildingModel.materials
    ↓
Wall.material_id
    ↓
calculate_wall_thermal_result()
    ↓
R = Rsi + d/λ + Rse
    ↓
U = 1/R
    ↓
Q = U × A × ΔT
    ↓
EngineeringResult
    ↓
Report
```

CAP je **PROVEN** na consumer/calculation boundaryju. Poznat je i alternativni thermal API koji može raditi sa već dostupnim veličinama mimo ovog `Material` puta.

Zaključak: stvarni consumer postoji, ali nije dokazano da je ovaj path jedini authority path za fizičku veličinu.

### 4.3 `youngs_modulus`

`Material.youngs_modulus` je validiran i pohranjen, ali nije dokazana veza prema solver inputu.

Dokazan je direktan solver path:

```text
SimplySupportedBeamInput.youngs_modulus_pa
    ↓
BeamSolver
    ↓
BeamSolverResult
```

Solver direktno koristi `youngs_modulus_pa` u matematičkom proračunu. To je **CAP PROVEN**.

Zaključak: **DIRECT SOLVER BYPASS PROVEN**. Postojanje `Material.youngs_modulus` nije dokaz runtime authorityja.

### 4.4 `compressive_strength_mpa`

Property postoji i ima lokalnu validaciju, ali nije dokazan production consumer, formula, structural transformation ili engineering result koji zavisi od njega.

CAP: **UNKNOWN**.

Zaključak: **STORED ONLY / NO PROVEN CONSUMER**. Ovo nije dokaz bypassa.

### 4.5 `dead_load_kpa`

`Roof.dead_load_kpa` postoji, validira se i pohranjuje, ali nije dokazan consumer koji ga koristi u `RoofLoadModel`.

`RoofLoadModel` umjesto toga koristi `RoofLayer[]` i iz njih računa:

```text
RoofLayer density/thickness or mass
    ↓
mass_kg_m2
    ↓
dead_load_kn_m2
    ↓
RoofLoadModel
    ↓
RoofLoadResult
```

Zaključak: CAP za konkretni `Roof.dead_load_kpa` je **UNKNOWN**. Paralelna representation je **PROVEN**.

### 4.6 `snow_load_kpa`

Postoje najmanje tri relevantne representations:

```text
Roof.snow_load_kpa
StructuralLoadInput.snow_kN_m2
EnvironmentalFact.snow_ground_characteristic
```

Za `EnvironmentalFact.snow_ground_characteristic` dokazan je:

```text
EnvironmentalFact
    ↓
SiteVerificationGate
    ↓
EnvironmentalLoadSnapshot
```

Ali nije dokazan kompletan structural calculation chain:

```text
snow_ground_characteristic
    ↓
snow design calculation
    ↓
roof snow load
    ↓
StructuralLoadInput.snow_kN_m2
    ↓
solver
```

Zaključak: nema dokazanog unified CAP-a. Postoje paralelne representations, ali structural consumer chain nije zatvoren.

### 4.7 `thickness`

Dva računski aktivna puta su dokazana:

```text
RoofLayer.thickness_m + density_kg_m3
    ↓
mass_kg_m2
    ↓
dead_load_kn_m2
    ↓
RoofLoadModel
```

```text
ConstructionLayer.thickness_m + density_kg_m3
    ↓
mass_kg_m2
    ↓
load_kn_m2
    ↓
LoadLedger
```

CAP: **PROVEN, MULTIPLE**. Nije dokazana zajednička authority tačka niti CIAC admission boundary.

### 4.8 `surface_mass`

`ConstructionLayer.mass_kg_m2` može biti deklarisana surface mass, a može nastati iz `density × thickness`; zatim direktno ulazi u load calculation.

`RoofLayer.mass_kg_m2` takođe predstavlja alternativni ulaz prema `dead_load_kn_m2`.

Dokazani putevi:

```text
ConstructionLayer.mass_kg_m2
    ↓
load_kn_m2
    ↓
LoadLedger
```

```text
RoofLayer.mass_kg_m2
    ↓
dead_load_kn_m2
    ↓
RoofLoadModel
```

CAP: **PROVEN, MULTIPLE**. Nije dokazana zajednička CIAC authority tačka.

### 4.9 `snow_ground_characteristic`

Verification/evidence path je stvaran:

```text
EnvironmentalFact
    ↓
snow_ground_characteristic
    ↓
SiteVerificationGate
    ↓
EnvironmentalLoadSnapshot
```

Gate i immutable snapshot nisu CAP dokaz. Nije pronađen dokaz da snapshot zatim ulazi u structural snow formula/solver chain.

CAP: **UNKNOWN** za structural calculation.

Zaključak: **EVIDENCE/SNAPSHOT PATH PROVEN — ENGINEERING CAP NOT PROVEN**.

## 5. What this audit proves

MAIN(5) pokazuje tri osnovne klase stanja:

### A — Property stvarno dolazi do računanja

- `thermal_conductivity`
- `thickness`
- `surface_mass`
- `density` kroz `RoofLayer` / `ConstructionLayer`

### B — Property postoji, ali drugi runtime representation ima odvojeni calculation path

- `Material.density`
- `Material.youngs_modulus`
- `Roof.dead_load_kpa`
- `Roof.snow_load_kpa`
- `StructuralLoadInput.snow_kN_m2`

### C — Property/evidence postoji, ali engineering consumer nije dokazan

- `compressive_strength_mpa`
- `snow_ground_characteristic` za structural calculation

## 6. CIAC gap statement

Ovaj audit ne zaključuje da CIAC treba biti implementiran na određenoj klasi ili funkciji. Zaključuje samo ono što je dokazivo:

1. CAP može biti stvaran i bez CIAC admissiona.
2. Adapter, validator, registry i verification gate nisu automatski authority boundary.
3. Višestruki CAP-ovi mogu postojati za isto fizičko svojstvo.
4. Property može postojati u `Material` representationu bez dokazane runtime veze prema calculation consumeru.
5. Direct solver input može predstavljati stvarni bypass ako nije obuhvaćen admission boundaryjem.
6. Object-level lineage ne zatvara automatski property-level lineage.
7. `CAP UNKNOWN` znači da consumer/calculation path nije dokazan; ne znači automatski bypass.

## 7. Boundary of this document

**Nema production code changes.**

Ovaj dokument ne:

- implementira CIAC runtime;
- uvodi nove klase/API-je/dekoratore/middleware;
- mijenja solver inpute;
- mijenja `Material`, `RoofLayer`, `ConstructionLayer` ili thermal/structural calculators;
- uvodi reconciliation ponašanje;
- uvodi admission enforcement;
- proglašava `main` canonical input authorityjem.

Dokument predstavlja **evidence baseline i smjernicu za naredni CIAC runtime design**.

## 8. Required next phase

Tek nakon review-a ovog dokaznog artefakta može se definirati CIAC runtime contract na osnovu stvarno dokazanih gapova.

Redoslijed ostaje:

```text
CURRENT MAIN
    ↓
CAP EVIDENCE
    ↓
BYPASS EVIDENCE
    ↓
CIAC GAP
    ↓
CIAC RUNTIME CONTRACT
    ↓
IMPLEMENTATION
```

**Ne preskakati dokazni sloj.**
