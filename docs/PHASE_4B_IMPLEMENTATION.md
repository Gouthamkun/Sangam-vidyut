# Phase 4B Implementation: Research Experiment & Ablation Engine

## Objective
Extend the Phase 4A experimental runner to support statistically robust multi-seed aggregation, dynamic parameter sweeps, and explicit feature ablations. This establishes Sangam Vidyut as a verifiable research testbed capable of producing statistical claims about bounded-rationality diffusion.

## Core Additions

### Multi-Seed Execution & Statistical Aggregation
- **`MultiSeedExperimentConfig`**: Overarches the base `ExperimentConfig`, specifying a list of integer seeds rather than a single seed.
- **Aggregation Engine**: Automatically computes cross-seed `mean`, `standard deviation`, `min`, and `max` for crucial metrics like `final_adoption_rate`.
- **Output Preservation**: Results are isolated per experiment into structured subdirectories:
  - `outputs/experiments/<exp_name>/raw/`: Distinct JSON files for every seed run.
  - `outputs/experiments/<exp_name ट्रायल>/aggregated/`: The statistical summarization across all seeds.
  - `outputs/experiments/<exp_name>/metadata/`: The exact generating configuration schema.

### Dynamic Parameter Sweeps
Implemented a Cartesian grid search function `generate_sweep_configs` in `experiments/engine.py`. This engine takes dictionary bounds (e.g. `{"beta": [0.1, 0.2], "topology": ["watts_strogatz", "barabasi_albert"]}`) and deterministically spawns unique `MultiSeedExperimentConfig` instances for every permutation.
These overrides map directly to internal runtime configurations, allowing zero-friction scaling.

### Controlled Ablation Framework
Introduced an `AblationConfig` permitting rigorous feature deactivation without altering Phase 3 internal code logic:
- `disable_sir`: Nullifies the SIR transition by locking `beta = 0.0`.
- `disable_network`: Nullifies topological peer influence.
- `disable_dynamic_subsidy`: Freezes the government subsidy, preventing scaling regardless of adoption targets.
- `disable_dynamic_pricing`: Locks industry panel prices at baseline.
- `disable_llm`: Reverts `lower_threshold` and `upper_threshold` to `0.5`, functionally bypassing LangGraph purely into the mathematical fallback.

### Topology Comparison
Added structural configuration for explicit `topology` variants. Experiments can run identically seeded networks using `watts_strogatz` versus `barabasi_albert` scale-free structures to evaluate influencer hub dynamics.

## Test Validation
Added `test_engine.py` addressing:
- Sweeper generation counting.
- Ablation configuration cascading.
- Statistical summarization logic.
- Output directory generation.

## Research Integrity Note
This infrastructure strictly tracks caching and failure rates independently. The research specification explicitly mandates that increased adoption rates do not automatically qualify an ABM model as "superior". The purpose of this framework is measuring behavioral deviation, not optimizing adoption outcomes.
