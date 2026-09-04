# Phase 4D.12B Ecological Refit

## 1. Objective
Refit the empirical ecological baseline using ONLY the repaired, consistently CEA-denominated PM Surya Ghar state-level targets, while explicitly preserving its ecological (non-causal) interpretation.

## 2. Corrected Data Sources
*   **Target:** `outputs/calibration/target/pm_surya_ghar_state_penetration_corrected.json`
*   **Numerator:** PM Surya Ghar Residential Installations (Reference Date: 27.07.2026, Source: Lok Sabha UQ 1698).
*   **Denominator:** CEA Domestic Consumers (Reference Date: 31.03.2024). Validated 36-state coverage with strict utility mapping; HCES fallback removed.

## 3. Target Construction
State Penetration = `PM_Surya_Ghar_installations` / `CEA_domestic_consumers`. All rates are bounded in $[0, 1]$. The contaminated historical target remains strictly isolated.

## 4. Feature Specification
*   **Included:** `log_mpce` (log1p bounded at 1.0), `household_size`, and one-hot dropped encodings of `sector`, `dwelling_type`, `electricity_access`, `free_electricity`.
*   **Excluded:** `home_owner`, `system_size_kw`, `survey_weight`.
*   **Aggregation:** HCES `Multiplier` (survey weights) are strictly utilized to aggregate predicted household-level logits into comparable state-level probabilities.

## 5. Models Evaluated
*   **Model A (State Mean Baseline):** A uniform rate predicting the national mean penetration across all states.
*   **Model B (Pooled Propensity Model):** A logistic household-feature model aggregated to states.
*   **Model C:** Intentionally omitted to prevent unrestricted state fixed effects from mathematically overfitting (absorbing cross-state variance).

## 6. Optimization & Identifiability Limitations
The optimization minimized state-level Mean Squared Error (MSE) bounded between $[0, 1]$. 
**Identifiability Limitations:** Because household-level adoption labels do not exist, the optimization does not uniquely identify household behavior. Multiple $\beta$ vectors can generate similar aggregate state-level outcomes. The resulting coefficients are **aggregate-consistent simulation parameters**. They are NOT causal estimates, nor are they individually identified behavioral coefficients.

## 7. Results

### In-Sample Results
*   **Model A (Mean) MAE:** 1.24%
*   **Model A (Mean) RMSE:** 1.53%
*   **Model B (Propensity) MAE:** 1.04%
*   **Model B (Propensity) RMSE:** 1.34%

### LOSO Results (Geographic Cross-Validation)
*   **Model A (Mean) LOSO MAE:** 1.27%
*   **Model A (Mean) LOSO RMSE:** 1.57%
*   **Model B (Propensity) LOSO MAE:** 1.20%
*   **Model B (Propensity) LOSO RMSE:** 1.53%

## 8. Final Selection Decision
**Model B (Pooled Propensity Model) is selected.** 
Model B provides modest geographic generalization improvement over the mean baseline (1.20% vs 1.27% LOSO MAE). Crucially, Model B provides heterogeneous household-level baseline propensities derived from empirical aggregate calibration. A uniform intercept-only baseline would remove this source of cross-household heterogeneity from the simulation.

## 9. Reproducibility/Provenance
*   **Random Seed:** 42
*   **Final Artifact:** `outputs/calibration/selected_model/empirical_baseline.json`
*   **Artifact SHA-256:** `0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241` (Stored in `refit_manifest.json`)
*   **Software version:** Scipy L-BFGS-B (Deterministic initialization, strict scaling).

## 10. Test Results
All PyTest suites (`tests/calibration/test_ecological_refit.py`) pass successfully, verifying correct provenance, boundary invariant checks, ABM isolation, and target schemas.
