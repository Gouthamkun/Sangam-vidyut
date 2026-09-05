# Release Notes — Final Research Release

## Project Purpose
Sangam Vidyut is a computational testbed and model-based simulation exploring how economic constraints, heterogeneous households, social networks, finite policy budgets, and industry responses interact to produce regime-dependent residential solar adoption dynamics.

## Completed Phases
- **Phase 4F.1**: Affordability Bottleneck Isolation.
- **Phase 4F.2**: Mechanism Activation (Topology, Beta, Heterogeneity).
- **Phase 4F.3**: Policy Robustness (Fixed vs Target-Seeking Dynamic Policy).
- **Phase 5**: Research Synthesis, Dashboard, and Packaging.

## Major Scientific Findings
- **The Budget-Network Paradox**: Rapid early network adoption accelerates subsidy expenditure, causing early budget exhaustion and a subsidy collapse. Slower baseline adoption preserves the budget, enabling later mass adoption cascades.
- **Regime-Dependent Action**: Topology, network beta, and heterogeneity are strictly inactive in affordability-blocked regimes and completely dominate inside diffusion-active regimes.

## Major Engineering Achievements
- **Reproducible Infrastructure**: Factorial automation spanning 1,060 multi-threaded runs.
- **Cognitive Routing Caching**: A seed-isolated LangGraph ambiguity router that safely evaluated over 1.1 million states with absolute determinism.
- **Atomic Persistence**: Immutable CSV/JSON checkpointing preventing mid-run corruption.

## Known Limitations
- The simulation uses an optional cognitive-routing layer, NOT human-level cognitive AI.
- It operates under a target-seeking policy heuristic, NOT an optimized control system.
- The model serves as a computational testbed, NOT a causal policy simulator or national forecast.
- Calibrations are aggregate/ecological, not true household-causal.

## Reproducibility Status
- 100% Deterministic: Validated by 126 invariant tests.
