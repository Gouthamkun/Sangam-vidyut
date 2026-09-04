# SOLAR ADOPTION SOURCE AUDIT (Phase 4D.4)

## 1. Objective & Source Priority
This audit identifies the strongest official Indian data sources for residential rooftop solar (RTS) adoption. Priority is strictly assigned to primary Government of India agencies (MNRE, National Portals, Parliament). Secondary consultancy estimates (e.g., JMK Research, Bridge to India) are excluded as primary calibration targets.

## 2. Temporal & Geographic Audit
| Dataset | Earliest Year | Latest Year | Frequency | Missing/Continuity | Geographic Coverage | Boundary Stability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MNRE SPIN Portal** | ~2015 | Early 2024 | Live/Snapshot | Halted updates post PM Surya Ghar transition. | State/UT | Stable (J&K split to UTs handled natively). |
| **PM Surya Ghar** | Feb 2024 | Present | Daily | Continuous since launch. | State/UT | Stable. |
| **MNRE Overall RTS**| 2014 | Present | Monthly | Continuous. | State/UT | Stable. |

## 3. Residential Segmentation
*Crucial Distinction: "Rooftop Solar" in India is heavily dominated by Commercial & Industrial (C&I) installations (historically ~70-80%). Datasets merging these are scientifically hazardous for a household ABM.*
- **MNRE SPIN Portal:** **DIRECTLY OBSERVED.** The portal explicitly segments installed capacity and number of consumers into "Residential", "Institutional", "Social", "Commercial", etc.
- **PM Surya Ghar Dashboard:** **DIRECTLY OBSERVED.** The scheme is exclusively for residential households.
- **MNRE Overall RE Capacity:** **MIXED (Aggregated).** Does not segment C&I from Residential. *Limitation: Should only be used as a macro upper-bound unless an explicit assumption (expert ratio allocation) is scientifically documented and approved.*

## 4. Variable Audit
| Dataset | Variable | Definition | Unit | Geography | Time | Residential? | Install vs Capacity | Cumul. vs Annual | Source | Confidence | Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SPIN** | `Consumers` | Distinct connected RTS meters | Count | State | Snapshot | Yes (Segmented) | Installation | Cumulative | MNRE | High | Legacy portal deprecation. |
| **SPIN** | `Capacity` | Total rated inverter/panel limit | MW | State | Snapshot | Yes (Segmented) | Capacity | Cumulative | MNRE | High | Same as above. |
| **SuryaGhar** | `Installations`| Systems physically installed | Count | State | Live | Yes (100%) | Installation | Cumulative (from 2024) | MNRE | Highest | Very short temporal history. |
| **Overall RE**| `RTS_Capacity` | Total RTS connected | MW | State | Monthly | No (Mixed) | Capacity | Cumulative | MNRE | High | Blends C&I. |

## 5. Calibration Target Design
**Recommended Target:** Cumulative Residential Installations (Household Count).
**Why:** Sangam Vidyut models *discrete household agents* making binary adoption decisions (`agent.adopted = True`). 
**Transformation:** 
`Observed Cumulative Residential Consumers (SPIN) + PM Surya Ghar Installations` 
-> *Target Household Count per State*
-> *Corresponding Sangam Vidyut Quantity:* `sum(agent.adopted * agent.processed_survey_weight)` grouped by state.
*Note:* Installed capacity (MW) is a secondary target requiring assumptions about average system size (kW per household). Installation count directly maps to the ABM's adoption rate.

## 6. Validation Split
The previously proposed split (2015–2021 Calibration, 2022–2024 Validation) **is highly defensible** based on this audit.
- **2015–2021:** Corresponds to MNRE Rooftop Solar Programme Phase I and early Phase II. Data resides in the legacy SPIN portal. Represents the organic, slower adoption phase.
- **2022–2024:** Captures the simplification of the National Portal (Phase II streamlining) and culminates in the massive February 2024 policy shock of the PM Surya Ghar scheme. Validating the ABM's ability to natively reproduce this hockey-stick growth without being explicitly trained on it is a rigorous scientific test.

## 7. Policy Change Audit (Regime Shifts)
1. **Pre-2019 (Phase I):** State-driven subsidy mechanisms, highly fragmented, slow adoption.
2. **2019–2023 (Phase II & National Portal):** Centralized Direct Benefit Transfer (DBT). Smoother process.
3. **Feb 2024 (PM Surya Ghar):** Massive subsidy hike (up to ₹78,000) + aggressive loan structures + marketing.

## 8. Data Quality & Limitations
- **Capacity vs Installation Ambiguity:** Many MNRE PDFs report only "MW", failing to report "Number of Consumers".
- **Duplicate Counting Risk:** Bridging legacy SPIN data with the new PM Surya Ghar portal risks double-counting if legacy Phase II installations are migrated into the new portal's tracking.
- **Missing Data:** Granular month-by-month residential counts from 2015-2019 are difficult to acquire; often only annual/snapshot data survives.

## 9. Provenance
See `docs/data/solar_adoption_source_registry.json`. All datasets are official Government of India Open Data but must be verified/downloaded manually to avoid scraper blockades.

## 10. Final Recommendation
**Minimum Defensible Bundle:**
1. **P0 (Calibration Target):** MNRE SPIN Portal State-wise Sector-wise Report (Snapshot of Residential Consumers/Installations up to end of 2023).
2. **P0 (Validation Target):** PM Surya Ghar State-wise Installation Count (Feb 2024 - Present).

## MANUAL DOWNLOAD INSTRUCTIONS
*To be executed manually by the user.*
1. Navigate to the legacy MNRE SPIN portal (or check Parliament Unstarred Questions on RTS if the portal is fully deprecated).
2. Download the State-wise, Sector-wise (Residential) Installation Count table. 
3. Navigate to the PM Surya Ghar official dashboard.
4. Download the State-wise Application/Installation summary.
5. Save these as flat CSV files to `data/raw/solar/adoption/`. 
*(Detailed instructions provided in the agent's main response output).*
