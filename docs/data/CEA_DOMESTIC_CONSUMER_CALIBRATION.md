# CEA Domestic Consumer Calibration Audit (Phase 4D.11A)

## 1. PM Surya Ghar Target & Denominator
The verified state-wise target formulation is:
$$ Adoption\_Rate_{state} = \frac{PM\_Surya\_Ghar\_Installations\ (July\ 2024)}{CEA\_Domestic\_Consumers\ (March\ 2024)} $$

Because domestic consumer counts are structurally stable (growing 1-2% annually) and no official July 2024 count exists, the March 2024 CEA static denominator is the most scientifically defensible and officially validated base available. 

## 2. Temporal Alignment
*   **Predictors (HCES):** Aug 2022 – Jul 2023
*   **Denominator (CEA):** 31st March 2024
*   **Numerator (PM SG):** July 2024
*   **Alignment Status:** We utilize a static denominator. The assumption is that structural household predictors (HCES) remain proportionally stable over the 1-2 year lag, and the CEA denominator is treated as a fixed population boundary.

## 3. Critical Calibration Distinction
It is scientifically invalid to equate **Cumulative PM Surya Ghar Installations** with raw **Household Adoption Propensity**. 
Observed adoption is the joint, cumulative outcome of multiple ABM forces:
$$ Observed\_Adoption = f(\underbrace{p\_base}_{\text{Household Propensity}} + \underbrace{Government}_{\text{Subsidy}} + \underbrace{Network}_{\text{SIR Diffusion}} + \underbrace{Industry}_{\text{Economics}}) $$
Forcing all observed state-level variation entirely into `p_base` during statistical calibration overfits the logistic model and falsely attributes policy-driven or network-driven adoption clusters entirely to static demographics. The calibration must isolate the propensity baseline without absorbing the dynamic simulation factors.

## 4. Identification & Underdetermination
Because we only possess cumulative state-level outcomes, estimating $P(\text{adoption propensity} | \text{household characteristics})$ is strictly **underidentified**.
*   We cannot recover unique household-level causal coefficients from macro-level targets alone.
*   **Solution:** The ecological calibration will estimate a constrained, pooled aggregate model. We will NOT claim these are true household-level causal coefficients. They are functional simulation seeds designed to reproduce macro-accuracy.

## 5. Baseline Comparisons Design
Future calibration will compare four nested structures:
*   **A. State Observed Penetration Baseline:** A purely macro model predicting a uniform rate per state regardless of micro-features.
*   **B. Household-Feature Aggregate Propensity Model:** A basic feature model aggregated to the state level without state effects.
*   **C. Household-Feature + State/Context Covariates:** Adding regional economic proxies to B.
*   **D. Full ABM-Generated Adoption:** The simulation output itself, tested against the statistical aggregate.

## 6. Calibration Target Recommendation
The first empirical calibration target should be:
**Cumulative penetration at a fixed reference date (July 2024 PM Surya Ghar counts / March 2024 CEA Consumers).** 
Incremental adoption over a defined period is superior for dynamic fitting but requires multiple temporal snapshots that are not yet officially available for PM Surya Ghar.

## 7. Phase 4D.11B Extraction Repair
An audit in Phase 4D.12 revealed that naive PDF text extraction of the CEA denominator was fundamentally flawed due to complex utility-level reporting (e.g., missing JBVNL for Jharkhand). 
A robust repair was implemented in Phase 4D.11B (\scripts/data/extract_cea_domestic_consumers.py\) using explicit deterministic utility-to-state mappings for all 85 DISCOMs in Annexure-V. The final, verified CEA denominator completely covers all 36 States/UTs (totaling ~272.7M consumers) without any silent fallbacks to the HCES dataset. The verified targets are persisted in \pm_surya_ghar_state_penetration_corrected.json\.

