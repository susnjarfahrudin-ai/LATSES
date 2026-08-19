# LATCES — MASTER INTERFACE / FUNCTIONAL CODEX

**Status:** Master functional specification  
**Purpose:** Define the single-object engineering interface that connects drafting, geometry, physical properties, measurements, engineering analyses, serviceability and AI assistance.

## 1. Core principle

**Draw once → model once → measure reality → calculate → optimize → recommend → human decides.**

LATCES must not be a collection of disconnected calculators. One Building Model is the source for:

- floor plans
- elevations and sections
- 3D
- walls, openings and construction
- materials and quantities
- mass
- airflow
- water and drainage
- heating/cooling
- electrical systems
- daylight
- solar
- structural analysis
- acoustics
- energy
- serviceability
- maintenance/warranty
- AI recommendations.

## 2. Information hierarchy

**NATURE → SCIENCE + MATHEMATICS + MEASUREMENTS + RULES → AI RESEARCH → LATCES MODEL → ENGINEERING ANALYSIS → OPTIMIZATION → AI RECOMMENDATION → HUMAN DECISION**

AI never overrides the scientific model, rules, measured evidence or human approval.

## 3. Main interface

Top-level areas:

1. PROJECT
2. BUILDING MODEL
3. DRAFTING
4. 3D / SECTIONS
5. MATERIALS & QUANTITIES
6. AIR
7. WATER
8. HEATING / COOLING
9. ELECTRICAL
10. DAYLIGHT
11. SOLAR
12. STRUCTURE
13. ENERGY
14. ACOUSTICS
15. SERVICE
16. MEASUREMENTS / SENSORS
17. EVIDENCE / SOURCES
18. AI ASSISTANT
19. OPTIMIZATION
20. VALIDATION

The central workspace provides **PLAN / SECTION / 3D** views of the same geometry.

## 4. Building Model

The building is composed of independently defined storeys. Storeys do not have to share dimensions.

Example:

- Ground floor: 10 × 10 m
- First floor: 10 × 8 m
- Second floor: 10 × 8 m
- Roof: 10 × 10 m
- Storey height: user-defined

Each storey contains rooms, walls, openings, slabs, ceilings, installations and physical properties.

## 5. Drafting model

### Room

Inputs:
- length
- width
- height
- name
- use
- material/finish

Interactive behaviour:
- preview follows cursor
- live dimensions
- snap
- click to place
- dimensions remain editable.

### Partition wall

Inputs:
- length
- thickness
- height
- material

The wall is a real geometric object, not a drawing line.

### Door

Inputs:
- width
- height
- type
- opening direction
- wall attachment

The door snaps to a wall. Its opening modifies the wall geometry.

### Window

Inputs:
- width
- height
- sill/parapet height
- type
- wall attachment

The window is also a true opening in the wall.

## 6. Wall/opening geometric rule

If storey height is **2.80 m** and a door is **0.90 × 2.10 m**:

- `z = 0.00–2.10 m`: opening
- `z = 2.10–2.80 m`: wall continues

For a window, the opening starts at its sill height and ends at sill + window height.

The same geometry must drive:

- plan
- section
- 3D
- material quantities
- thermal calculations
- daylight calculations
- structural analysis where applicable.

## 7. Graphic standard

The 3D model should distinguish:

- masonry/brick
- concrete
- timber
- glass
- metal/sheet metal
- insulation
- roofing
- floor finishes
- doors/windows
- installations.

Materials must be linked to actual model materials rather than decorative-only colours.

## 8. Airflow through space — priority module

The airflow model is spatial and dynamic rather than a single room ACH number.

System chain:

**outside air → filter → recovery/heat exchanger → heating/cooling coil → plenum → room → exhaust → recovery → outside**

Calculate:

- volume flow
- local velocity
- pressure
- pressure loss
- temperature
- humidity
- buoyancy
- turbulence
- directionality
- distribution
- occupied-zone conditions.

### Occupied zone

Special attention to approximately **0.70–1.70 m** above floor level.

Design objective is very low perceptible air movement, with the user's proposed target range around **0.02–0.05 m/s** where physically achievable and verified by calculation/measurement. This is a design target, not a universal safety guarantee.

Airflow must be analysed as multiple distributed sources, not as one uniform velocity.

## 9. Passive ventilation

Support passive inlet and exhaust configurations.

Inputs:

- opening area
- opening height
- indoor/outdoor temperature
- vertical separation
- wind
- resistance
- geometry

Calculate buoyancy-driven flow and expected velocity. Clearly distinguish calculated estimates from measured performance.

## 10. Winter heat recovery

Preferred conceptual chain:

**outside air → filter → water preheater/dogrijač → metal heat exchanger → plenum → room**

Return air flows through the recovery exchanger before leaving the building.

Calculate:

- recovered heat
- supply temperature
- return temperature
- condensation
- freezing risk
- pressure loss
- required exchanger area
- required heating power.

