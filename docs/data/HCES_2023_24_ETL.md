# HCES 2023-24 Household Core ETL Report (Phase 4D.3)

## 1. Objective
Establish the empirical household data layer by processing the raw HCES 2023-24 unit-level JSON records into a memory-safe, unique household core parquet file.

**Scientific Constraints:** This ETL does *not* generate synthetic agents, calibrate solar adoption, alter ABM behavior, or construct social networks. It solely produces the statistical household frame.

## 2. Pre-ETL Audit Resolutions
1. **Level 11 Resolution:** Verified via `tabulation_state_code.xlsx` and `Layout_HCES 2023-24.xlsx` (Sheet2) that Level 11 corresponds to the DGQ Questionnaire (Section 4.3). This level was either omitted from the downloaded JSON package or merged elsewhere; it is not utilized for the core demographic/economic metrics.
2. **Multiplier Scaling:** Historical NSSO text multipliers were scaled down by 100 to yield true household weights. However, the exact `/100` scaling rule for the Multiplier is *not explicit* in the provided HCES 2023-24 JSON format methodology documentation. Consequently, `processed_survey_weight` maps exactly to the unmodified raw `Multiplier`.
3. **Endogeneity (MPCE / Electricity):** The extracted MPCE intrinsically includes electricity bills. This is officially documented here as a potential feature-dependence/endogeneity issue requiring calibration review, as post-solar adoption would alter the MPCE.
4. **Network Data:** No social networks have been artificially generated from HCES.
5. **Solar Adoption:** HCES is strictly used for the demographic baseline, not for the historical rooftop solar adoption target.

## 3. Levels and Variables Extracted
The ETL logically joins the following levels using the composite unique key `FSU_Serial_No` + `Second_Stage_Stratum_No` + `Sample_Household_No`:

*   **Level 01:** Identification particulars.
    *   Variables: `State`, `Sector`, `District`, `Multiplier`.
*   **Level 03:** Household demographics.
    *   Variables: `HH_Size_FDQ`, `Type_of_Dwelling_Unit`, `Energy_Source_Lighting`.
*   **Level 07:** Policy contexts.
    *   Variables: `Free_electricity`.
*   **Level 15:** Consumption expenditure (aggregate across the 4 quarterly visits).
    *   Variables: `MONTHLY_CONSUMPTION_EXP`.

## 4. Processing Logic & Output Validations
*   **Household Key Uniqueness:** Checked and strictly verified (261,953 unique household keys across all merges).
*   **Level 15 Aggregation:** Level 15 comprises exactly 1,047,812 rows (exactly 4 visits per household). The script groups `MONTHLY_CONSUMPTION_EXP` by the primary keys and takes the mean across visits to determine the average monthly expenditure, restoring the 1-to-1 relationship with the master frame.
*   **Derived MPCE:** Calculated exactly as `MONTHLY_CONSUMPTION_EXP / HH_Size_FDQ`.
*   **Electricity Filtering (Level 06):** The official `Item_Code` mapping for electricity could not be verified in the provided methodology or layout documents. To comply strictly with the directive to avoid hard-coding unverified item codes, this step was bypassed.

## 5. Performance Behavior
- **Peak Memory:** Peaked under 3GB because of strategic level filtering and the bypassing of multi-gigabyte item-level datasets.
- **Runtime:** Completed in <2 minutes on a standard developer environment.

## 6. Output Files Produced
- `data/processed/households/hces_2023_24/hces_household_core.parquet`
- `data/metadata/households/hces_2023_24/hces_household_core_metadata.json`
- `tests/data/test_hces_household_etl.py`

## 7. Known Limitations
- Electricity expenditure is currently unavailable due to the unverified item code mapping.
- Validated state codes still need textual labeling via the state crosswalk in downstream processing.
