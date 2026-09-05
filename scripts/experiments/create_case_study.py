import os

CASE_STUDY_CONTENT = """# Sangam Vidyut — Modeling Nonlinear Residential Solar Adoption

**An India-calibrated, agent-based computational laboratory for exploring social diffusion, household heterogeneity, and finite policy feedback loops.**

Sangam Vidyut is a bottom-up research simulation built to investigate how individual economic friction and local network clustering trigger cascading phase transitions in residential rooftop solar adoption.

---

## The Problem

Traditional national solar adoption forecasts rely on top-down, aggregate equations. While mathematically smooth, these models structurally obscure critical household-level interactions. They cannot "see" social contagion spreading through a neighborhood, nor can they accurately model what happens when sudden network clustering prematurely exhausts a finite government budget. 

By ignoring individual affordability constraints, heterogeneous household characteristics, and local social influence, aggregate representations often fail to predict tipping points or cascading failures under rigid macroeconomic limits.

---

## The Research Question

*How do finite fiscal constraints, industry price adjustments, and heterogeneous affordability interact with social network cascades to determine the trajectory of residential solar adoption?*

The core hypothesis explores whether adoption emerges differently when individual households interact through bounded local networks instead of being represented purely by top-down aggregate averages.

---

## What I Built

![System Architecture](../figures/figure_01_architecture.png)

I engineered a full-stack, reproducible Agent-Based Model (ABM) connecting micro-behavior to macro-economics.

**The Agents:**
- **ConsumerAgent**: Synthetic households situated on a network graph evaluating personalized adoption scores.
- **GovernmentAgent**: Allocates a finite fiscal budget, dispensing and conditionally adjusting subsidies.
- **IndustryAgent**: Scales base panel prices based on aggregate demand elasticity.
- **EnvironmentAgent**: Calculates standard CO2 emissions averted.
- **AnalysisAgent**: Aggregates state-space metrics and enforces atomic data provenance.

**The Tech Stack:**
- **Modeling**: Python, Mesa, NetworkX
- **Data & AI**: pandas, NumPy, scikit-learn, PyTorch
- **Cognitive Layer**: LangGraph, Pydantic, Ollama
- **Engineering**: pytest, Matplotlib, Seaborn

---

## Data & Calibration

The simulation is fundamentally grounded using the **Indian Household Consumption Expenditure Survey (HCES 2023-24)**. 

Using survey weights, I generated a synthetic, representative distribution of households, extracting Monthly Per Capita Expenditure (MPCE), sector, and dwelling characteristics. Macro constraints were mapped using MNRE benchmark costs, PM Surya Ghar targets, and the CEA domestic consumer denominator.

*Note: Calibration is strictly aggregate-consistent/ecological rather than causal household-level identification.*

---

## The Hard Engineering Problems

Building a reliable computational testbed required solving several deep engineering challenges:

**A. Empirical Calibration & Data Linkage**
*Problem*: Linking disparate Indian economic survey datasets (HCES) with physical energy denominators (CEA).
*Solution*: Ecological calibration bridging survey-weighted MPCE proxies to macro-level penetration targets.

**B. Deterministic Reproducibility**
*Problem*: ABMs are notoriously difficult to reproduce due to stochastic variance.
*Solution*: Strict factorial designs using matched seeds (`[42...51]`), explicit configuration hashing (`config_sha256`), and calibration SHA-256 bindings.

**C. Hybrid LLM Routing & Cognitive Caching**
*Problem*: Querying an LLM (even local Ollama/MockLLM proxies) for 1.1 million agent decisions is computationally impossible and stochastic.
*Solution*: Engineered a LangGraph ambiguity router with a strictly seed-isolated cognitive cache. It perfectly identified and bypassed 299,000 duplicate intra-timestep contexts without cross-seed contamination.

**D. Atomic Experiment Persistence**
*Problem*: Multi-hour parameter sweeps corrupting state upon interruption.
*Solution*: Engineered atomic artifact persistence with explicit JSON/CSV checkpoints. A 560-run campaign can be paused, validated, and cleanly resumed.

---

## Scientific Experiment Program

The model was subjected to 3 rigorously isolated experimental phases across N=500 synthetic household networks:

1. **Phase 4F.1 (Affordability Bottleneck)**: Isolated economic friction from network physics.
2. **Phase 4F.2 (Mechanism Activation)**: A **560-run factorial** across subsidies to locate exact transition thresholds.
3. **Phase 4F.3 (Policy Robustness)**: A **320-run campaign** comparing fixed vs target-seeking dynamic policies under a finite budget.

---

## The Most Interesting Finding: The Budget–Network Paradox

![Budget Exhaustion Paradox](../figures/figure_11_budget_feedback.png)

The most surprising emergent result was discovered when auditing the Static vs ABM comparison under finite fiscal limits.

**Path A (Network ABM)**: Rapid network adoption → rapid subsidy spending → finite budget exhaustion → subsidy collapse → later adoption permanently stalls.

**Path B (Static Baseline)**: Slower early adoption → budget preserved → industry price decline continues → later affordability improves → delayed massive adoption cascade.

This paradox proves that an aggregate static model can mathematically *overstate* final adoption because it ignores the fiscal reality of early network clustering. This is an emergent behavior of the implemented computational system, not a universal empirical law.

---

## Key Results

Based on the explicit `CLAIM_EVIDENCE_MATRIX.md`:

- **Subsidy Bottlenecks**: `SUPPORTED`. Financial friction strictly blocks adoption regardless of network physics.
- **Topology (BA vs WS)**: `CONDITIONALLY_SUPPORTED`. Network geometry only alters adoption within narrow active transition regimes.
- **Beta (Contagion)**: `CONDITIONALLY_SUPPORTED`. Transmission rates alter velocity but cannot override base affordability blocks.
- **Household Heterogeneity**: `CONDITIONALLY_SUPPORTED`. Variance in population affordability smooths out phase-transition cliffs.
- **Target-Seeking Dynamic Policy (H2)**: `CONDITIONALLY_SUPPORTED`. Protects cascades in active regimes, but aggressively wastes capital attempting to force blocked regimes.
- **Static vs Dynamic Forecasts (H3)**: `NOT_SUPPORTED`. Initial hypotheses assumed static models understate ABMs; the opposite was proven true under strict budget constraints.
- **Cognition**: `NOT_SUPPORTED`. No aggregate cognitive advantage over deterministic mathematics was detected.

---

## Why the LLM is Not the Headline

Sangam Vidyut uses LLMs strictly as an *optional ambiguity-routing layer*, not as a forecasting gimmick. 

The decision mechanism is mathematically rigid:
`score = 0.4*p_base + 0.4*SIR_score + 0.2*affordability`

- **Clear decision (score >= 0.20 or <= 0.05)** → Mathematical deterministic route.
- **Ambiguous decision (0.05 < score < 0.20)** → LLM cognitive route.

Using MockLLM and local Ollama integrations via LangGraph and Pydantic structured outputs, I proved the architectural stability of the cache. However, I explicitly found that *no aggregate cognitive advantage was detected in the tested configuration*. The true mechanism driving the system was the macroeconomic feedback loop.

---

## Reproducibility as a Core Feature

Research software is useless if it cannot be replicated. Sangam Vidyut is guarded by:
- **126 passing tests** (`pytest -q`) verifying SIR invariants and caching logic.
- Explicit experiment manifests detailing every parameter constraint.
- Configuration and Calibration `SHA-256` hashing.
- Strict matched-seed experimental geometries.

---

## What I Learned

1. **Complex models are often dominated by simple bottlenecks**: Despite building complex scale-free network contagions, basic household affordability strictly blocked all physics.
2. **Aggregate calibration ≠ Causal identification**: Using proxy data allows for robust system dynamics exploration, but it fundamentally prevents drawing real-world individual behavioral conclusions.
3. **Reproducibility must be engineered**: Caching 1.1 million LLM calls securely across parallel multiprocessing threads requires strict state isolation and invariant checking.
4. **Negative results expose architectural truths**: Discovering that the ABM underperformed the Static model (H3) forced a deep audit that exposed the beautiful budget-exhaustion paradox.
5. **LLM integration requires strict boundaries**: Passing raw state to an LLM is chaotic; using structured outputs and mathematical thresholding to bound the LLM makes it a useful computational tool rather than a liability.

---

## Limitations

- **N=500 Scale**: Synthetic populations limit macro-clustering depth.
- **Synthetic Networks**: Relies on Barabási-Albert/Watts-Strogatz geometries rather than empirical geospatial data.
- **Ecological Calibration**: Missing direct historical household adoption labels forces the use of aggregate outcome proxies.
- **Uncalibrated Contagion**: Beta transmission is theoretically parametrized.
- **Model-Specific Heuristics**: The dynamic policy uses a simple target-seeking rule, not an optimized control algorithm.
- **MockLLM Bounds**: Evaluates algorithmic caching architecture, not human semantic intelligence.
- **No Causal Claims**: The simulation is a theoretical computational testbed, not a real-world policy predictor.

---

## Technology / Skills Used

- **Modeling**: Mesa (Agent-Based Modeling), SIR Diffusion, NetworkX
- **Machine Learning**: scikit-learn, Logistic Regression, PyTorch
- **AI Integration**: LangGraph, Pydantic, Ollama, Structured Outputs
- **Data Engineering**: pandas, NumPy, Survey Weighting, ETL
- **Software Engineering**: Python, pytest, Reproducibility, Configuration Hashing, Atomic Persistence, Experiment Orchestration
- **Visualization**: Matplotlib, Seaborn

---

## Portfolio Links

- [GitHub Repository](#)
- [Master Research Report](MASTER_RESEARCH_REPORT.md)
- [Project README](../../README.md)
- [Figures Directory](../figures/)
- [Streamlit Dashboard (Coming Soon)](#)

---

**Sangam Vidyut is a computational laboratory for studying how economic constraints, heterogeneous households, social networks, finite policy budgets, and industry responses interact to produce regime-dependent residential solar adoption dynamics.**
"""

def create_case_study():
    path = "docs/research/PORTFOLIO_CASE_STUDY.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(CASE_STUDY_CONTENT)
    print(f"Successfully created {path}")

if __name__ == "__main__":
    create_case_study()