## 11. Summer fresh-air cooling

The cooling concept is not a mini split replacing fresh air.

Fresh outside air remains the ventilation air. A water circuit can cool that fresh air through an air/water heat exchanger with condensate drainage.

Possible system:

**outside air → filter → water coil → condensate drain → plenum → room**

A refrigeration source may cool the water reservoir. Electrical input power must never be confused with useful cooling capacity; calculate COP/EER under the actual operating conditions.

## 12. Indoor air quality

Track:

- CO₂
- VOC
- formaldehyde/HCHO
- PM1/PM2.5/PM10 where available
- temperature
- relative humidity.

Each value carries provenance: measured, declared, calculated, simulated or unknown.

## 13. Water — life-critical subsystem

Water is a first-class Building Model subsystem.

Hydraulics:

- flow
- pressure
- pipe diameter
- velocity
- pressure losses
- pump
- circulation
- storage
- temperature.

### Water quality

Track, where supported by appropriate measurement/testing:

- temperature
- pH
- conductivity
- turbidity
- disinfectant residual
- stagnation/time-at-temperature
- microbiological test results
- microbiological risk indicators.

LATCES must not claim microbiological safety from an unvalidated consumer sensor or from calculations alone. Laboratory or appropriately validated measurements remain the authority for health-critical microbiological conclusions.

## 14. Drainage

Model:

- pipe diameter
- slope
- flow
- velocity
- fittings
- pressure/flow losses
- venting
- traps
- inspection points
- service access.

LATCES can compare alternatives such as **2 × 45° vs 1 × 90°**, but must calculate whether the proposed geometry actually reduces resistance for the specific system.

## 15. Heating

Supported heating concepts:

- underfloor
- radiators
- wall heating
- ceiling heating
- convectors
- air heating
- hybrid systems
- other validated technologies.

From the building model calculate room heat loss, required capacity, distribution requirements and comfort implications.

## 16. Cooling

Calculate cooling load from:

- solar gains
- transmission
- glazing
- ventilation
- occupants
- equipment
- shading
- thermal mass.

## 17. Electrical

Model:

- lighting
- outlets
- appliances
- high-load equipment
- distribution
- protection
- connected load
- peak load
- energy use.

## 18. Daylight

For every relevant opening:

- orientation
- area
- height
- position
- shading
- glazing properties.

Estimate spatial daylight availability and flag inadequate or excessive exposure. Distinguish simplified estimates from validated daylight simulation.

## 19. Solar

Model:

- roof geometry
- orientation
- pitch
- shading
- usable area
- panels
- production
- battery
- self-consumption.

## 20. Structural model

Use the same geometry for:

- walls
- slabs
- beams
- columns
- roof.

Inputs include material properties, mass, permanent actions, imposed loads, snow, wind and other applicable actions. Structural results must identify the applicable calculation assumptions and code basis.

## 21. Materials

Each material record may contain:

- density
- thermal conductivity
- heat capacity
- strength parameters
- acoustic properties
- emissions
- durability
- fire properties
- cost
- manufacturer/source
- evidence status.

## 22. Health/material emissions

Track:

- formaldehyde
- VOC
- emission class
- adhesives
- coatings
- insulation emissions.

Separate:

- manufacturer declaration
- independent certification
- actual measurement.

## 23. Quantities and mass

Automatically derive from geometry:

- length
- area
- volume
- mass
- count.

Produce material takeoffs and an estimated object mass.

## 24. Energy

Unified balance:

**heating + cooling + ventilation + water + electricity − solar generation = net energy balance**

Use actual system efficiencies and operating conditions rather than nominal labels alone.

## 25. Acoustics

Track:

- fan noise
- air velocity
- ducts
- grilles
- pressure losses
- vibration
- structure-borne transmission
- room-to-room transmission.

Low-velocity airflow is treated as a comfort/noise design objective, not simply a visual setting.

## 26. Serviceability

Every significant equipment object should carry:

- location
- service clearance
- access route
- maintenance interval
- warranty
- service provider
- spare parts
- installation date
- expected service life.

LATCES should explicitly ask: **Can a human actually reach, remove, inspect and replace this component?**

## 27. Warranty and service assistant

AI may monitor:

- warranty expiration
- maintenance dates
- service requirements
- replacement parts
- service contacts.

AI may prepare service requests, e-mails and notifications, but sending external communications requires human approval.

## 28. Measurement and sensor registry

Every measurement should record:

- instrument
- manufacturer
- model
- serial number when available
- sensor type
- range
- accuracy
- resolution
- calibration
- calibration date
- location
- installation method
- timestamp
- environmental conditions.

Sensor categories:

- INDUSTRIAL / PROFESSIONAL
- ENGINEERING / COMMERCIAL
- CONSUMER
- EXPERIMENTAL

