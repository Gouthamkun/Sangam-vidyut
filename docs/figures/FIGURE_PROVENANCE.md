# Figure Provenance

## Figure 1: System Architecture
- **Phase**: Conceptual (All Phases)
- **Source Artifact**: `MASTER_RESEARCH_REPORT.md` (System Architecture description)
- **Scientific Rationale**: Explicitly visualizes the core execution loop and data integration limits.

## Figure 2: Indian Calibration Pipeline
- **Phase**: Pre-flight / Phase 4E (Calibration)
- **Source Artifact**: `docs/calibration/` and `MASTER_RESEARCH_REPORT.md`
- **Scientific Rationale**: Depicts the aggregate-consistent mapping from HCES 2023-24 to synthetic quantiles without claiming causal household labels.

## Figure 3: Household Decision Mechanism
- **Phase**: Core Model Mechanics
- **Source Artifact**: `src/simulation/agents/consumer.py`
- **Scientific Rationale**: Mathematically outlines the bounded-rationality equation `0.4*p_base + 0.4*SIR + 0.2*affordability` and the threshold logic determining LLM cognitive routing.

## Figure 4: Subsidy Response Curve
- **Phase**: Phase 4F.2
- **Source File**: `outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv`
- **Filtering**: `model_class == DETERMINISTIC_EMPIRICAL_ABM`
- **Aggregation Rule**: Mean adoption percentage over 10 matched seeds at each subsidy level.
- **Uncertainty**: Shaded standard deviation (± 1 SD) bands across identical seed configurations.

## Figure 5: Mechanism Activation Regimes
- **Phase**: Phase 4F.2 (Synthesis)
- **Source Artifact**: `outputs/experiments/phase_4f_2/reports/phase_4f_2_report.md`
- **Scientific Rationale**: Conceptually highlights the empirical block limits: Blocked (<2000), Diffusion-Active (2000-3000), Saturated (>4000).

## Figure 6: Topology Effect
- **Phase**: Phase 4F.2
- **Source File**: `outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv`
- **Filtering**: `model_class == DETERMINISTIC_EMPIRICAL_ABM`
- **Aggregation Rule**: Mean final adoption % grouped by Barabási-Albert vs Watts-Strogatz at each subsidy level.
- **Uncertainty**: Error bars denoting standard deviation over 10 seeds.

## Figure 7: Beta Effect (Contagion Rate)
- **Phase**: Phase 4F.2
- **Source File**: `outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv`
- **Filtering**: `model_class == DETERMINISTIC_EMPIRICAL_ABM`
- **Aggregation Rule**: Mean final adoption %, separated by Beta (0.05, 0.15, 0.30) across subsidies.

## Figure 8: Household Heterogeneity Impact
- **Phase**: Phase 4F.2
- **Source File**: `outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv`
- **Filtering**: `topology == watts_strogatz` AND `beta == 0.15`
- **Aggregation Rule**: Comparison of Empirical (high variance) vs Constant (zero variance) p_base mapping.

## Figure 9: Policy Trajectories (Fixed vs Dynamic)
- **Phase**: Phase 4F.3
- **Source File**: `outputs/experiments/phase_4f_3/raw/R3_DET_3000.0_*_watts_strogatz_42_trajectory.csv`
- **Filtering**: Subsidy 3000, Watts-Strogatz topology, Seed 42.
- **Scientific Rationale**: Direct matched-seed trajectory demonstration of target-seeking algorithm maintaining cascades.

## Figure 10: Policy Efficiency
- **Phase**: Phase 4F.3
- **Source File**: `outputs/experiments/phase_4f_3/tables/fixed_vs_dynamic.csv`
- **Aggregation Rule**: Mean difference in predefined policy efficiency (New Adoptions / Expenditure_millions) between Dynamic and Fixed models.

## Figure 11: Budget Exhaustion Paradox
- **Phase**: Phase 4F.3 (Analysis Audit)
- **Source Artifact**: `MASTER_RESEARCH_REPORT.md` (Static vs ABM Audit finding)
- **Scientific Rationale**: Diagrammatic proof of the counter-intuitive fiscal feedback loop where slow adoption preserves budget, leading to higher final delayed adoption.

## Figure 12: Complete Feedback Loop
- **Phase**: Conceptual Synthesis
- **Source Artifact**: `MASTER_RESEARCH_REPORT.md`
- **Scientific Rationale**: Fully maps the causal flow between the Government, Industry, Environment, and Social Network sub-agents within Sangam Vidyut.
