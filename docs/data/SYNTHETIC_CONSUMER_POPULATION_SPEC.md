# Synthetic Consumer Population Specification (Phase 4D.8 / 4D.8A)

## 1. Sampling-Weight Methodological Justification
The HCES `Multiplier` represents the statistical expansion factor (inflation factor), indicating the exact number of households in the national/stratum population that a given sampled household represents. 
- **Methodological Legitimacy:** Passing the `Multiplier` directly as a sampling weight (`weights="Multiplier"`) with replacement (`replace=True`) is the mathematically correct procedure for simulating a synthetic population. By sampling households proportionally to their expansion weights, the resulting synthetic draw inherently un-weights the survey and yields a "self-weighting" representative cross-section of the true demographic distribution.
- **Data Integrity:** The raw data does NOT need scaling or mathematical mutation prior to sampling, as the `pandas.DataFrame.sample` method automatically normalizes the weight vector to relative probabilities.

## 2. Household Tenure Availability
An audit of the extracted HCES 2023-24 variables confirms that `Type_of_Dwelling_Unit` denotes the structural/architectural characteristics of the residence (e.g., independent house vs. flat), NOT legal ownership or tenure. Therefore, a household's tenure (owned vs. rented) is **UNAVAILABLE** in the current dataset. We will NOT silently infer home ownership from dwelling type. The attribute `home_owner` will be classified as explicitly missing.

## 3. Final ConsumerAgent Mapping
The synthetic agent generator will explicitly use the following mapping architecture:

| ConsumerAgent Field | HCES Source | Status | Transformation | Justification |
| :--- | :--- | :--- | :--- | :--- |
| `state` | `State` | **DIRECT** | None | Core geography. |
| `district` | `District` | **DIRECT** | None | Core geography. |
| `sector` | `Sector` | **DIRECT** | None | Urban/rural categorization. |
| `household_size` | `HH_Size_FDQ` | **DIRECT** | None | Demographic structure. |
| `dwelling_type` | `Type_of_Dwelling_Unit` | **DIRECT** | None | Architectural structure. |
| `home_owner` | N/A | **UNAVAILABLE** | None | Tenure is not extracted. Do NOT infer from dwelling type. |
| `electricity_access` | `Energy_Source_Lighting` | **DIRECT** | None | Energy status. |
| `free_electricity` | `Free_electricity` | **DIRECT** | None | Subsidy indicator. |
| `monthly_consumption_expenditure` | `MONTHLY_CONSUMPTION_EXP` | **DIRECT** | None | Base expenditure metric. |
| `derived_mpce` | N/A | **DERIVED** | `MCE / HH_Size` | Per-capita economic proxy. Validated previously. |
| `mpce_decile` | N/A | **DERIVED** | `Weighted Quantile` | Stratification via Multiplier. |
| `survey_weight` | `Multiplier` | **DIRECT** | None | Ensures sample methodology provenance. |

## 4. Sampling Procedure
The synthetic population will be drawn via a seed-controlled algorithm to guarantee reproducibility while preserving the complex survey design:
```python
synthetic_population = hces_df.sample(
    n=size,
    weights='Multiplier', 
    replace=True, 
    random_state=S
)
```
- **Requirements Met:**
  - All states/UTs are retained.
  - The replacement policy allows high-weight households to be selected multiple times, accurately mirroring national demographics.
  - No raw data mutation is performed.

## 5. Validation Diagnostics
After running the sample procedure, a diagnostic script must compare the **synthetic sample distribution** against the original **source distribution (survey-weighted)**. The validation must measure:
- **State distribution**
- **Urban/rural distribution**
- **Household-size distribution**
- **MPCE distribution (mean, variance, density)**
- **MPCE decile representation**

*Constraint:* For the N=500 Development configuration, statistical dispersion will naturally occur. The diagnostic will not claim perfect inferential representativeness at N=500, but will mathematically confirm that the generative algorithm is operating correctly against the weighted vector. 
