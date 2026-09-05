# PHASE 4F.3 — POLICY ROBUSTNESS & DECISION-RELEVANCE (PRE-FLIGHT DESIGN)

## 1. Scientific Objectives
Phase 4F.2 successfully mapped the unconditional boundaries of the system, establishing exactly when network mechanisms transition from *AFFORDABILITY-BLOCKED* to *DIFFUSION-ACTIVE* and *SATURATED*. 

Phase 4F.3 shifts the focus from structural mapping to **Policy Robustness and Decision-Relevance**. The objective is to determine whether the regime-dependent network laws uncovered in Phase 4F.2 produce robust and policy-relevant conclusions. Specifically, we will test whether a target-seeking dynamic subsidy policy can achieve the equivalent macroscopic cascades as brute-force saturated subsidies, but at significantly higher fiscal efficiencies, and whether these policy conclusions remain stable across underlying network topologies.

## 2. Explicit Hypotheses
* **H1 (Policy Efficiency)**: Fixed subsidies positioned strictly in the diffusion-active transition regime (e.g., 3000) yield a mathematically higher marginal efficiency (adoptions per unit cost) compared to saturation-level subsidies (5000), because the cascade is structurally accelerated by network effects rather than purely funded by the state.
* **H2 (Dynamic Effectiveness)**: A target-seeking dynamic subsidy policy achieves an *equivalent cascade* to saturated fixed policies, but at a significantly reduced total fiscal expenditure.
* **H3 (Structural Robustness)**: The predicted policy conclusions (expenditure constraints and time-to-target efficiency) remain stable across the underlying synthetic topology (Watts-Strogatz vs. Barabási-Albert) and household heterogeneity, acting only as variance boundaries on the policy frontier.
* **H4 (Static Underestimation)**: Static/reference modeling will systematically understate adoption trajectory and/or policy efficiency relative to the dynamic ABM in diffusion-active regimes.

## 3. Exact 320-Run Factorial
* **Deterministic**: 5 subsidies × 2 policy modes (FIXED, DYNAMIC) × 2 topologies (WS, BA) × 10 matched seeds = **200 runs**.
* **Static**: 5 subsidies × 2 topologies (structural match) × 10 matched seeds = **100 runs**.
* **Cognitive**: 2 topologies × 10 matched seeds at subsidy=3000 using a SINGLE policy mode (`FIXED`) = **20 runs**.

*Confirmation*: 200 + 100 + 20 = **320 runs**.

* **Base Subsidies**: 1000, 2000, 3000, 4000, 5000
* **Beta Transmission Rate**: 0.15 (Locked)
* **Population**: 500
* **Horizon**: 24 quarters
* **Seeds**: 10 unique paired seeds (42 through 51)

## 4. Freeze the Dynamic Policy Algorithm
The DYNAMIC policy (`target-seeking dynamic subsidy policy`) executes the following exact deterministic rule at every time step:
* **Initial Subsidy**: `config.government.base_subsidy`
* **Target Adoption**: 50% (`config.government.target_adoption_rate = 0.5`)
* **When Evaluated**: Every step, by the `GovernmentAgent`.
* **Information Available**: 
  - `model.new_adoptions_last_step`
  - `model.total_adopters`
  - `model.config.simulation.n_agents`
* **Expenditure Calculation**: `spent = new_adoptions_last_step * current_subsidy`
* **Budget Exhaustion Behavior**: The budget is reduced by `spent`. If `budget <= 0.0`, it is clamped to `0.0`, the `subsidy` is forced to `0.0`, and the policy terminates (no further adjustments).
* **Subsidy Adjustment Rule**:
  - `current_rate = total_adopters / n_agents`
  - *If `current_rate < target_adoption_rate` (Target Not Reached)*:
    - Increase subsidy by 5%: `proposed = current_subsidy * 1.05`
    - Apply affordability cap: `subsidy = min(proposed, budget / max(1, new_adoptions_last_step))`
  - *If `current_rate >= target_adoption_rate` (Target Reached Behavior)*:
    - Reduce subsidy by 5%: `subsidy = current_subsidy * 0.95`
* **Allowed Subsidy Values/Range**: Lower bound implicitly approaches `0.0`. Upper bound dynamically capped by the remaining budget divided by the previous step's demand rate.
* **Termination Behavior**: Policy continues scaling down post-target indefinitely, or locks at exactly `0.0` permanently if the budget hits 0.

## 5. Formalize Policy Efficiency
Efficiency metrics will be strictly calculated as:
* **Raw Total Subsidy Expenditure**: Output in raw dollar units.
* **Policy Efficiency**: `new_adoptions / (total_subsidy_expenditure / 1,000,000)`
* **Emissions Efficiency**: `(total_adopters * kw_per_panel * co2_per_kw) / (total_subsidy_expenditure / 1,000,000)`

## 6. Formalize 'Equivalent Cascade'
A target-seeking dynamic policy will be considered to have produced an *equivalent cascade* to a saturated fixed policy if, and only if, all of the following predeclared tolerances are met:
* **Final Adoption**: Within ±5% (absolute rate).
* **Time-to-50%**: Within ±2 quarters.
* **Tipping Probability**: Equal (±0%).
* **Peak Adoption Velocity**: Within ±10%.

## 7. Fiscal Outcomes
Every dynamic-policy run will rigidly track and record:
* Initial budget
* Total expenditure
* Quarter of budget exhaustion (if applicable)
* Subsidy at exhaustion
* Adoption at exhaustion
* Whether the 50% target was reached before exhaustion
* Whether saturation (>=95%) was reached

## 8. Artifact Structure
Data will persist identically to Phase 4F.2 to guarantee tooling compatibility:
* `outputs/experiments/phase_4f_3/manifests/`
* `outputs/experiments/phase_4f_3/raw/`
* `outputs/experiments/phase_4f_3/tables/`
* `outputs/experiments/phase_4f_3/reports/phase_4f_3_report.md`

## 9. Provenance Requirements
* Empirical calibration SHA-256 must match exactly across all 320 manifests.
* Every manifest must record `config_sha256` matching the exact instantiated schema state.
* Model code will remain completely unmodified.

## 10. Quality Gates
* **Test Matrix**: Existing `pytest -q` regression suite must pass before execution.
* **S+I+R Invariant**: `S + I + R = N` must hold for every step of all 320 trajectories.
* **Cache Audit**: Cognitive cross-seed cache hits must strictly equal `0`.
* **Matched-Seed Integrity**: Exact seed arrays must enforce isolation of structural variance from stochasticity across the paired baseline sets.
