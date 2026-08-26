# LAT-CES-0001 — Constitutional Architecture Reference (CAR)

**Document ID:** LAT-CES-0001  
**Title:** Constitutional Architecture Reference (CAR)  
**Revision:** A  
**Classification:** Architecture Foundation  
**Status:** ACCEPTED AS ARCHITECTURAL BASELINE  
**Depends on:** LAT-CES-0000

## 1. Svrha

LAT-CES-0001 je karta sistema. Ne određuje pojedinačnu implementaciju klase ili UI-a; određuje gdje takva implementacija pripada, koji autoritet koristi i kojim tokom dokaza smije raditi.

## 2. Univerzalni sistemski lanac

```text
PHYSICAL REALITY
      ↓
MEASUREMENT & METROLOGY
      ↓
KNOWLEDGE / EVIDENCE
      ↓
MATHEMATICS + PHYSICS
      ↓
LAT CORE
      ↓
DOMAIN MODELS / ADAPTERS
      ↓
ENGINEERING ANALYSIS
      ↓
VERIFICATION / VALIDATION
      ↓
HUMAN ENGINEERING DECISION
```

Korisnički interfejsi su prikaz i kontrola sistema; nisu izvor fizičke istine.

## 3. BuildingModel source of truth

Jedan fizički objekat ima jedan canonical identitet i jedan canonical model.

```text
BuildingModel
├── Level
├── Room
├── Wall
├── Opening
├── Roof
├── Stair
├── Terrace
├── Product / Material identity
├── MEP registry
└── environmental / measurement references
```

Statics, Thermal, MEP, Quantities, Illustrations i Reports čitaju isti validirani BuildingModel. Scientific moduli ne smiju praviti paralelne fizičke kopije `Wall`, `Room`, `Material` ili drugih objekata.

## 4. Four Twin Architecture

LAT-CES koristi četiri međusobno povezana pogleda na stvarnost:

### Human Twin

Znanje, iskustvo, odluke, odgovornost i inženjerska prosudba čovjeka.

### Digital Twin

Canonical building/system model, geometrija, simulacija i izračunati rezultati.

### AI Twin

Analiza, preporuke, optimizacija i pomoć u radu. AI nema ustavni autoritet.

### Knowledge Twin

Dokazi, dokumentacija, konfiguracije, mjerenja, testovi, verifikacije, validacije, odluke, revizije i istorija promjena.

Knowledge Twin je institucionalno pamćenje sistema, a ne drugi fizički simulator.

## 5. Core arhitektura

```text
LAT-CES Core
├── Mathematics Engine
├── Physics Engine
├── Measurement & Metrology Engine
├── Verification Engine
├── Validation Engine
├── Traceability / Lineage Engine
├── Knowledge / Evidence Engine
├── Simulation Engine
├── AI Assistant Engine
└── Domain Adapter Interface
```

Domenski sistemi koriste Core i ne mijenjaju njegov ustavni autoritet.

## 6. Domain Architecture

Primjeri domena:

```text
LAT-BUILDING
LAT-STRUCT
LAT-THERMO
LAT-FLUID
LAT-HVAC / LAT-MEP
LAT-ELECTRIC
LAT-ENERGY
LAT-ACOUSTICS
LAT-ROBOTICS
...
```

Domenski adapteri čitaju canonical podatke i vraćaju provjerljive rezultate, bez stvaranja drugog source-of-truth modela.

## 7. Product / Material architecture

```text
Product
   ↓
Material / engineering properties
   ↓
Canonical element binding
   ↓
Engineering views
```

Product identitet mora imati provenance i status podataka. Primjenjivost proizvoda mora zavisiti od tipa target elementa; npr. Window Product ne smije biti validan za `HeatingZone`.

Vrijednosti koje nisu verificirane moraju ostati `INPUT_REQUIRED` ili drugi eksplicitni status, a ne postati lažne činjenice.

## 8. MEP architecture

MEP je stručni sloj nad BuildingModelom, a ne drugo građevinsko okruženje.

```text
BuildingModel
   ↓
MEP Registry
├── Heating
├── Cooling
├── Ventilation
└── Water
```

MEP editor preuzima etaže, prostorije, zidove, prozore, ploče, slojeve i ostalu geometriju iz BuildingModela. U MEP editoru se projektuju sistemi, ne crtaju novi zidovi ili krovovi.

## 9. Measurement / Nature integration

Lokacija objekta povezuje model sa vanjskim fizičkim okruženjem kroz provjerene izvore i lokalna mjerenja.

```text
Location
  ↓
meteorological / environmental evidence
  ↓
BuildingModel context
  ↓
calculations
  ↓
real sensors
  ↓
model ↔ measurement validation
```

Vanjski podatak i lokalno mjerenje moraju zadržati različit provenance. Model ne smije predstavljati vanjski dataset kao direktno mjerenje na parceli.

## 10. Authority and evidence flow

```text
Nature
  > Measurement
  > Mathematics
  > Natural laws
  > Engineering science
  > LAT Core
  > Domain modules
  > AI Assistant
  > UI
```

Svaki rezultat mora biti moguće pratiti do ulaza, metode, izvora, identiteta modela i, kada je primjenjivo, mjerenja.

## 11. Quality gates

Svaka značajna razvojna promjena prolazi:

```text
Code / model validation
      ↓
Verification
      ↓
Windows / packaging validation when applicable
      ↓
GUI / functional acceptance when applicable
      ↓
Human engineering acceptance
```

CI GREEN nije zamjena za fizičku validaciju niti za odgovornu inženjersku odluku.

## 12. Architectural invariants

1. Jedan fizički objekat → jedan identitet → jedan canonical model.
2. Scientific views su read-only pogledi ili kontrolisani izvedeni rezultati; ne postaju novi fizički source of truth.
3. Nedostajući podaci ostaju eksplicitno označeni.
4. AI nema autoritet iznad dokaza i nauke.
5. Mjerenje i izračunati rezultat imaju različit provenance.
6. Adaptacija modela mora ostaviti sljediv trag.

## 13. Odnos prema implementaciji

Implementacija smije evoluirati. Ovaj dokument ostaje arhitektonska referenca, a konkretne Python klase, paketi i GUI mogu se mijenjati ako ostanu kompatibilni sa ustavnim principima i architectural invariants.
