# Phase 4E.4: Behavioral Mechanism Design and Operating-Regime Study

## 1. Problem Statement
The ABM effectively stalled in Phase 4E.2 because the new empirical household propensities (max $\approx 0.111$) are structurally incompatible with the legacy decision threshold assumptions (`upper_threshold = 0.7`). This mathematically locked the population in a DEAD regime where neither cognitive evaluation (LLM) nor autonomous adoption could be triggered, regardless of social diffusion or extreme subsidies.

## 2. Current Architecture & Semantics (Phase A)
*   **`p_base`:** An aggregate-calibrated simulation prior mapping a household's demographic/economic properties to a relative baseline likelihood of adopting solar. It is *not* an individually identified real-world adoption probability.
*   **`sir_score`:** A $[0, 1]$ scalar representing the strength of social diffusion/infection pressure.
*   **`affordability`:** A $[0, 1]$ scalar indicating the fraction of the system price covered by subsidies.
*   **Weighted Score:** A continuous latent parameter measuring the combined adoption pressure.
*   **`lower_threshold`:** The boundary below which adoption is deterministically rejected (WAIT).
*   **`upper_threshold`:** The boundary above which adoption is deterministically accepted (ADOPT).
*   **Cognitive Ambiguity:** The interval between these thresholds represents households under conflicting or moderate pressure where rule-based heuristics fail, necessitating LLM evaluation.

## 3. Scale Mismatch (Phase B)
The component decomposition (`outputs/validation/phase_4e_4/score_component_decomposition.csv`) reveals:
*   Max `p_base` contribution: $0.4 \times 0.11145 \approx 0.044$
*   Max `sir` contribution: $0.4 \times 1.0 = 0.4$
*   Max `aff` contribution: $0.2 \times 1.0 = 0.2$
Total maximum possible theoretical score = `0.644`, which strictly prevents reaching `0.7`.
Most realistic configurations peak around `0.15 - 0.25`, rendering even the `0.3` cognitive boundary unreachable.

## 4. Decomposing the Design (Phase C)
The current architecture successfully splits the logic into:
1.  **Adoption Pressure** (the score calculation).
2.  **Decision Policy** (the threshold logic).
By maintaining this split, we can shift the Decision Policy (thresholds) to match the Adoption Pressure (score scale) without fundamentally warping the empirical probabilities.

## 5. Candidate Mathematical Families (Phase D)
1.  **Current Linear:** `w1*p_base + w2*sir + w3*aff`
    *   *Advantage:* Simple, additive, bounded.
    *   *Disadvantage:* Score magnitude tied directly to empirical base scale.
2.  **Normalized Empirical-Pressure:** `w1*norm(p_base) + w2*sir + w3*aff`
    *   *Advantage:* Reaches 1.0 easily.
    *   *Disadvantage:* Destroys true probabilistic meaning of `p_base`; artificially inflates small variance.
3.  **Additive Social/Economic Pressure:** `p_base + a*sir + b*aff`
    *   *Advantage:* Treats `p_base` as true probability, modifies via offsets.
    *   *Disadvantage:* Breaks legacy parameter weighting schema.
4.  **Odds/Logit Combination:** `sigmoid(logit(p_base) + a*sir + b*aff)`
    *   *Advantage:* Statistically principled handling of probabilities.
    *   *Disadvantage:* Small empirical `p_base` (e.g., $10^{-4}$) creates massive negative logits ($-9$) that overwhelm any reasonable modifiers, ensuring a DEAD regime.

## 6. Regime Definitions (Phase E)
*   **DEAD:** No agent can cross thresholds.
*   **COGNITIVE-ACCESSIBLE:** Median households enter LLM via social influence; high-propensity households enter autonomously.
*   **SELECTIVE-AUTONOMOUS:** Adoption requires strict convergence of high propensity and network effect.
*   **BROAD-AUTONOMOUS:** Mass immediate adoption; LLM bypassed.
*   **RUNAWAY:** Unconditional adoption independent of heterogeneity.

## 7. Legacy vs Empirical Analysis (Phase F)
In the legacy model, `p_base` dummy calculations effectively equated to `0.0`, masking the threshold gap since the baseline had no true variability. The empirical model introduces critical, structured variance between `0.00001` and `0.111`. Designs like normalization (Family 2) collapse this true heterogeneity, whereas the Linear (Family 1) and Additive (Family 3) preserve the shape precisely.

## 8. Target Leakage Safeguards (Phase G)
We explicitly prohibit tuning weights or thresholds to match PM Surya Ghar target curves. Thresholds must be selected *mechanistically* to ensure the cognitive and autonomous branches are reachable by the structural variance of the population (e.g., bridging the gap between $P_{50}$ and $P_{99}$ with reasonable network effects).

## 9. Candidate Ranking & Selection (Phase H)
1.  **Current Linear (Family 1)** combined with adjusted COGNITIVE-ACCESSIBLE thresholds.
2.  **Additive (Family 3)**.
3.  **Logit (Family 4)**.
4.  **Normalized (Family 2)**.

## 10. Recommended Design
We recommend **Candidate Family 1: CURRENT LINEAR (with shifted COGNITIVE-ACCESSIBLE thresholds: `[0.05, 0.20]`)**. 
It preserves linear predictability and legacy reproducibility perfectly. It maps the empirical scale into behavioral ranges without mathematically complex distortions (F4) or artificial normalizations (F2) that destroy the relative differences among households.

## 11. Limitations
The selected mechanism is an agentic abstraction. It guarantees reachability for the LLM deliberator but remains a mechanistic proxy, not a statistically fitted individual causal model.
