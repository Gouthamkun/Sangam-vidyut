import os

README_CONTENT = """# Sangam Vidyut

Sangam Vidyut is an India-calibrated, bottom-up agent-based simulation for studying nonlinear residential rooftop-solar adoption under household heterogeneity, social-network diffusion, and policy feedback.

## Why This Project Exists

Can household-level heterogeneity, social networks, affordability, and policy feedback create adoption cascades that aggregate/static representations may not explicitly capture? 

Traditional equation-based forecasting structurally obscures early localized clustering, leading to artificially smooth curves that fail to predict tipping points or cascading failures under rigid budget constraints. Sangam Vidyut explicitly models these micro-level interactions to explore phase transitions. 

**Note:** This is a computational research model and theoretical testbed, not a validated national causal forecast of actual household behavior.

## How It Works

```text
Indian Data (HCES) 
  → Synthetic Households 
    → Economic Adoption 
      → Social Network/SIR 
        → Policy + Industry Feedback 
          → Aggregate Outcomes
```

- **ConsumerAgent**: Synthetic households localized on a network graph evaluating personalized adoption scores.
- **GovernmentAgent**: Allocates a finite fiscal budget and adjusts subsidies dynamically or statically.
- **IndustryAgent**: Scales base panel prices based on aggregate demand elasticity.
- **EnvironmentAgent**: Calculates standard CO2 emissions averted by the active solar panels.
- **AnalysisAgent**: Aggregates state-space metrics and enforces atomic data provenance.

## Data & Calibration

The simulation is fundamentally grounded using the **Indian Household Consumption Expenditure Survey (HCES 2023-24)**. 
- We utilize HCES survey weights to construct representative distributions of MPCE (Monthly Per Capita Expenditure).
- Macro constraints are mapped using MNRE benchmark costs, PM Surya Ghar targets, and the CEA domestic consumer denominator.

*Household calibration is strictly aggregate-consistent/ecological, not causal household-level identification.*

## Modeling Stack

- **Python** / **Mesa** (Agent-Based Modeling)
- **NetworkX** (Synthetic Topologies)
- **scikit-learn** / **PyTorch** / **pandas** / **numpy** (Data Processing)
- **LangGraph** / **Ollama** / **Pydantic** (Optional Cognitive Layer)
- **pytest** (Invariant Testing)
- **Plotly / Matplotlib** (Visualization)

The LLM is implemented purely as an *optional cognitive-routing layer* to resolve ambiguous decisions. Mesa remains strictly authoritative over the entire simulation state.

## The Core Mechanism

Adoption evaluates empirical propensity, social contagion, and financial friction.

`score = 0.4 * p_base + 0.4 * SIR_score + 0.2 * affordability`

- **Clear decision**: Mathematically routed (score >= 0.20 deterministically adopts; score <= 0.05 deterministically waits).
- **Ambiguous decision**: (0.05 < score < 0.20) Routed to the cognitive LLM provider.

## Key Findings

| Phase | Focus | Result |
|---|---|---|
| **Phase 4F.1** | Affordability Bottleneck | Absolute financial friction strictly blocks adoption regardless of network physics. |
| **Phase 4F.2** | Mechanism Activation | Topology, beta (contagion), and heterogeneity are conditionally active only within the narrow transition regime. |
| **Phase 4F.3** | Policy/Fiscal Interactions | Target-seeking dynamic policy defends cascades in active regimes but aggressively wastes capital attempting to force blocked regimes. |

**The model exhibits regime-dependent nonlinear behavior:** economic affordability determines whether diffusion can activate, while network structure, transmission, household heterogeneity, and fiscal/industry feedback influence behavior in the diffusion-active regime.

## Important Surprising Result (The Budget Paradox)

A crucial discovery in Phase 4F.3 is the budget-network feedback paradox caused by finite fiscal limits:

*Path A (Network ABM)*: rapid early network adoption → rapid subsidy expenditure → budget exhaustion → subsidy collapse → altered later affordability (cascade permanently stalls).

*Path B (Static Baseline)*: slower early adoption → budget preservation → continued industry price decline → later affordability improvement → delayed high adoption.

This is a **model-specific emergent mechanism** proving that ignoring early network clustering under strict budget constraints perversely results in mathematically over-optimistic final adoption forecasts.

## Experimental Scale

- **Phase 4F.1**: Completed (Affordability isolation)
- **Phase 4F.2**: 560 runs (Mechanism activation factorial)
- **Phase 4F.3**: 320 runs (Policy robustness factorial)

*(Note: N=500 households per simulation run. The scale evaluates fundamental mathematical interactions, but does not imply national statistical representativeness.)*

## Research Status

- [x] Phase 4F.1: Complete
- [x] Phase 4F.2: Complete
- [x] Phase 4F.3: Complete
- [x] Phase 5.1: Complete (Master Report)
- [x] Phase 5.2: Complete (Publication Figures)

## Limitations

- Aggregate/ecological calibration (not mapped to exact real-world individuals).
- No direct historical household adoption labels (forced use of proxy outcomes).
- Synthetic social networks (Barabási-Albert/Watts-Strogatz geometries rather than empirical geospatial graphs).
- N=500 experimental populations limits macro-clustering depth.
- The dynamic policy utilizes a model-specific target-seeking heuristic, not an optimized optimal-control algorithm.
- Contagion transmission (`beta`) is not yet empirically calibrated.
- MockLLM caching limitations bound cognitive experiments to algorithmic architectural tests rather than human semantic intelligence.
- **No causal claims** regarding real-world policy effects.

## Figures

![System Architecture](docs/figures/figure_01_architecture.png)
*Figure 1. Sangam Vidyut System Architecture.*

![Subsidy Response](docs/figures/figure_04_subsidy_response.png)
*Figure 2. Subsidy Response Curve.*

![Mechanism Regimes](docs/figures/figure_05_mechanism_activation.png)
*Figure 3. Mechanism Activation Regimes.*

![Policy Trajectories](docs/figures/figure_09_policy.png)
*Figure 4. Fixed vs Target-Seeking Dynamic Policy.*

![Efficiency Comparison](docs/figures/figure_10_efficiency.png)
*Figure 5. Dynamic Policy Efficiency Gains vs Fixed Base.*

![Budget Feedback](docs/figures/figure_11_budget_feedback.png)
*Figure 6. The Budget Exhaustion Paradox.*

## Quick Start

```bash
# 1. Environment Setup
python -m venv venv
source venv/bin/activate  # Or `venv\\Scripts\\activate` on Windows

# 2. Dependency Installation
pip install -r requirements.txt

# 3. Test Command (126/126 passing tests guaranteeing invariant physics and atomic persistence)
pytest -q

# 4. Example Simulation Command (Smoke test a single run)
python scripts/experiments/phase_4f_3_smoke_test.py
```

## Repository Structure

```text
src/          # Core Mesa simulation engine, agents, and LLM interfaces
experiments/  # Phase-specific execution definitions and runner logic
scripts/      # Orchestration, data generation, plotting, and execution scripts
tests/        # Pytest suite validating caching and model physics
schemas/      # Pydantic schemas enforcing output structure
docs/         # Master Research Reports, design specs, and figures
outputs/      # Persisted results (manifests, logs, aggregated CSVs)
data/         # Un-tracked raw empirical data (HCES / surveys)
```

## Reproducibility

Sangam Vidyut guarantees identical factorial reproduction via:
- Deterministic random seeds (`[42...51]`) mapped exactly across configurations.
- Immutable experiment manifests detailing every parameter constraint.
- Configuration hashing (`config_sha256`) and calibration bindings (`SHA-256: 0d5acf7...`).
- Atomic artifact persistence preventing corrupted mid-run data.
- Strict invariant checks (e.g. `S + I + R == N`) at every timestep.
- Seed-isolated cognitive caches guaranteeing zero contamination.
- **126 passing tests** continuously guarding simulation physics.

## Scientific Positioning

Sangam Vidyut is complementary to aggregate/system-dynamics energy-policy models rather than a replacement for them. It serves specifically to bound the error margins that occur when aggregate models ignore local network friction and temporal budget exhaustion. 

## Future Work

- Expanding population sizes (e.g. N=100,000+).
- Integrating real geospatial social-network data.
- Utilizing better household-level adoption labels.
- Validating physical system-size (kW) capacity distributions.
- Testing formal Reinforcement Learning policy-rule alternatives against the heuristic.
- External real-world validation and rigorous sensitivity/uncertainty analysis.
"""

def update_readme():
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    print("Successfully updated README.md")

if __name__ == "__main__":
    update_readme()
