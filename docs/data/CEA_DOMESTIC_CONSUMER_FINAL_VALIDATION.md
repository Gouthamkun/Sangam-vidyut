# CEA Domestic Consumer Extraction Repair & Final Validation (Phase 4D.11B)

## 1. The Denominator Contamination
An audit of the Phase 4D.12 denominator extraction revealed severe missing data. The naive PDF string-matching missed multi-utility states, specifically failing to aggregate JBVNL for Jharkhand due to a PDF artifact, and missing UTs (like Chandigarh and Lakshadweep) entirely.

## 2. Extraction Methodology
A robust, deterministic mapping was introduced. Annexure-V of the `cea_consumer_metering_31mar2024.pdf` contains a globally numbered list of 85 utilities/DISCOMs. 
The extraction process now:
1. explicitly maps utility IDs `1` through `85` to their precise State/UT.
2. intercepts a known PDF artifact on utility `21` (JBVNL), where Domestic counts leaked onto the utility header row instead of their own row.
3. enforces a structural invariant: `URBAN_DOMESTIC` + `RURAL_DOMESTIC` = `TOTAL_DOMESTIC`.
4. explicitly validates the sum of all state domestic consumers against the CEA-declared National Domestic Total.

## 3. Findings & State Coverage
*   **Total Utilities Found:** 79 domestic-serving utilities (out of 85 total; the remainder are SEZs/industrial parks with 0 domestic consumers).
*   **National Domestic Consumers:** `272,724,602`. This perfectly reconciles with the national sum expected by the CEA.
*   **State Coverage:** All 36 States/UTs are deterministically mapped. The silent HCES fallback has been permanently disabled.

## 4. Range and Sanity Checks
*   `0 <= installations`: Passed.
*   `0 < domestic_consumers`: Passed for all 36 States.
*   `0 <= penetration <= 1`: Passed.

**Noteworthy Adjustments:**
*   Jharkhand's denominator was restored from 41k to **5.55 Million** consumers. Its observed PM Surya Ghar penetration mathematically fell from an absurd ~8% to a correct **0.059%**.
*   Chhattisgarh's denominator was successfully retrieved (**5.15 Million**), establishing a rate of **1.6%**.

## 5. Artifact Reconstruction
*   `cea_domestic_consumers_by_utility.parquet`: The granular, utility-level parsing result.
*   `cea_domestic_consumers_by_state.csv`: The clean, aggregated state denominators.
*   `pm_surya_ghar_state_penetration_corrected.json`: The final logistic calibration target, with verified reference dates (Numerator: 27.07.2026, Denominator: 31.03.2024) and flawless denominators.

## 6. Final Status
**CEA DENOMINATOR VALIDATED**
The denominator extraction is now deterministically proven, perfectly covers all 36 administrative units without HCES fallbacks, correctly mitigates the JBVNL PDF artifact, and is backed by a fully green test suite. The pipeline is structurally sound and prepared for coefficient refitting.
