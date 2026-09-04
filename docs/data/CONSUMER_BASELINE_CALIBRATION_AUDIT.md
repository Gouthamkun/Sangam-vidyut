# Consumer Baseline Logistic Model Calibration Audit (Phase 4D.10)

## 1. Audit of the Existing Baseline Model (`p_base`)
The current baseline statistical model (`src/models/statistical/baseline.py`) is implemented as an uncalibrated mock placeholder.
*   **Model Type:** `LogisticRegression` (scikit-learn).
*   **Training Data Source:** Dynamically generated pure random noise during initialization (`mock_fit`).
*   **Training Features:** `[income, home_owner]`
*   **Feature Scaling/Transformation:** None. The model is trained directly on $X \sim N(0, 1)$ without StandardScaler.
*   **Target Variable:** Binary $y \in \{0, 1\}$ assigned uniformly at random.
*   **Scientific Status:** The model is strictly illustrative and **scientifically invalid** for the current HCES empirical inputs.

### Feature Compatibility Matrix
| Feature | Old Meaning | Unit | Range | HCES Equivalent | Compatibility | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `income` | Raw Income | Arbitrary | $\approx [-3, 3]$ (Standard Normal) | `derived_mpce` (INR) | **INVALID** | `derived_mpce` ranges in the 1,000s–10,000s. Direct substitution causes extreme extrapolation. |
| `home_owner` | Tenure Boolean | Binary | $\{0, 1\}$ | `home_owner = -1` | **INVALID** | HCES does not observe tenure. Passing -1 into a model trained on $\{0, 1\}$ introduces mathematical bias. |

## 2. MPCE vs Income Compatibility & Extrapolation Check
HCES measures *expenditure*, not income. `derived_mpce` is a rigorous per-capita proxy, but mathematically, substituting an expenditure metric natively bounded in $[1000, 50000+]$ into a model trained on data bounded in $[-3, 3]$ causes catastrophic extrapolation.
*   **Extrapolation Percentage:** 100% of the HCES `derived_mpce` values fall completely outside the logistic regression's training domain. 
*   **Resulting Distribution:** Because $X$ is massive, the dot product $X \cdot \beta$ diverges instantly. The resulting `p_base` distribution mathematically collapses exactly to `0.0` or `1.0`. (An N=500 audit showed $p\_base < 0.01$ for all 500 agents with median exactly $0.0$).

## 3. Home Ownership Limitation
Because HCES 2023-24 lacks a dedicated tenure variable, `home_owner` was mapped as **UNAVAILABLE** (`-1`). The logistic regression mathematically interprets `-1` as a continuous numeric scalar, skewing the intercept boundary unpredictably. 
*   **Recommendation:** Future calibration must either structurally drop the `home_owner` requirement from the regression entirely or replace it with a separate sub-model proxy if conceptually required.

## 4. Calibration Target Requirement
To correct this, we must replace the `mock_fit` random target with an empirically defensible adoption target.
*   **Available Target:** PM Surya Ghar residential installation/household counts (Phase 4D.5B).
*   **Ecological Inference Limitation:** HCES provides household-level microdata (features), but the PM Surya Ghar target only provides state-level macro-counts (labels). We do not possess a dataset mapping *which specific household* adopted. The calibration design must address this ecological missing-label problem.

## 5. Recommended Calibration Design
*   **Target:** State-wise PM Surya Ghar adoption rates (Installations / Households).
*   **Feature Engineering:** Standardize `derived_mpce` (e.g., Z-score or logarithmic scaling). Drop `home_owner`. Include `sector`, `electricity_access`, and `dwelling_type` as categorical predictors.
*   **Training Methodology (Ecological Calibration):** 
    1. Group the HCES synthetic sample by state.
    2. Define a loss function comparing the *predicted state adoption rate* (mean of predicted household probabilities) against the *observed state adoption rate* (from PM Surya Ghar UQ 1698).
    3. Fit the logistic coefficients ($\beta$) via gradient descent to minimize this ecological loss, rather than fitting to mock household-level binary labels.
*   **ABM Implementation:** Once calibrated, freeze the coefficients and deploy them statically into the ABM to generate household-level `p_base` probabilities.

## 6. Synthetic ID Reproducibility
The `synthetic_agent_id` generation logic uses `uuid.UUID(bytes=np.random.bytes(16))` explicitly constrained by the random seed `S`. 
*   **Reproducibility Status:** **EXACT**. The same source data + same seed deterministically produces identically ordered UUIDs and identically matched household attributes.

## 7. Baseline Model Scientific Status
**Classification:** **D. Scientifically invalid for current HCES inputs.**
The model strictly requires recalibration using proper feature scaling and empirical ecological targets before its outputs can be trusted in the ABM decision equation.
