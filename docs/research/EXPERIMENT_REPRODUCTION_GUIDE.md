# Experiment Reproduction Guide

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
