import os

REPRODUCIBILITY = """# Sangam Vidyut Reproducibility Guide

This document outlines the strict technical constraints and infrastructure used to ensure bitwise reproducibility across the Sangam Vidyut Phase 4F experiments.

## IMPORTANT DISTINCTION
- **Reproducing Existing Results**: Validating identical artifacts using the locked `config_sha256` and exact 10-matched-seed arrays.
- **Running New Experiments**: Will overwrite artifacts and invalidate Phase 4F locked boundaries. **Do not run new experiments in the locked release state.**

## Environment Lock
- **Python Version**: 3.12.4
- **Dependency Installation**: Run `pip install -r requirements-lock.txt` to instantiate the exact validated environment.

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

## Reproducibility Mechanics
- **Random Seed Strategy**: All experiments utilize deterministic 10-matched-seed arrays (`[42, 43, 44, 45, 46, 47, 48, 49, 50, 51]`).
- **Configuration Hashing**: Every experiment generates a `config_sha256` mapping exactly to its invariant parameters.
- **Calibration Artifact**: The population proxy is locked to `SHA-256: 0d5acf7...`.
- **Atomic Persistence**: Experiment manifests and CSV trajectories are written atomically to prevent mid-run state corruption.
- **Invariant Checks**: Mathematical constraints (e.g. `S + I + R == N`) are explicitly validated per-timestep.
- **Test Suite**: A `pytest` suite consisting of 126 assertions continuously monitors physics and cognitive cache isolation.
- **Dashboard Launch**: `python -m streamlit run app.py` (Loads precomputed outputs. Does NOT mutate data).
"""

EXP_GUIDE = """# Experiment Reproduction Guide

*Warning: Running these commands will overwrite the locked outputs for the specified phases. Use only for verification of reproducibility.*

## Phase 4F.1
- **Purpose**: Affordability Bottleneck Assessment
- **Configuration**: Baseline un-networked mechanics vs theoretical bounds.
- **Output Directory**: `outputs/experiments/phase_4f_1_rerun/`
- **Command**: `python scripts/experiments/phase_4f_1_campaign.py`
- **Analysis**: `python scripts/experiments/phase_4f_1_analysis.py`

## Phase 4F.2
- **Purpose**: Mechanism Activation (Topology, Beta, Heterogeneity)
- **Configuration**: 560-run deterministic factorial cross-product.
- **Seeds**: 10 matched seeds `[42-51]`.
- **Output Directory**: `outputs/experiments/phase_4f_2/`
- **Command**: `python scripts/experiments/phase_4f_2_campaign.py`
- **Analysis**: `python scripts/experiments/phase_4f_2_analysis.py`
- **Expected Artifacts**: 560 atomic manifests, trajectories, and 1 aggregated `aggregated_factor_summary.csv`.

## Phase 4F.3
- **Purpose**: Policy Robustness (Fixed vs Target-Seeking Dynamic)
- **Configuration**: 320-run factorial isolating budget exhaustion.
- **Seeds**: 10 matched seeds `[42-51]`.
- **Output Directory**: `outputs/experiments/phase_4f_3/`
- **Command**: `python scripts/experiments/phase_4f_3_campaign.py`
- **Analysis**: `python scripts/experiments/phase_4f_3_analysis.py`
- **Expected Artifacts**: 320 atomic manifests, trajectories, and `fixed_vs_dynamic.csv`.
"""

DATA_PROV = """# Data Provenance

The Sangam Vidyut model relies on public empirical datasets mapped via ecological calibration. **No private credentials or sensitive local paths are exposed.**

## 1. Household Consumption Expenditure Survey (HCES 2023-24)
- **Purpose**: Empirical distribution of wealth proxy (MPCE) for synthetic household generation.
- **Local Representation**: Survey-weighted probability distributions.
- **Limitations**: Aggregate statistics only; does not provide direct household-level solar adoption labels.

## 2. MNRE Benchmark Costs
- **Purpose**: Establishes base panel prices and capital thresholds.
- **Local Representation**: `IndustryAgent` base constraints and scaling boundaries.

## 3. PM Surya Ghar Targets
- **Purpose**: Calibrates the government budget cap and 50% target milestones.
- **Local Representation**: Configures `GovernmentAgent` fiscal allocations.

## 4. CEA Domestic Consumer Data
- **Purpose**: Establishes the macro-denominator for household scale conversion.
- **Local Representation**: Bound-checking targets for the ecological scaling.
"""

