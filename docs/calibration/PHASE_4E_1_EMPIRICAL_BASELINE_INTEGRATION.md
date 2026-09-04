# Phase 4E.1 Empirical Baseline Integration

## 1. Why the integration is needed
Previous versions of the simulation relied on an illustrative logistic regression (`AdoptionLogisticRegression`) mapping randomly generated `income` and `home_owner` variables into a uniform theoretical adoption probability. Phase 4D produced a scientifically verified, aggregate-calibrated empirical propensity model trained on true HCES 2023-24 household structures mapping against the corrected CEA denominators. 
Integrating this empirical model replaces the illustrative baseline with a heterogeneous, real-world derived simulation prior without altering the underlying mathematical rules of SIR network diffusion, economic affordability, or LLM-based cognitive decisions.

## 2. Frozen Artifact
The provider explicitly loads the frozen artifact without modification:
*   **Path:** `outputs/calibration/selected_model/empirical_baseline.json`
*   **SHA-256:** `0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241`

## 3. Feature Mapping
Within `EmpiricalBaselineProvider`, synthetic household properties are strictly mapped to the calibrated feature representation:
*   `derived_mpce` → `log_mpce` (using the same log1p transformation applied at fit-time)
*   `household_size`, `sector`, `dwelling_type`, `electricity_access`, `free_electricity`
*   Forbidden features (`home_owner`, `system_size_kw`, `survey_weight`) are architecturally firewalled from the prediction calculation.

## 4. Provider Architecture
A new `EmpiricalBaselineProvider` abstraction was built to enforce a strict boundary between the structural equation modeling and the Mesa `ConsumerAgent`. 
*   **Deterministic Loading:** Loads the artifact JSON precisely once.
*   **Data Transformation:** Ensures missing dummies default to `0.0` and enforces strict deterministic column ordering.
*   **Logistic Evaluation:** Evaluates the dot product of the agent feature vector with the frozen coefficients, applying a standard sigmoid bounded perfectly in $[0, 1]$.

## 5. Legacy Compatibility
A new `baseline_provider` switch has been added to `SimulationConfig`:
```yaml
simulation:
  baseline_provider: "legacy" # Default
```
This guarantees that all previous Phase 4C theoretical experiments (which rely on the illustrative mock regression) remain 100% backward-compatible and bit-for-bit reproducible.

## 6. Mathematical Integration Point
In `ConsumerAgent.step()`, `p_base` is now dynamically sourced:
```python
if getattr(self.model, "baseline_provider", None) is not None:
    p_base = self.model.baseline_provider.predict(self)
else:
    # Legacy logic
```
This isolates the change entirely to the $P_{base}$ component of the hybrid score, strictly preserving the SIR mathematical structure, subsidy economics, thresholds, and LLM LangGraph routing logic.

## 7. Scientific Interpretation
**IMPORTANT CONSTRAINT:** The empirical `p_base` does *not* represent a causal probability of observed real-world household adoption. It is an **aggregate-calibrated household-level baseline propensity used as a heterogeneous simulation prior.** The final adoption dynamic observed within the ABM remains the emergent sum of this prior, social diffusion, and economic subsidy shocks.

## 8. Determinism
Repeated `model.baseline_provider.predict(agent)` calls produce mathematically identical results (difference $< 1e^{-9}$) for identically parameterized households.

## 9. Smoke-Test Results
*   **Distribution Analysis (500-agent Synthetic Population):**
    *   Min: ~0.000019
    *   Max: ~0.111450
    *   Median: ~0.000330
    *   Mean: ~0.001238
    *   No NaNs, No Infs. All valid probabilities bounded in $[0, 1]$. Heterogeneity confirmed (StdDev ~0.0056).
*   **ABM 100-Agent Deterministic Smoke Test:**
    *   The model initialized successfully, synthesized the population, stepped forward 4 quarters, and handled the probability matrix flawlessly. (0 explicit threshold-crossing adoptions occurred under static initialization in 4 timesteps, correctly matching the exceptionally low probability mass).

## 10. Test Results
*   89/89 unit and integration tests passed.
*   Added `test_legacy_equivalence` ensuring Phase 4C tests operate identically under `"legacy"`.
*   Added `test_empirical_provider_determinism` and `test_empirical_integration_and_distribution` to validate probability limits and empirical model structure.

## 11. Provenance
*   **Calibration Artifact Path:** `outputs/calibration/selected_model/empirical_baseline.json`
*   **Baseline Provider Type:** `"empirical"`
*   **Smoke Test Seed:** `100`
