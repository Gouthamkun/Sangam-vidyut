# PHASE 4D: INDIA DATA ACQUISITION & CALIBRATION SPECIFICATION

## 1. OBJECTIVE
This specification designs the data foundation required to transform Sangam Vidyut from a controlled/synthetic Agent-Based Model (ABM) into a calibrated residential solar adoption model for India. It establishes a rigorous pipeline for acquiring, harmonizing, and validating official Indian data to parameterize households, grid context, and economic environments without corrupting the ABM logic.

**CRITICAL RULES:**
- No datasets are downloaded into the repository yet.
- The ABM mathematical parameters and weights are not modified.
- No dataset is fabricated.
- Official/Primary sources (MNRE, CEA, NSSO, CERC) take absolute precedence.

## 2. DATA DOMAINS
The specification encompasses:
A. HOUSEHOLD DEMOGRAPHICS
B. HOUSEHOLD ECONOMICS
C. ELECTRICITY / ENERGY USE
D. RESIDENTIAL SOLAR ADOPTION
E. SOLAR SYSTEM COSTS
F. GOVERNMENT SUBSIDY / POLICY
G. ELECTRICITY TARIFFS
H. SOLAR RESOURCE / GEOGRAPHY
I. GRID EMISSIONS
J. SOCIAL / NETWORK PROXIES
K. TECHNOLOGY / PRICE LEARNING
L. VALIDATION / GROUND-TRUTH SOURCES

## 3. HOUSEHOLD DATA (Demographics, Economics, Energy Use)
**Official Indian Sources:**
1. **NSSO (National Sample Survey Office):** Consumer Expenditure Survey (CES), latest available round.
2. **NFHS-5 (National Family Health Survey):** For housing type, durable goods, electricity access, household size.
3. **PLFS (Periodic Labour Force Survey):** For employment/occupation.
4. **CEEW ACCESS Survey:** For electricity reliability and detailed rural/urban energy access.

**Variables to Acquire:**
- *Income Proxy:* Monthly Per Capita Consumption Expenditure (MPCE) from NSSO. Income is notoriously under-reported; MPCE is the official proxy.
- *Dwelling/Tenure:* NFHS-5 "Own/Rent" and "Kachha/Pucca" status (proxies roof suitability).
- *Electricity Expenditure:* NSSO or CEEW ACCESS.
- *Resolution:* State level and Urban/Rural segmentation.

## 4. SOLAR ADOPTION DATA
**Authoritative Historical Sources:**
- **MNRE (Ministry of New and Renewable Energy):** Annual Reports, State-wise Rooftop Solar Installations.
- **National Portal for Rooftop Solar (PM Surya Ghar):** Dashboards for recent residential registrations.

**Distinctions:**
- *Installed Capacity (MW):* Often aggregates C&I (Commercial & Industrial) and Residential. Must be carefully parsed.
- *Number of Installations:* Pure count of residential systems.
- *Household Adoption Rate:* Installations divided by total eligible households in the state.

*Note:* MNRE State-wise data provides capacity, but often lumps sectors. Residential-specific disaggregation requires MNRE benchmark reports or PM Surya Ghar portal extraction.

## 5. SOLAR COST DATA
**Authoritative Sources:**
- **MNRE Benchmark Costs:** Officially published annually/biannually dictating subsidy calculation baselines.
- **CERC (Central Electricity Regulatory Commission):** Tariff orders often contain capital cost benchmarks.

**Variables:**
- Rooftop PV system price (₹/kWp).
- Inverter/BOS cost breakdown.
- *Model Mapping:* The current `config.industry.base_price` (₹5000 in synth runs) must eventually map to the MNRE benchmark cost per kW for a standard 3kW system.

## 6. GOVERNMENT POLICY / SUBSIDY DATA
**Authoritative Sources:**
- **PM Surya Ghar: Muft Bijli Yojana:** Official guidelines.
- **MNRE Phase II Rooftop Solar Programme:** Historical subsidy guidelines.

*Schema Example:* (See `DATA_DICTIONARY.md`)
Includes subsidy amounts (e.g., ₹30,000 per kW up to 2kW), capacity limits, and effective dates.

## 7. ELECTRICITY TARIFF DATA
**Authoritative Sources:**
- **SERC (State Electricity Regulatory Commission):** Annual Tariff Orders.
- **PFC (Power Finance Corporation):** "Report on Performance of State Power Utilities".

**Variables:**
- Fixed Charges (₹/kW/month).
- Energy Charges (₹/kWh by consumption slab).
- Effective rate.
*Usage:* Used to calculate payback/affordability heterogeneously across states.

## 8. SOLAR RESOURCE / REGIONAL DATA
**Authoritative Sources:**
- **NISE (National Institute of Solar Energy):** State-wise solar potential reports.
- **Global Solar Atlas / NREL NSRDB India:** Spatial irradiation.

**Variables:** Global Horizontal Irradiance (GHI), Specific Yield (kWh/kWp). Spatially resolved to state/district to adjust effective yield and payback.

## 9. EMISSIONS / ENVIRONMENT DATA
**Authoritative Sources:**
- **CEA (Central Electricity Authority):** CO2 Baseline Database for the Indian Power Sector (Version 21.0 or latest).

**Variables:**
- Grid Emission Factor (tCO2/MWh).
*Usage:* `EnvironmentAgent` converts avoided grid consumption into emissions saved.

