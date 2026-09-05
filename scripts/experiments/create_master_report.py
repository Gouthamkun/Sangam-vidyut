import os

REPORT_CONTENT = """# Sangam Vidyut: Master Research Report

## 1. Abstract
The transition to rooftop solar is fundamentally a socio-technical challenge governed by both economic friction and localized peer effects. We present Sangam Vidyut, an Agent-Based Model (ABM) grounded in an empirical calibration of Indian household data (HCES 2023-24) to simulate residential solar adoption. The framework explicitly links heterogeneous household affordability, SIR-based social network diffusion, and macro-level feedback from industry pricing and finite government fiscal budgets. We evaluate these dynamics across three experimental phases utilizing a robust factorial design and an optional hybrid LLM cognitive layer. The results demonstrate that affordability acts as an absolute bottleneck to adoption (Phase 4F.1); alleviating this bottleneck activates highly nonlinear, topology-dependent diffusion cascades (Phase 4F.2); and imposing strict government budget constraints fundamentally alters the trajectory, heavily punishing premature network clustering (Phase 4F.3). These findings highlight that static aggregate representations systematically mischaracterize adoption curves when fiscal limits apply. The simulation serves as a computational testbed for structural mechanisms, though real-world causal prediction is explicitly not claimed.

## 2. Introduction
Rooftop solar adoption represents a complex, non-linear socio-technical problem. Traditional top-down, aggregate models utilize static equations that often smooth out the localized clustering behavior fundamental to human decision-making. These models frequently fail to represent how sudden tipping points or cascading failures materialize under finite government budgets and dynamically updating price signals. Sangam Vidyut addresses these limitations by embedding household-level heterogeneity and social diffusion within a rigid macroeconomic feedback loop, explicitly investigating how policy interventions interact with the non-linear physics of network adoption. 

The primary research question is: *How do finite fiscal constraints, industry price adjustments, and heterogeneous affordability interact with social network cascades to determine the trajectory of residential solar adoption?*

## 3. Related Modeling Approaches
Sangam Vidyut bridges conventional system-dynamics approaches (which govern macro-flows of budgets and prices) and agent-based models (which govern micro-interactions and heterogeneity). Rather than replacing traditional diffusion models (like Bass diffusion), it integrates a localized SIR (Susceptible-Infectious-Recovered) mechanic over discrete synthetic networks. Additionally, the architecture optionally incorporates generative agents (LLMs) specifically as an architectural integration layer to map boundedly rational ambiguity, positioning the model as a hybrid numerical-cognitive simulation. We do not claim novelty as the "first LLM solar model," but rather focus strictly on the structural integration of empirical Indian household data, finite-budget feedback loops, and ABM network physics.

## 4. System Architecture
Sangam Vidyut operates within the Mesa framework and relies on NetworkX for synthetic topology mapping. The system comprises four distinct components:
- **ConsumerAgent**: Individual households localized on a network graph. They calculate adoption scores based on individual affordability and neighbor infection rates.
- **GovernmentAgent**: Manages a finite initial budget and adjusts subsidies based on configurable policies (fixed vs. target-seeking dynamic).
- **IndustryAgent**: Adjusts base panel prices conditionally based on aggregate recent adoption demand.
- **EnvironmentAgent**: Calculates standard CO2 emissions averted by active panels.
- **AnalysisAgent**: Aggregates state-space metrics for observability.

Social contagion is managed via localized SIR transmission physics. Cognitive routing is managed via LangGraph, utilizing either a deterministic `MockLLM` for computational rigor or local `Ollama` models.

## 5. Indian Data & Calibration
The synthetic population is grounded using the Indian Household Consumption Expenditure Survey (HCES 2023-24). Survey weights are applied to align the synthetic agents with representative empirical distributions. 
- **Features utilized**: Derived MPCE, household size, sector, dwelling type, electricity access, and free electricity quotas. 
- **Macro constraints**: The CEA domestic consumer denominator and MNRE benchmark costs structurally define affordability.

**Calibration Limitations**: The calibration is purely ecological and aggregate-consistent. Crucially, the model lacks direct household-level solar adoption labels, verifiable system-size distributions, direct income mappings, and empirically mapped physical social networks. Consequently, household-level predictions are mathematically valid within the proxy space but causally unsupported in the real world.

## 6. Household Model
The decision to adopt solar relies on a composite score representing empirical propensity, social pressure, and economic friction. The mathematical structure is strictly implemented as:

`score = 0.4 * p_base + 0.4 * SIR_score + 0.2 * affordability`

- **p_base**: The empirically fitted baseline probability derived from household characteristics.
- **SIR_score**: Evaluated as `1.0 - (1.0 - beta)^infected_neighbors`.
- **affordability**: Bounded ratio of available subsidy to the current panel price.

**Hybrid Decision Routing**: 
Scores map to three distinct zones defined by upper and lower thresholds. High scores result in deterministic adoption; low scores result in deterministic waiting. Scores falling in the middle ambiguity zone are computationally routed to the cognitive layer (LLM Provider) for resolution.

## 7. Social Network & SIR
Agents are structured within synthetic topologies (Watts-Strogatz and Barabási-Albert). Social exposure is strictly constrained to directly connected neighbors. 
- **Transmission (beta)**: The probability that an infected neighbor transmits the adoption signal per quarter.
- **SIR states**: Susceptible (0), Infectious (1), Recovered (2). Agents are infectious for a finite period post-adoption before transitioning to recovered, signifying the end of their active conversational influence. 
This provides a rigorous contagion mechanic, though we explicitly avoid overstating strict mathematical equivalence with biological epidemic models.

## 8. Policy & Feedback
The macroeconomic environment enforces strict feedback loops:
- **Government Subsidy & Finite Budget**: The government allocates a hard-capped budget. Every adoption linearly deducts from this reserve. If exhausted, subsidies crash to zero.
- **Industry Price Response**: Periods of low aggregate demand trigger industry price drops, while high demand artificially inflates prices.

**The Emergent Mechanism**:
A fundamental finding of the model is the budget-exhaustion paradox. 
*Path A (Network Clustering)*: Early network-driven adoption → faster subsidy spending → earlier budget exhaustion → sudden subsidy collapse → permanent affordability destruction for late adopters.
*Path B (Delayed Adoption)*: Slower early adoption → budget preservation → continued industry price decline → later affordability improvement → large delayed mass-adoption cascades.
This explicitly highlights a structural model mechanic, not a universal real-world law.

## 9. Cognitive Layer
The cognitive layer exists as an architectural and behavioral ablation. Ambiguous decisions are routed through LangGraph, utilizing structured Pydantic outputs. For scale and determinism, experiments utilize a `MockLLM`, which deterministically simulates a bounded random walk around the mathematical score using seed-isolated caching. This strictly evaluates architectural routing, LLM caching integrity, and computational tracking mechanisms, explicitly NOT human cognitive reasoning or intelligence.

## 10. Experimental Methodology
Sangam Vidyut enforces absolute reproducibility: 
- Matched synthetic seeds across configurations.
- Checksummed configuration hashes (`config_sha256`) and explicit calibration SHA-256 bindings.
- Atomic persistence mechanisms preventing data corruption.
- Three progressive experimental phases isolating distinct causal mechanisms.

## 11. Phase 4F.1 Results (Economic Bottleneck)
Phase 4F.1 established that affordability acts as an absolute structural bottleneck. When subsidies were insufficient to cross the localized affordability thresholds, the network remained dormant. Regardless of the network structure (topology) or transmission rate (beta), adoption remained blocked unless the economic baseline shifted, proving that contagion physics are fundamentally constrained by economic reality.

## 12. Phase 4F.2 Results (Mechanism Activation)
Phase 4F.2 systematically executed 560 runs to map the activation thresholds. 
- **Mechanism Activation**: A strict transition regime exists. At subsidy levels below 2000, networks were blocked. Between 2000-3000, the networks achieved "diffusion-active" states. Above 4000, networks hit structural saturation.
- **Conditional Effects**: Network topology (Barabási-Albert vs Watts-Strogatz) and beta variations only impacted adoption velocities *conditionally*—specifically within the narrow 2000-3000 transition regime. Outside this regime, topology was mathematically irrelevant. 
- **Heterogeneity**: Increasing household variance widened the transition slope, preventing abrupt step-function adoption curves.

## 13. Phase 4F.3 Results (Policy Robustness)
Phase 4F.3 executed 320 runs analyzing a target-seeking dynamic policy against a strict 1,000,000 fiscal budget. 
- **H1 (Fiscal Efficiency)**: SUPPORTED. Fixed transition-regime subsidies (2000-3000) triggered wide network cascades per dollar spent, whereas saturated subsidies (4000-5000) instantly depleted the budget on a smaller initial wave.
- **H2 (Dynamic Policy)**: CONDITIONALLY_SUPPORTED. The target-seeking policy successfully protected the cascade and conserved budget fractionally in active regimes. However, in blocked regimes, it forced adoption artificially by maximizing expenditure and draining the budget instantly.
- **H3 (Static vs ABM)**: NOT_SUPPORTED. A mathematically rigorous audit proved the static baseline actually *overstated* final adoption under budget constraints. Removing network physics suppressed early adoption, which safely conserved the government budget. This delay allowed the static population to exploit ongoing industry price drops, eventually resulting in a massive delayed cascade. Conversely, the ABM's rapid early network clustering burned through the budget prematurely, crashing the subsidy and halting the cascade entirely. 
- **Cognitive Accounting**: 1,163,720 total evaluations yielded exactly zero cross-seed cache contamination, verifying architectural stability.

## 14. Cross-Phase Synthesis
The simulation reveals a profound nested hierarchy:
**AFFORDABILITY** dictates **INITIAL ADOPTION**, which seeds **SOCIAL DIFFUSION**. The resulting **NETWORK EFFECTS** aggressively accelerate demand, triggering a severe **FISCAL FEEDBACK** loop that exhausts budgets prematurely. This interacts with the **INDUSTRY PRICE RESPONSE**, ultimately defining the **POLICY OUTCOME**. Each phase exposed a layer of this dependency, proving that focusing purely on network physics without enforcing rigid macroeconomic boundaries yields fundamentally incorrect predictions.

## 15. Consolidated Evidence Table

| Question/Hypothesis | Phase | Evidence Status | Key Result | Regime/Conditions | Limitation |
|---|---|---|---|---|---|
| Q1 ABM vs Static | 4F.3 | SUPPORTED | ABM exhausts budget earlier, halting cascades | Finite Budget Regimes | Specific budget exhaustion rule |
| Q2 Topology | 4F.2 | SUPPORTED | BA topology accelerates tipping | Diffusion-Active Transition Regime (Subsidy 2000-3000) | Synthetic N=500 graphs |
| Q3 Beta | 4F.2 | SUPPORTED | Higher beta narrows the transition threshold | Diffusion-Active Transition Regime | Beta uncalibrated empirically |
| Q4 Heterogeneity | 4F.2 | SUPPORTED | Variance correlates with adoption slope | All Regimes | Quantile proxy mappings |
| Q5 Subsidy | 4F.1/2 | SUPPORTED | Strict nonlinear threshold limits | Unconditional | Fixed baseline elasticity |
| Q6 Cognitive Layer | 4F.3 | SUPPORTED | Cache architecture correctly maps ambiguity | Unconditional | MockLLM heuristic proxy |
| H1 Policy Efficiency | 4F.3 | SUPPORTED | Transition subsidies yield highest adoption per dollar | Unconditional | Simplified efficiency definition |
| H2 Dynamic Policy | 4F.3 | CONDITIONALLY_SUPPORTED | Secures cascade in active states; wastes budget in blocked | Diffusion-Active & Saturated Regimes | Heuristic rule-based agent |
| H3 Static > ABM | 4F.3 | NOT_SUPPORTED | Static model overstates adoption by conserving budget | Finite Budget Regimes | Model-specific mechanics |

## 16. Scientific Contribution
Sangam Vidyut provides an empirical-calibrated computational framework for studying regime-dependent residential solar adoption where affordability, heterogeneous households, social-network diffusion, finite subsidies, and industry price feedback interact. It explicitly avoids causal identification, national forecasting accuracy, universal policy superiority, or proof of human-like LLM cognition. It stands purely as a rigorous theoretical testbed for complex socio-economic feedback loops.

## 17. Policy Implications
MODEL-BASED POLICY IMPLICATIONS:
- **Subsidy Thresholds**: Identifying the exact transition regime prevents catastrophic capital waste in saturated zones.
- **Fiscal Constraints**: Aggressive early adoption can lead to premature budget exhaustion, unintentionally permanently locking out the late-majority.
- **Dynamic Feedback**: Policy evaluations must dynamically recalculate affordability relative to shifting industry prices, as static subsidies risk outliving their optimal window of influence.

## 18. Limitations
- **N=500 Limit**: Synthetic scale limits macro-level clustering representation.
- **Ecological Calibration**: Limits strict household-level accuracy.
- **Proxy Labels**: Missing direct historical adoption labels forces the use of aggregate outcome proxies.
- **Synthetic Networks**: Fails to capture real-world geospatial and socio-demographic assortativity.
- **Model-Specific Rules**: Behavioral thresholds and the target-seeking heuristic are explicitly hardcoded parameters.
- **MockLLM bounds**: The cognitive layer currently evaluates algorithmic stability, not semantic intelligence. 
- **Causality**: The framework is strictly observational and computational, incapable of inferring causal household effects.

## 19. Reproducibility
The Git repository preserves strict semantic versioning. Experiment manifests, locked configuration hashes (`config_sha256`), and identical seed lists (`[42...51]`) guarantee bitwise exact reproduction. Data provenance is ensured via the calibration artifact SHA-256 (`0d5acf7...`). Execution paths (`pytest -q` followed by `scripts/experiments/phase_4f_X_campaign.py`) reliably persist raw trajectory CSVs directly to disk.

## 20. Future Work
Future computational research must pivot toward scaling the topology (e.g., N=100,000 empirical network graphs) and substituting the proxy mechanism for richer, observed real-world network data. Methodological extensions require stronger household-level historical adoption labels, validated system-size distributions, alternative policy control algorithms (e.g., deep reinforcement learning), explicit sensitivity/uncertainty bounds, and eventually, real-world policy backtesting.

## 21. Conclusion
Sangam Vidyut demonstrates, within a bounded computational experiment, that residential solar adoption can exhibit regime-dependent nonlinear dynamics arising from the interaction of affordability, household heterogeneity, social-network diffusion, finite fiscal budgets, and industry price feedback. Ultimately, the model confirms that ignoring the macro-fiscal limits of early network clustering yields profoundly inaccurate long-term adoption curves. Additionally, we observe that LLM cognition did not produce a detectable aggregate adoption advantage in the currently tested configuration.
"""

