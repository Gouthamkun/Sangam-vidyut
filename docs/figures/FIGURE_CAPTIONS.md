# Figure Captions

**Figure 1. Sangam Vidyut System Architecture.** The conceptual agent-based structure connecting empirical Indian household data to macroeconomic feedback loops. Note the integration of social network diffusion with explicit, discrete affordability bottlenecks and an optional architectural LLM routing layer for ambiguous decisions.

**Figure 2. Aggregate-Consistent Ecological Calibration Pipeline.** Demonstrates the flow from the HCES 2023-24 survey data into a synthetic N=500 population. The model is ecologically fitted against MNRE/CEA macro-targets, serving as an aggregate proxy rather than enabling true household-level causal identification.

**Figure 3. Household Decision Mechanism.** The mathematical thresholding logic governing individual agent behavior. Adoption is determined by a deterministic score function (`0.4*p_base + 0.4*SIR + 0.2*affordability`). The diagram highlights the explicit boundary conditions where bounded-rationality (LLM Cognitive Routing) is optionally triggered.

**Figure 4. Subsidy Response Curve (N=500).** The absolute adoption return on varying government subsidy levels (Phase 4F.2 Deterministic ABM). The curve reveals a highly nonlinear transition from an affordability-blocked regime into a diffusion-active state, before plateauing into absolute saturation. 

**Figure 5. Observed Mechanism Activation Regimes.** An interpretive mapping of the three fundamental structural phases identified in Phase 4F.2. Network mechanics are strictly dormant in the Blocked regime, highly sensitive in the Diffusion-Active regime, and structurally irrelevant in the Saturated regime.

**Figure 6. Conditional Topology Effect (BA vs WS).** A comparison of final mean adoption between scale-free (Barabási-Albert) and small-world (Watts-Strogatz) social geometries. The topology structure exclusively influences final adoption counts *within* the diffusion-active transition regime (Subsidy 2000-3000), proving network effects are fundamentally conditional on baseline affordability.

**Figure 7. Contagion Rate (Beta) Sensitivity.** Evaluation of the SIR transmission probability (beta) across the subsidy response curve. Higher beta values trigger steeper, earlier adoption cliffs, but they strictly cannot override the absolute financial blocking thresholds at subsidies <2000.

**Figure 8. Household Heterogeneity Impact.** A matched-seed comparison contrasting an empirical distribution of baseline adoption propensity (`p_base`) against a constant (zero-variance) mean. The empirical variance prevents sudden step-function phase transitions, mathematically smoothing the adoption cliff across the active regime.

**Figure 9. Fixed vs Target-Seeking Dynamic Policy (Subsidy 3000).** Matched trajectory demonstration evaluating a fixed subsidy against a dynamic heuristic adjusting to a 50% target. While the dynamic policy successfully sustains the cascade in this specific transition regime, we note this is a heuristic agent model and not an optimized macroeconomic control proof.

**Figure 10. Dynamic Policy Efficiency Gains vs Fixed Base.** The relative change in fiscal policy efficiency (New Adoptions per million monetary units) between Dynamic and Fixed strategies across regimes. The dynamic model conserves fractional efficiency in active zones but aggressively wastes budget when forcing adoption in blocked zones.

**Figure 11. Budget Exhaustion Paradox (Observed Simulation Mechanism).** The causal flowchart explaining the counter-intuitive Phase 4F.3 discovery. In finite-budget models, rapid early adoption via network clustering burns through government subsidies prematurely, permanently crashing affordability. Conversely, models ignoring network effects artificially preserve the budget, leading to over-optimistic delayed mass adoption.

**Figure 12. Complete System Feedback (Causal Loop Diagram).** The master diagram of interconnected macroeconomic feedback loops dictating the Sangam Vidyut model trajectory. It illustrates how household interactions (SIR) and affordability trigger finite fiscal exhaustion, while aggregate adoption delays drive down base industry prices.