Country of origin is not a quality criterion. Evidence of accuracy, stability, calibration, durability and repeatability is.

## 29. Evidence model

Every external technical claim receives one of:

- **DECLARED** — manufacturer/seller statement
- **VERIFIED** — independently verified
- **MEASURED** — actual measurement
- **CALCULATED** — mathematical result
- **SIMULATED** — model result
- **USER EXPERIENCE** — real-world feedback
- **AI RESEARCH** — information located by AI and awaiting validation
- **UNKNOWN** — insufficient evidence.

AI must never silently upgrade a declared value into a verified fact.

## 30. AI research

AI may research:

- technical datasheets
- scientific papers
- standards and regulations
- certificates
- products
- service providers
- replacement parts
- costs
- real-world user feedback.

Research outputs are stored with source, date, subject, relevance and evidence status.

## 31. Real-world experience

AI may analyse user reports for fans, sensors, pumps, heat exchangers, filters, controls, heating equipment and other components.

Extract recurring signals for:

- noise
- vibration
- failures
- service quality
- durability
- control behaviour
- long-term satisfaction.

User experience is valuable evidence for product selection, but it is not a substitute for laboratory measurement.

## 32. AI engineering assistant

AI is an **engineering assistant**, not the project owner.

Example:

> Recommendation: move the supply plenum 0.40 m north.
>
> Why: lower occupied-zone velocity, lower ΔP, shorter duct, fewer fittings, improved service access.

The user can:

**ACCEPT / REJECT / MODIFY**

AI can also organise research into project folders, prepare documentation, track service tasks and draft communications. Human approval remains the decision boundary for project changes and external actions.

## 33. Optimization engine

Optimize for:

- comfort
- air quality
- water quality/risk
- energy
- noise
- pressure loss
- material quantity
- cost
- serviceability
- durability
- safety.

LATCES should compare alternatives rather than blindly select a single answer.

## 34. Validation

Every segment receives an explicit state:

- **PASS** — verified by a relevant test/measurement
- **PARTIAL** — partly implemented or verified
- **FAIL** — test failed
- **NOT IMPLEMENTED** — missing implementation
- **UNKNOWN** — insufficient evidence.

The GUI appearance is never evidence of functional completion.

## 35. Final dashboard

Example:

| Segment | Status |
|---|---|
| Geometry | PASS / PARTIAL |
| Drafting | PASS / PARTIAL |
| Wall/Openings | PASS / PARTIAL |
| 3D | PASS / PARTIAL |
| Sections | PASS / PARTIAL |
| Airflow | PASS / PARTIAL |
| IAQ | PASS / PARTIAL |
| Water | PASS / PARTIAL |
| Water Quality | UNKNOWN / PARTIAL |
| Heating | PASS / PARTIAL |
| Cooling | PASS / PARTIAL |
| Electrical | PASS / PARTIAL |
| Daylight | PASS / PARTIAL |
| Solar | PASS / PARTIAL |
| Structure | PASS / PARTIAL |
| Energy | PASS / PARTIAL |
| Acoustics | PASS / PARTIAL |
| Materials | PASS / PARTIAL |
| Serviceability | PASS / PARTIAL |
| Sensors | PASS / PARTIAL |
| Evidence | PASS / PARTIAL |
| AI Assistant | PASS / PARTIAL |
| Optimization | PASS / PARTIAL |

## 36. Required logical modules

1. BuildingModelCore
2. GeometryKernel
3. DraftingEngine
4. WallOpeningEngine
5. SectionEngine
6. ThreeDEngine
7. MaterialQuantityEngine
8. AirflowEngine
9. PassiveVentilationEngine
10. HeatRecoveryEngine
11. FreshAirCoolingEngine
12. WaterHydraulicEngine
13. WaterQualityRiskEngine
14. DrainageEngine
15. HeatingEngine
16. CoolingLoadEngine
17. ElectricalEngine
18. DaylightEngine
19. SolarEngine
20. StructuralAnalysisLayer
21. ThermalEnergyEngine
22. AcousticEngine
23. MeasurementRegistry
24. SensorEvidenceRegistry
25. SourceEvidenceRegistry
26. RealWorldExperienceEngine
27. ServiceabilityEngine
28. WarrantyMaintenanceEngine
29. OptimizationEngine
30. AIResearchLayer
31. AIEngineeringAdvisor
32. AIRecommendationEngine
33. ValidationEngine
34. ReportingEngine

## 37. Implementation rule

This document is a functional specification, not a claim that every item already exists in the current codebase.

A feature becomes complete only after:

**IMPLEMENTATION → UNIT/INTEGRATION TEST → GUI TEST → PHYSICAL/NUMERICAL VALIDATION WHERE APPLICABLE → PASS**.

The final architecture must keep GUI, Building Model, Scientific Model, calculations, 2D, 3D, sections, quantities, systems and AI tied to the same authoritative object model.