MATRIX_CONTENT = """# Claim Evidence Matrix

| Claim | Phase | Result Artifact | Conditionality |
|---|---|---|---|
| Affordability is an absolute adoption bottleneck. | Phase 4F.1 | `outputs/experiments/phase_4f_1/` | Unconditional |
| Mechanism activation strictly follows transition regimes (Blocked, Active, Saturated). | Phase 4F.2 | `phase_4f_2_report.md`, `aggregated_factor_summary.csv` | Unconditional |
| Network topology (BA vs WS) and Beta variations only alter adoption velocity conditionally. | Phase 4F.2 | `topology_policy_effects.csv`, `phase_4f_2_report.md` | Conditionally Supported (Active Regime 2000-3000) |
| Transition-regime subsidies maximize fiscal efficiency. | Phase 4F.3 | `policy_comparison.csv` (H1) | Unconditional |
| Target-seeking dynamic policy conserves budget while defending cascades. | Phase 4F.3 | `fixed_vs_dynamic.csv` (H2) | Conditionally Supported (Active/Saturated Regimes) |
| Target-seeking dynamic policy aggressively wastes budget trying to force blocked regimes. | Phase 4F.3 | `fixed_vs_dynamic.csv` (H2) | Conditionally Supported (Blocked Regime 1000) |
| Static aggregate models systematically overstate final adoption under strict finite budgets. | Phase 4F.3 | `static_vs_abm.csv` (H3), `phase_4f_3_report.md` | Conditionally Supported (Finite Budgets) |
| LLM Architectural integration is deterministic and strictly tracks identical timestep contexts. | Phase 4F.3 | `cognitive_audit.csv` | Unconditional |
"""

def generate_reports():
    os.makedirs("docs/research", exist_ok=True)
    with open("docs/research/MASTER_RESEARCH_REPORT.md", "w", encoding="utf-8") as f:
        f.write(REPORT_CONTENT)
    with open("docs/research/CLAIM_EVIDENCE_MATRIX.md", "w", encoding="utf-8") as f:
        f.write(MATRIX_CONTENT)
    print("Files created: docs/research/MASTER_RESEARCH_REPORT.md, docs/research/CLAIM_EVIDENCE_MATRIX.md")

if __name__ == "__main__":
    generate_reports()
