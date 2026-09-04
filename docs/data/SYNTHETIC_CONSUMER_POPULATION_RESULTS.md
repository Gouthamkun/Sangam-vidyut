# Synthetic Consumer Population Validation Report (Phase 4D.8B)

## 1. Sampling Methodology & Weighting Interpretation
The synthetic populations were generated using **survey-weighted empirical resampling**. The official HCES 2023–24 `Multiplier` field was strictly used as a relative sampling probability vector. Because the `Multiplier` acts as an inflation factor, drawing households proportionally to this weight naturally transforms the complex multi-stage stratified dataset into a self-weighting sequence. 

*Important Note:* We do not claim exact national representativeness for small synthetic samples (e.g., N=500). Instead, this procedure guarantees that the synthetic extraction mathematically approaches the target national distribution strictly derived from the HCES core.

## 2. Source Dataset & Parameters
- **Source Dataset:** `hces_household_core.parquet`
- **Population Sizes:** N = 500 (Development configuration)
- **Validation Seeds:** 42, 100, 200, 300, 400
- **RNG:** Explicit NumPy random state tied directly to the seed parameter.

## 3. Duplication Diagnostics
Because sampling occurs *with replacement*, it is mathematically expected for highly weighted or heavily sampled households to be selected multiple times. However, for a small sample of N=500 drawn from a universe of 261,953 records, the duplication collision rate was zero:
*   Total synthetic agents: 500
*   Unique source households: 500
*   Duplicated source households: 0
*   Maximum multiplicity: 1

## 4. Distribution Comparison (Seed 42)
To empirically validate the generation script, we compared the unweighted synthetic frequencies against the survey-weighted frequencies of the complete HCES source dataset. 

*Maximum Absolute Percentage Differences (Deviations):*
*   **State Distribution:** 3.44% max deviation. (All primary states retained).
*   **Sector (Urban/Rural):** 1.04% deviation.
*   **Household Size:** 4.25% max deviation.
*   **Dwelling Type:** 2.72% max deviation.
*   **Electricity Access:** 0.13% max deviation.
*   **MPCE Decile:** 2.40% max deviation.

The generated populations preserve the underlying distributions with normal and acceptable sampling variance for an N=500 draw. (Note: MPCE deciles were correctly pre-computed via weighted quantiles on the entire population, meaning each synthetic household exactly inherited its source stratum without local re-computation).

## 5. Reproducibility & Integrity Tests
The test suite (`tests/data/test_synthetic_population.py`) confirmed:
1.  **Deterministic Reproducibility:** Repeated generation with Seed 42 produces a mathematically identical cohort.
2.  **Seed Distinction:** Changing the seed yields an entirely different set of households.
3.  **Unique Identities:** `synthetic_agent_id` is successfully generated as a UUID to prevent ABM collisions.
4.  **No Hallucinations:** The `home_owner` and `system_size_kw` fields were strictly withheld from the generated parquet structure.

## 6. Important Limitations
The synthetic population is a survey-weighted resampling of observed HCES households. It is not a fully reconstructed synthetic microdata file. It does not recreate the complete finite-population structure, household clustering within strata, or nested geographic hierarchies beneath the district level. It serves strictly as a computationally tractable proxy base for the Sangam Vidyut agent-based model.

## 7. Integration Status
As of Phase 4D.9, the synthetic population has been successfully integrated with the ConsumerAgent via the Adapter factory pattern. Missing fields remain cleanly isolated and backward compatibility with the ABM is mathematically preserved.
