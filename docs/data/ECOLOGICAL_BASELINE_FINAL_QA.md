# Ecological Baseline Final QA (Phase 4D.12A)

## 1. Verified Numerator Provenance
*   **Question Number:** Lok Sabha UQ 1698
*   **Answer Date:** 29.07.2026
*   **Table Title:** Annexure referred to in reply of parts (a) to (e)
*   **Reference Date:** 27.07.2026
*   **Installation Metric:** Count (Sector: Residential)
*   **Source PDF:** `lok_sabha_uq_1698_pmsuryaghar.pdf`
*   **Source Page:** 3

*Discrepancy Warning:* The Phase 4D.12 calibration implementation incorrectly hardcoded the year 2024 in both the schema and documentation. The verified artifact clearly mandates **2026**.

## 2. Verified Denominator Provenance & Consistency
The calibration implementation attempted to use the CEA Domestic Consumer denominator (as of 31.03.2024). However, an audit of the target-construction merge reveals severe contamination in the extraction layer:

| State | Numerator (Installations) | Denominator Source | Denominator | Observed Rate | Mapping Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Gujarat | 766278.0 | CEA | 14881962.0 | 0.0514 | CEA Matched |
| Maharashtra | 692853.0 | CEA | 25047631.0 | 0.0276 | CEA Matched |
| ... | ... | ... | ... | ... | ... |
| Chhattisgarh | 82920.0 | CEA | NaN | NaN | Unmatched/Missing |
| Jharkhand | 3279.0 | CEA | 41690.0 | 0.0786 | CEA Matched (Incomplete/Flawed) |
| Dadra & Nagar Haveli and Daman & Diu | 1138.0 | CEA | NaN | NaN | Unmatched/Missing |
| Andaman & Nicobar Islands | 407.0 | CEA | NaN | NaN | Unmatched/Missing |

**Denominator Policy Recommendation:** 
**Policy A:** CEA Domestic Consumer denominator for all states, after resolving deterministic state mapping.
The naive PDF extraction script failed to aggregate all utilities for Jharkhand (capturing only 41k consumers instead of ~5-6 million) and entirely missed Chhattisgarh and two UTs due to string mapping failures. A robust, verified extraction mapping of all DISCOMs to their parent states in the CEA Annexure-V is strictly required before proceeding.

## 3. Target Rate Definition
The target rate remains defined as:
`PM Surya Ghar residential installations (2026) / CEA Domestic Consumers (2024)`. 
This mixed-temporal structure must be formally documented as the official macro-target.

## 4. Objective Actually Used
**Objective comparison planned, but current implementation selected MSE without an executed NLL comparison.**
This is classified as a minor documentation/experiment-design deviation. NLL was preemptively skipped due to anticipated numerical explosion given $N=261M$ counts, but the formal evaluation step was bypassed.

## 5. Model C Status
Model C (State/Context Extension) was **NOT empirically evaluated**. The evaluation was skipped because testing unrestricted state fixed effects against 33 state targets would perfectly absorb cross-state variance and mathematically overfit, forcing household coefficients to noise.

## 6. Model B & LOSO Results
*   Model A training MAE ≈ 1.48%
*   Model B training MAE ≈ 1.29%
*   Model B LOSO MAE ≈ 1.67%

**Interpretation:** The pooled household-feature model reduced in-sample aggregate error relative to the national-mean baseline, while geographic holdout error was higher, indicating limited out-of-sample identification from the available state-level aggregate target. 

## 7. Identifiability
The model remains mathematically underidentified. The coefficients are **aggregate-consistent**, which does not mean they are **household-level identified**, and they are explicitly not **causal**.

## 8. Final Status
**REQUIRES RE-FIT**
The model cannot be frozen. The fitted target used an incorrect temporal metadata string (2024 instead of 2026) and was actively contaminated by a flawed denominator extraction (Jharkhand utility omission and missing states). The extraction must be fixed and the coefficients refitted.
