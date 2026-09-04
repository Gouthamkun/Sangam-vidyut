# Phase 4E.5: Threshold Policy Validation

## 1. Motivation
Phase 4E.4 established that the empirical baseline ($P_{max} \approx 0.111$) mathematically stalls adoption under the inherited Phase 4C thresholds (`0.30, 0.70`). The linear score family preserves the existing mathematical score structure perfectly. However, changing thresholds creates a distinct behavioral regime. We aim to test whether shifting to a new candidate policy (`0.05, 0.20`) restores scientific utility without resorting to arbitrary target curve fitting.

## 2. Threshold Semantics
*   **Legacy Reproducibility:** Legacy Phase 4C reproducibility is preserved strictly through the explicit legacy provider and configuration path (`legacy_defaults`).
*   **Behavioral Regime:** By shifting thresholds, we decouple the historical illustrative values from the empirical mechanics, mapping empirical propensity to cognitive pathways appropriately.

## 3. Candidate Policies
*   **Policy 0 (DEAD BASELINE):** `lower = 0.30`, `upper = 0.70`.
*   **Policy 1 (CANDIDATE):** `lower = 0.05`, `upper = 0.20`.
*   *(Intermediate structural variants generated for theoretical testing: [0.10, 0.30] and [0.15, 0.40])*

## 4. Reachability
Under Policy 0, cognitive and autonomous paths were completely inaccessible. 
Under Policy 1 (`0.05, 0.20`), the 500-agent empirical population demonstrates correct reachability:
*   High `p_base` agents cross into cognitive evaluation even under baseline affordability.
*   Median agents require social influence (`sir_score`) to breach the `0.05` threshold.
*   Autonomous adoption (`0.20`) requires a powerful convergence of extreme empirical propensity, high subsidy, and strong network effects.

## 5. Household Heterogeneity
Heterogeneity is perfectly preserved and visible:
*   $Q_1$ (Lowest empirical propensity) remains locked in WAIT under standard conditions.
*   $Q_5$ (Highest empirical propensity) easily reaches Cognitive/LLM deliberation thresholds.
*   Therefore, the model ensures empirical household features meaningfully restrict behavioral pathways without demanding non-linear normalizations.

## 6. Social Diffusion
When testing Policy 1 on Watts-Strogatz and Barabási-Albert topologies across $\beta \in [0.05, 0.15, 0.30]$:
*   Social diffusion remains highly relevant.
*   Even under strong diffusion ($\beta=0.30$), Policy 1 correctly suppresses unconditional runaway adoption, restricting successful adoptions to the cognitive logic rather than blindly accepting everyone via the autonomous threshold.

## 7. Economic Sensitivity
Subsidy scaling (0, 1000, 5000 INR) successfully shifts the score up, bridging the gap to the `0.05` cognitive threshold for median agents, proving the affordability vector is intact and meaningful under the new policy.

## 8. Cognitive Routing Validation
Using the `MockLLMProvider`, Policy 1 dynamically triggers LLM evaluation for ambiguous agents inside the `[0.05, 0.20]` window, avoiding the computational waste of testing guaranteed-reject agents while engaging the cognitive mechanism properly for households on the decision margin.

## 9. Stress Test (Selectivity / Runaway Test)
Under maximum stress ($\beta=0.8$, Subsidy=$5000$, Barabási-Albert hubs):
*   Policy 1 generates *selective autonomous* cascades for highly connected affluent nodes.
*   It does *not* trigger broad or runaway mass-adoption, demonstrating mathematically safe firewalls.

## 10. Legacy Reproducibility
A regression test under `Policy 0` with `baseline_provider = "legacy"` successfully replicated the Phase 4C baseline mechanics perfectly, confirming the structural modifications are strictly opt-in and do not corrupt historical logic.

## 11. Selection Criteria
Policy 1 was evaluated against the mandate:
1. Cognitive deliberation is reachable. (Pass)
2. Autonomous adoption remains selective. (Pass)
3. Household heterogeneity remains visible. (Pass)
4. Social diffusion matters. (Pass)
5. Affordability matters. (Pass)
6. No unconditional runaway adoption. (Pass)
7. No empirical target leakage. (Pass)
8. Legacy mode remains reproducible. (Pass)

## 12. Final Recommendation
Policy 1 (`0.05, 0.20`) is strictly validated for its mathematical properties and designated:
**CANDIDATE OPERATING POLICY — VALIDATED FOR EXPERIMENTAL USE**
*Note: This is an architectural validation, not an empirical calibration or real-world behavioral validation.*

## 13. Limitations
This candidate policy establishes the geometric reachability required to conduct agentic experiments. It makes no claim to producing a perfectly calibrated final solar adoption curve matching true aggregate history.
