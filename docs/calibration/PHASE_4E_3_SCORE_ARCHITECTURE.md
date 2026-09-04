# Phase 4E.3: Score Architecture Analysis

## 1. Score Definition
The core decision logic of `ConsumerAgent` calculates an `adoption_probability` (referred to as `score`) using a fixed linear combination of three normalized components:
```python
score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
```

## 2. Component Ranges
*   **`p_base`:** Sigmoid output bounded exactly in $[0.0, 1.0]$. In empirical mode, this is computed via `EmpiricalBaselineProvider`.
*   **`sir_score`:** Independent infection probability formula: $1.0 - (1.0 - \beta)^{I}$, where $I$ is the number of infected neighbors. Bounded exactly in $[0.0, 1.0]$ for $\beta \in [0.0, 1.0]$.
*   **`affordability`:** $\min(\text{subsidy} / \max(\text{price}, 1.0), 1.0)$. Bounded exactly in $[0.0, 1.0]$ assuming non-negative prices and subsidies.

## 3. Weight Constraints
The current hardcoded weights are:
*   `w_base` = 0.4
*   `w_sir` = 0.4
*   `w_affordability` = 0.2
Sum of weights equals 1.0, ensuring the final score perfectly remains within $[0.0, 1.0]$.

## 4. Threshold Semantics & Routing Branches
The ABM defines two explicit configuration boundaries:
*   `lower_threshold` (default `0.3`)
*   `upper_threshold` (default `0.7`)

The routing branches are evaluated exactly in this sequence:
1.  **Immediate Adoption:** `if score >= upper_threshold`
    *   Household autonomously accepts solar without deliberation. `decision_path = "rule"`.
2.  **Immediate Rejection (WAIT):** `elif score <= lower_threshold`
    *   Household deterministically rejects solar. `decision_path = "rule"`.
3.  **LLM Routing (Ambiguous):** `else` (meaning `lower_threshold < score < upper_threshold`)
    *   Household requires cognitive deliberation. Calls `llm_interface.decide()`. `decision_path = "llm"`.

No other hidden gates or constraints are evaluated for susceptibility before making this decision. Once adopted, agents transition to `sir_state = 1` (Infected), and post-recovery (`sir_state = 2`) they are no longer evaluated.
