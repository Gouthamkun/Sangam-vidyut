# Ecological Baseline Calibration Design (Phase 4D.11)

## 1. Retirement of Current Baseline
The current statistical model (`src/models/statistical/baseline.py`) uses a `mock_fit` initialized on Gaussian noise. 
*   **Classification:** **LEGACY CONTROLLED-EXPERIMENT BASELINE**
*   **Status:** It must be retained in the codebase to guarantee that prior Phase 4C theoretical experiments remain mathematically reproducible. However, it is explicitly prohibited from being used for empirical HCES-based calibration or final research experiments.

## 2. Order of Operations & Synthetic Population Role
To prevent sampling noise from polluting statistical estimation, the correct operational order is:
1.  **Full HCES Data:** Ingest the complete validated `hces_household_core.parquet` (N = 261,953).
2.  **Calibration:** Fit the statistical propensity model using survey weights to aggregate to state levels.
3.  **Freeze:** Freeze the fitted coefficients ($\beta$).
4.  **Generate Synthetic Households:** Run the Phase 4D.8B generator to sample households.
5.  **Compute Propensities:** Apply the frozen model to the synthetic agents to derive their `p_base`.
6.  **Simulate:** Feed the agents into the ABM.

*(We must NEVER calibrate on the N=500/N=5000 synthetic samples).*

## 3. Calibration Outcome Target & Denominator
*   **Numerator:** State-wise PM Surya Ghar residential installation counts (from UQ 1698).
*   **Denominator Candidates:** 
    *   *HCES Expanded State Households:* Computed by summing the `Multiplier` field for each state. This provides perfect internal consistency but might include households without grid access.
    *   *Official Residential Electricity Consumers:* (e.g., from CEA / Ministry of Power reports). This is the true eligible base.
*   **Decision:** The most defensible denominator is **Official Grid-Connected Residential Consumers**. If this is unavailable, the HCES survey-expanded household count serves as the fallback denominator.

## 4. Ecological Identification & Underdetermination Limitation
*   **Limitation:** HCES provides household-level predictors (features), but PM Surya Ghar only provides state-level aggregate outcomes (labels). 
*   **Meaning:** Household-level adoption labels are missing. We are running an *ecological regression*.
*   **Identifiability:** This is a mathematically underdetermined system. Multiple differing configurations of household coefficients can produce nearly identical state-aggregate adoption rates. 
*   **Disclaimer:** The calibration estimates an *aggregate-consistent propensity model* to seed the ABM; it does NOT estimate "true household causal coefficients" or a uniquely identified individual adoption model.

## 5. Feature Design
| Feature | Type | Status/Transformation | Interpretation |
| :--- | :--- | :--- | :--- |
| `derived_mpce` | Continuous | Apply `log(derived_mpce)` to correct heavy-tailed skew | Income/Wealth Proxy |
| `household_size` | Discrete | Retain raw | Energy demand scalar |
| `sector` | Categorical | Urban/Rural | Spatial/grid reliability proxy |
| `dwelling_type` | Categorical | Encode as one-hot | Proxies structural readiness (e.g., independent vs flat) |
| `electricity_access`| Categorical | Filter/Covariate | Grid access necessity |
| `free_electricity` | Binary | Direct boolean | Suppresses adoption incentive |
| `survey_weight` | N/A | **DO NOT USE AS FEATURE** | Must be used strictly for expansion to state-level aggregates during the loss calculation. |

## 6. State Effects Heterogeneity
Should we use state intercepts (Fixed Effects)?
*   *Risk:* State fixed effects (intercepts) will perfectly absorb the variance between state adoption rates, reducing the household-level coefficients (MPCE, dwelling type) to zero/noise. 
*   *Decision:* **No fixed state intercepts.** The model should rely on state-level aggregates of the household features (e.g., a state with higher average MPCE and more independent homes predicts a higher state rate naturally). A Random Effects (hierarchical) structure can be explored as a secondary penalty, but the primary calibration must be a pooled household-level propensity model.

## 7. Temporal Compatibility
*   **Mismatch:** HCES data represents August 2022 – July 2023. PM Surya Ghar represents February 2024 onward.
*   **Implication:** We do not have perfect temporal alignment. We are fundamentally assuming that the structural demographic and economic distributions of states captured in 2023 hold stable through 2024–2026. This temporal lag must be declared in all final ABM reports.

## 8. Aggregate Calibration Objective (Loss Function)
Instead of standard MSE, adoption is a count process (Installations out of Eligible Households).
*   **Recommended Loss:** Binomial Negative Log-Likelihood (NLL) or Poisson NLL. 
*   **Formulation:** Compute $\hat{p}_i = \text{sigmoid}(X_i \beta)$ for each household $i$. Compute the expected state adoption count: $\hat{Y}_s = \sum_{i \in \text{State}_s} (Multiplier_i \times \hat{p}_i)$. Calculate the Binomial log-likelihood of observing the true state count $Y_s$ given the predicted count $\hat{Y}_s$.

## 9. Constraints
*   The Logistic link function ($\text{sigmoid}(X\beta)$) intrinsically guarantees $0 \le p\_base \le 1$.
*   *Monotonicity:* We will NOT impose arbitrary constraints (e.g., forcing MPCE coefficient to be strictly positive) unless cross-validation proves it is required to stabilize the underdetermined ecological gradient.

## 10. Out-of-Sample Validation (Geographic Holdout)
Because PM Surya Ghar data represents a single snapshot, temporal out-of-sample validation is impossible.
*   **Protocol:** Geographic K-Fold Cross-Validation or Leave-One-State-Out (LOSO). We train the ecological coefficients on 30 States/UTs and validate the predicted aggregated adoption rates on the remaining 6 held-out States/UTs.

## 11. Baseline Comparisons
To prove the calibration works, it must beat:
*   **Baseline A:** Intercept-only state rate model (predicts the national mean rate for all states).
*   **Baseline B:** Simple HCES feature aggregate model (Standard OLS predicting state rate using state-mean MPCE).
*   **Candidate C:** The Ecological Propensity Model (household-level logistic aggregated to state).

## 12. Capacity Target Restraint
Residential MW remains a completely separate target (P0-B). Capacity will NOT be used for this household-level calibration. The missing system-size distribution limits MW validation for now.


## 13. Phase 4D.11A Update: Denominator & Temporal Calibration Audit
Based on the manual acquisition of CEA data:
- **Denominator:** Officially updated to the CEA State/UT-wise Domestic Consumers (as on 31st March 2024).
- **Temporal Alignment:** A static denominator is used. Structural features from HCES (2022-23) are paired with the March 2024 CEA base and July 2024 PM Surya Ghar target.
- **Critical Distinction:** The ecological calibration must structurally avoid forcing all observed cumulative variance into p_base. The model acknowledges that observed adoption is the joint outcome of propensity, subsidy, and network diffusion.