## 10. SOCIAL NETWORK DATA
**OBSERVED NETWORK DATA:** Not directly available at household-to-household resolution in India.
**MODELED NETWORK CONSTRUCTION:**
- *Spatial Proximity Proxy:* Use Census Ward data or NSSO cluster sampling framework to define "neighborhoods".
- *Socioeconomic Similarity:* Use MPCE deciles.
- *Approach:* We will construct the modeled network by generating sub-graphs for each district/ward, connecting agents using a Watts-Strogatz or Barabasi-Albert topology constrained by physical geography and socioeconomic homophily.

## 11. HOUSEHOLD PERSONA GENERATION
**CRITICAL:** The LLM must NOT invent the underlying population distribution.

**Pipeline:**
Official Data (NSSO/NFHS) → Cleaning → Statistical Sampling (KDE/Copulas) → Synthetic Household Population → ConsumerAgent instantiation.

**ConsumerAgent Persona Fields:**
- `state`
- `urban_rural`
- `household_size`
- `mpce_decile` (Income proxy)
- `home_owner` (Tenure proxy)
- `roof_suitability` (Kachha/Pucca proxy)
- `electricity_slab`
- `subsidy_eligibility`

## 12. CALIBRATION TARGETS
See `docs/data/CALIBRATION_PLAN.md`.

## 13. DATA QUALITY & PROVENANCE
See `docs/data/DATA_PROVENANCE_SCHEMA.md`.

## 14. DATA DIRECTORY DESIGN
When implemented, the repository will use:
```text
data/
├── raw/          # Immutable original downloads (e.g., MNRE PDFs, NSSO CSVs)
├── external/     # Third-party mappings or crosswalks
├── interim/      # Partially cleaned/joined data
├── processed/    # Final ML-ready / ABM-ready inputs
├── calibration/  # Target arrays for loss functions
├── metadata/     # Provenance tracking JSONs
└── validation/   # Holdout data for counterfactual testing
```

## 15. DATASET PRIORITIZATION
**P0 (Minimum Viable Calibration):**
1. NSSO CES (Income proxy)
2. MNRE Benchmark Costs (Costs)
3. PM Surya Ghar Guidelines (Subsidy)
4. MNRE State-wise Residential Installations (Adoption target)

**P1 (Research Grade):**
1. SERC Tariff Slabs
2. NISE Solar Yield
3. CEA CO2 Baseline

**P2/P3 (Extensions):**
1. CEEW ACCESS (Granular reliability)
2. High-resolution satellite rooftop extraction.

## 16. DATA GAPS
1. **True Household Income:** Unavailable. *Requires Proxy (MPCE).*
2. **Direct Peer Networks:** Unavailable. *Requires Synthetic Construction (Spatial proximity).*
3. **Residential-Only Historical Adoption:** Often merged with C&I in older MNRE reports. *Requires expert assumption/disaggregation ratios.*

## 17. IDENTIFY OFFICIAL SOURCES
Primary reliance is on MoSPI/NSSO, MNRE, CEA, and SERCs. No generic Kaggle datasets or unverified secondary sources will be used for primary calibration.

## 18. SOURCE VALIDATION (P0)
- **NSSO CES:** EXISTS. ACCESSIBLE (via MoSPI microdata). COVERAGE: All India. PREPROCESSING: Heavy survey weighting required.
- **MNRE Benchmark Costs:** EXISTS. ACCESSIBLE (PDF/Web). COVERAGE: All India. PREPROCESSING: PDF extraction.
- **MNRE Installations:** EXISTS. ACCESSIBLE. PREPROCESSING: Parsing state-level tables.

## 19. MODEL MAPPING TABLE
| Dataset | Variable | Source | Geography | Agent | Model Component | Calibration Role | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| NSSO CES | MPCE | MoSPI | State/UR | ConsumerAgent | Income Proxy | Input Distribution | P0 |
| NFHS-5 | Tenure | MoSPI | District | ConsumerAgent | Home Owner | Input Distribution | P0 |
| PM Surya Ghar | Subsidy | MNRE | National | GovernmentAgent | base_subsidy | Parameter | P0 |
| MNRE Costs | kW Cost | MNRE | National | IndustryAgent | base_price | Parameter | P0 |
| CEA CO2 | Emis. Factor | CEA | Grid | EnvironmentAgent| co2_reduction | Output Metric | P1 |
| MNRE Adopt. | Installations | MNRE | State | AnalysisAgent | final_adoption | Fit Target | P0 |

## 20. CALIBRATION ARCHITECTURE
See `docs/data/CALIBRATION_PLAN.md`.

## 21. IMPORTANT SCIENTIFIC RULES
- **DO NOT** alter current ABM parameters.
- **DO NOT** treat synthetic personas as observed households.
- **DO NOT** leak validation data into calibration.
- **DO NOT** download unverified data into the production pipeline.

## 22. DELIVERABLES
See supplementary files:
- `docs/data/DATA_DICTIONARY.md`
- `docs/data/DATA_PROVENANCE_SCHEMA.md`
- `docs/data/CALIBRATION_PLAN.md`

## 23. FINAL REPORT SUMMARY
- **P0 Datasets:** NSSO CES, MNRE Benchmark Costs, MNRE Installations, PM Surya Ghar Policy.
- **Missing Variables:** True Income, Direct Peer Networks.
- **Recommended Acquisition Order:** 1. MNRE Policy/Costs, 2. NSSO Demographics, 3. MNRE Adoption Targets.
- **Next Implementation Step:** Authorize download and ETL parsing of the MNRE Benchmark Costs and Policy Guidelines to establish the economic baseline. DO NOT PROCEED WITHOUT AUTHORIZATION.