ARTIFACT_INDEX = """# Research Artifact Index

Index of primary released artifacts (located in `docs/` and `outputs/`):

- **Master Report**: `docs/research/MASTER_RESEARCH_REPORT.md` (Required for reproduction: No | Source-authored)
- **Claim Matrix**: `docs/research/CLAIM_EVIDENCE_MATRIX.md` (Required for reproduction: No | Source-authored)
- **Portfolio Case Study**: `docs/research/PORTFOLIO_CASE_STUDY.md` (Required for reproduction: No | Source-authored)
- **Figures**: `docs/figures/*.png` (Required for reproduction: No | Generated)
- **Phase 4F.1 Report**: `outputs/experiments/phase_4f_1_rerun/reports/` (Required for reproduction: Yes | Generated)
- **Phase 4F.2 Report & Tables**: `outputs/experiments/phase_4f_2/` (Required for reproduction: Yes | Generated)
- **Phase 4F.3 Report & Tables**: `outputs/experiments/phase_4f_3/` (Required for reproduction: Yes | Generated)
- **Experiment Manifests**: JSON configs inside phase directories (Required for reproduction: Yes | Generated)
- **Dashboard App**: `app.py` (Required for reproduction: No | Source-authored)
"""

RELEASE_CHECKLIST = """# Scientific Release Checklist

## CODE
- [x] Source tracked
- [x] No accidental .pyc
- [x] No secrets
- [x] No debug artifacts

## DATA
- [x] Raw/private data correctly ignored
- [x] Provenance documented
- [x] No sensitive local data committed

## EXPERIMENTS
- [x] Phase 4F.1 locked
- [x] Phase 4F.2 = 560 runs
- [x] Phase 4F.3 = 320 runs

## RESULTS
- [x] Reports present
- [x] Tables present
- [x] Figures present
- [x] Claim matrix aligned

## TESTING
- [x] Current validated test suite = 126 passing

## DASHBOARD
- [x] Launches successfully
- [x] Locked artifacts load
- [x] No scientific mutation

## DOCUMENTATION
- [x] README
- [x] Research report
- [x] Portfolio
- [x] Reproduction guide
- [x] Data provenance
- [x] Demo script
"""

RELEASE_NOTES = """# Release Notes — Final Research Release

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
- **Reproducible Infrastructure**: Factorial automation spanning 880 multi-threaded runs.
- **Cognitive Routing Caching**: A seed-isolated LangGraph ambiguity router that safely evaluated over 1.1 million states with absolute determinism.
- **Atomic Persistence**: Immutable CSV/JSON checkpointing preventing mid-run corruption.

## Known Limitations
- The simulation uses an optional cognitive-routing layer, NOT human-level cognitive AI.
- It operates under a target-seeking policy heuristic, NOT an optimized control system.
- The model serves as a computational testbed, NOT a causal policy simulator or national forecast.
- Calibrations are aggregate/ecological, not true household-causal.

## Reproducibility Status
- 100% Deterministic: Validated by 126 invariant tests.
"""

PROJECT_MAP = """# Final Project Map

```text
DATA (HCES, CEA, MNRE)
       ↓
  CALIBRATION (Aggregate-Ecological)
       ↓
HOUSEHOLD AGENTS (ConsumerAgent)
       ↓
ECONOMIC DECISION (0.4*p_base + 0.4*SIR + 0.2*affordability)
       ↓
  NETWORK / SIR (Watts-Strogatz / Barabási-Albert)
       ↓
POLICY / INDUSTRY / ENVIRONMENT (Feedback Loops)
       ↓
OPTIONAL COGNITIVE ROUTING (LangGraph Ambiguity Filter)
       ↓
EXPERIMENT ENGINE (Mesa Orchestrator)
       ↓
    ANALYSIS (Aggregation & Provenance)
       ↓
    FIGURES (Matplotlib/Plotly)
       ↓
   DASHBOARD (Streamlit - app.py)
       ↓
REPORT / PORTFOLIO (Synthesis Documents)
```
"""

import os
os.makedirs("docs/research", exist_ok=True)
files = {
    "docs/research/REPRODUCIBILITY.md": REPRODUCIBILITY,
    "docs/research/EXPERIMENT_REPRODUCTION_GUIDE.md": EXP_GUIDE,
    "docs/research/DATA_PROVENANCE.md": DATA_PROV,
    "docs/research/RESEARCH_ARTIFACT_INDEX.md": ARTIFACT_INDEX,
    "docs/research/RELEASE_CHECKLIST.md": RELEASE_CHECKLIST,
    "docs/research/RELEASE_NOTES.md": RELEASE_NOTES,
    "docs/research/PROJECT_MAP.md": PROJECT_MAP
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files successfully generated.")
