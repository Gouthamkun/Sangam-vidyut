# HCES 2023-24 HOUSEHOLD CORE VALIDATION REPORT (Phase 4D.3A)

## 1. Raw to Processed Reconciliation
The output dataset (`hces_household_core.parquet`) was quantitatively verified against the raw JSON files:
- **Total household records:** 261,953
- **Unique household keys:** 261,953
- **Duplicate keys:** 0
- **Level Joins:** A perfect 1-to-1 relationship was confirmed between Level 01 (Master Frame) and Levels 03, 07, and the aggregated Level 15. The number of unmatched records in all outer joins was explicitly 0.

## 2. Level-11 Documentation Correction
LEVEL-11 is present in the official HCES data dictionary/catalogue but was not present in the downloaded JSON subset used for this ETL. It is not required for the current household-core demographic/economic variables and was therefore excluded. No assumptions or reconstructions of Level 11 were made.

## 3. Expenditure Semantics
The `MONTHLY_CONSUMPTION_EXP` field (from Level 15) successfully represents the household's usual monthly consumption expenditure.
- **Visit Count:** Exactly 4 observations (visits) per household, corresponding to the quarterly survey structure.
- **Derivation Constraint:** The arithmetic mean of `MONTHLY_CONSUMPTION_EXP` across the 4 visits is used as the project's *annual-average-monthly household expenditure derivation*. This is a modeling choice for Sangam Vidyut and is not strictly claimed to be the final official published MoSPI MPCE estimator (which may involve specific outlier/trimming treatments).

## 4. MPCE Audit
The field `derived_mpce` = `MONTHLY_CONSUMPTION_EXP / HH_Size_FDQ`.
- **Denominator (`HH_Size_FDQ`):** Sourced from Level 03. It represents the official demographic count of household members.
- **Missing/Zeros/Negatives:** 0 NaNs, 0 Zeros, and 0 Negative values were found for `HH_Size_FDQ`. 
- **MPCE Range:** Minimum = ₹200.0, Maximum = ₹81,000.0. 
- **Missing MPCE:** 0 NaNs.

## 5. Survey Weight Audit
The `Multiplier` field was retained exactly as the `raw_multiplier` and `processed_survey_weight` without applying the historical `/100` scaling rule, as the official HCES 2023-24 JSON documentation does not explicitly command it.
- **Min:** 369
- **Median:** 114,044.0
- **Mean:** 111,344.8
- **Max:** 2,366,902
- **Unique Values:** 23,567
- **Conclusion:** The vast scale directly implies it operates as an expansion weight mapping to the population.

## 6. Distribution Diagnostics
- **Unweighted MPCE Mean:** ₹3,625.47
- **Weighted MPCE Mean:** ₹3,560.27
- **Unweighted HH Size Mean:** 4.21
- **Weighted HH Size Mean:** 4.17
*(Differences signify the structural necessity of weights for representativeness, as smaller/rural households may carry varying probability expansion weights).*

## 7. Missing-Data Audit
An exhaustive column scan revealed:
- `Type_of_Dwelling_Unit` (Level 03): 1,591 missing (NaN) values. Represents "Unknown" or "Not Applicable".
- All other numeric indicators (State, Sector, District, HH_Size, Energy_Source, Free_electricity, MPCE, Weights) have exactly 0 missing, 0 zeros, and 0 invalid codes. 

## 8. Electricity Data Limitation (Gap)
Level 06 (Fuel and Light) electricity expenditure has **NOT** been included in this core. The exact official `Item_Code` mapping for electricity is absent from the layout documentation, and guessing/hard-coding the code was strictly prohibited.
- **Status:** The household core contains the `Energy_Source_Lighting` access indicator, but **does NOT** contain household electricity expenditure. This remains an open P1 data requirement.

## 9. ConsumerAgent Compatibility
| ConsumerAgent Field | Available HCES Field | Mapping Type | Status |
| :--- | :--- | :--- | :--- |
| `state` | `State` (Level 01/03) | DIRECT | Satisfied |
| `urban_rural` | `Sector` (Level 01/03) | DIRECT | Satisfied |
| `household_size` | `HH_Size_FDQ` (Level 03) | DIRECT | Satisfied |
| `income_proxy` | `derived_mpce` (Level 15/03) | PROXY | Satisfied |
| `free_electricity_subsidy` | `Free_electricity` (Level 07) | DIRECT | Satisfied |
| `roof_suitability` | `Type_of_Dwelling_Unit` (Level 03) | PROXY | Satisfied |
| `electricity_access` | `Energy_Source_Lighting` (Level 03)| PROXY | Satisfied |

**Remaining Requirements (External Datasets Needed):**
- *Home Ownership / Tenure:* NFHS-5 or Census.
- *Solar Adoption History:* MNRE state-level data.
- *Electricity Tariffs:* SERC Tariff Orders.
- *Solar Resource:* NISE/NREL spatial maps.

## 10. Data Lineage & Provenance Validation
All processed variables maintain strict traceability to raw levels and calculations. `data/metadata/households/hces_2023_24/hces_household_core_metadata.json` tracks source files and unmerged key counts. The transformation formulas (e.g., MPCE mean aggregation) are explicitly documented in the ETL script.

## 11. Reproducibility Result
The ETL script was re-run against the raw JSON payload in a temporary backup context. 
- **Result:** `pd.testing.assert_frame_equal` verified perfect deterministic equality (Row, Column, and Value equality).

## 12. Test Result
`python -m pytest` executed cleanly (6/6 tests passed). Test coverage ensures key uniqueness and non-negative MPCE derivation invariants.

## 13. Remaining Data Requirements (Phase 4D.4 Recommendation)
The immediate next phase (4D.4) must address:
1. Identifying the missing Level 06 `Item_Code` for electricity expenditure.
2. Acquiring the PM Surya Ghar/MNRE State-Level residential adoption statistics to serve as the empirical validation target for the ABM.

## FINAL STATUS
**DATA CORE VALIDATED WITH DOCUMENTED LIMITATIONS**
