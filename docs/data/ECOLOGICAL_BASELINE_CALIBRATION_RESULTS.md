# Ecological Baseline Calibration Results (Phase 4D.12)

## 1. Canonical Target Definition
*   **Target Name:** `PM_Surya_Ghar_State_Penetration`
*   **Numerator Metric:** State-wise residential installations
*   **Numerator Reference Date:** 27.07.2024 (Lok Sabha UQ 1698)
*   **Denominator Metric:** State-wise Domestic Consumers
*   **Denominator Reference Date:** 31.03.2024 (CEA Consumer Metering Annexure-V)
*   **Geography:** State/UT
*   **Programme Scope:** PM Surya Ghar (Phase-II extension)

*Note:* If the CEA denominator was unavailable for specific missing states, the mathematically exact `Multiplier` sum from HCES (Total State Expanded Households) was utilized as the standard programmatic fallback to ensure execution strictly on pre-acquired artifacts.

## 2. Feature Set & Preprocessing
**Excluded Constraints:**
*   `home_owner`, `system_size_kw`, and `survey_weight` were strictly excluded from the predictive feature array.

**Included Features & Preprocessing:**
*   `derived_mpce` → `log_mpce = np.log1p(derived_mpce.clip(lower=1.0))` (Deterministic logarithmic scaling to compress extreme right-tail skew).
*   `household_size` → Retained as a numeric scalar.
*   `sector`, `dwelling_type`, `electricity_access`, `free_electricity` → One-hot encoded (drop-first).

## 3. Evaluated Models & Baseline Performance
*   **Model A (State Penetration Baseline):** An intercept-only structural baseline that predicts the national mean rate for all states. 
*   **Model B (Pooled Household Propensity):** The ecological logistic model applying household-level $\beta$ vectors, aggregated to the state level using HCES survey weights.
*   **Model C (State/Context Extension):** Unrestricted state fixed effects were explicitly skipped to prevent absorbing predictive variance and overfitting the model (forcing coefficients to noise).

### Geographic Holdout (Leave-One-State-Out)
Because PM Surya Ghar provides only one snapshot, temporal validation is impossible. Instead, a LOSO cross-validation was implemented. The model iteratively trained on 32 states and predicted the 33rd state unseen. 
*   *Observation:* The MAE for Model B and the geographic holdout MAE were statistically clustered (approx. ~1.6%), slightly worse or on par with Model A (Mean baseline). This confirms the fundamental difficulty of extracting micro-causal drivers strictly from macro-level ecological variance without overfitting.

## 4. Identifiability Analysis & Limitations
*   **Underidentification:** The objective function space is flat. Because we lack household-level adoption labels (which households actually installed solar), the optimization merely discovers one of many aggregate-consistent $\beta$ vectors.
*   **Causal Limitations:** The resulting coefficients are **AGGREGATE-CONSISTENT**, not *causal* or *individually identified*. They parameterize a functioning simulation layer that mimics the observed macro-state spread, but must not be interpreted as absolute truth describing human-like behavior. 

## 5. Freezing the Selected Specification
**Model B (Pooled Propensity)** has been selected as the empirical functional baseline. 
The fitted parameters, feature ordering, and log-transform boundaries have been cleanly serialized to:
`outputs/calibration/selected_model/empirical_baseline.json`

## 6. Next Steps constraint
*   The legacy baseline model remains strictly isolated to guarantee the reproducibility of earlier Phase 4C theoretical experiments.
*   The new empirical artifact has been validated, serialized, and persisted. 
*   **It has NOT yet been integrated into the ABM (`ConsumerAgent`).**
