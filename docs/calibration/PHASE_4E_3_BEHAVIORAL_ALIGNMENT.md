# Phase 4E.3: Behavioral Score Scale / Threshold Alignment

## 1. Objective and Premise
The objective of this phase was to determine whether the near-zero adoption observed during Phase 4E.2 was an expected mathematical consequence of retaining the inherited Phase 4C thresholds against the new empirical `p_base`, or a structural incompatibility requiring redesign.

**Conclusion:** The inherited Phase 4C thresholds were not calibrated from the empirical PM Surya Ghar observations. Phase 4E.2 demonstrated that they create a largely unreachable adoption regime when combined with the empirically calibrated household propensity scale.

## 2. Mathematical Reachability (Phase B)
Using the defined model equation:
`score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability`

We evaluated the exact bounds under the empirical `p_base` distribution ($P_{max} \approx 0.11145$):
*   **Max Possible Score:** $0.4(0.11145) + 0.4(1.0) + 0.2(1.0) = 0.64458$
*   **Autonomous Threshold:** `0.7`.
*   **Result:** Autonomous adoption is **mathematically impossible** for any agent under any condition, because the absolute max possible score (`~0.645`) is strictly less than the `0.7` threshold.

Furthermore, analyzing the Cognitive Threshold (`0.3`) under default affordability (`0.2`, meaning $0.2 \times 0.2 = 0.04$ base score):
*   At empirical $P_{99} \approx 0.01$, an agent requires `sir_score >= 0.64` to reach the `0.3` threshold.
*   Under a standard `beta = 0.05`, reaching a `sir_score` of `0.64` requires $\approx 21$ infected neighbors. 
*   **Result:** Given typical network topologies (e.g. Watts-Strogatz $k=4$), the cognitive layer is essentially **unreachable**, confirming the model is operating in a "DEAD" regime.

## 3. Target Leakage Prevention (Phase E)
When redesigning or tuning thresholds/weights, we must **NOT** optimize them directly against PM Surya Ghar installation counts, CEA penetration targets, or any desired final adoption curve. 
*   **Scientific Rationale:** The empirical calibration (Phase 4D) already consumed those aggregate observations to fit the `p_base` parameters.
*   **Leakage:** Re-using the same historical trajectory to manually tune the decision mechanics (weights/thresholds) would use the target twice: once to define the baseline, and again to force the mechanism. This destroys the validity of the ABM's mechanistic output.
*   **Correct Approach:** Structural properties and reachability mapping (ensuring logical pathways are mechanically accessible) must guide threshold configuration.

## 4. Parameter Space Classification (Phase F)
Based on sensitivity mapping (`outputs/validation/phase_4e_3/`), we classify the threshold space as follows:

1.  **DEAD:** `[0.3, 0.7]`
    *   *Characteristic:* Neither cognitive nor autonomous adoption is reachable under normal network conditions.
2.  **COGNITIVE-ACCESSIBLE (SELECTIVE-AUTONOMOUS):** `[0.05, 0.20]`
    *   *Characteristic:* Agents at $P_{90}+$ ($p_{base} \approx 0.0018$) with at least one infected neighbor ($score \approx 0.0007 + 0.02 + 0.04 = 0.06$) successfully cross the cognitive threshold (`0.05`) for LLM evaluation. Agents at $P_{max}$ with strong networks cross into autonomous adoption (`0.20`).
3.  **BROAD-AUTONOMOUS:** `[0.01, 0.05]`
    *   *Characteristic:* Median agents immediately enter LLM evaluation or autonomous adoption without any social influence.
4.  **RUNAWAY:** `[0.001, 0.01]`
    *   *Characteristic:* Massive unconditional cascades overriding heterogeneity.

## 5. Recommended Candidate Regime
The recommended operating regime is **COGNITIVE-ACCESSIBLE (`lower: 0.05, upper: 0.20`)**.
It correctly integrates the scale of the empirical ecological calibration while ensuring that:
1. Social diffusion (SIR) acts as a strict requirement for median-propensity households to enter deliberation.
2. High-propensity households can autonomously bridge into deliberation.
3. The LLM router activates selectively on ambiguous agents, rather than being bypassed or overwhelmed.

*Note: The recommended regime is identified but has NOT been implemented in production yet, per the phase instructions.*
