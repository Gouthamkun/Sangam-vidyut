# Phase 4C Experiment Plan: Tipping-Point and Cascade Hypotheses

## 1. Experiment 1 — Topological Diffusion
**Hypothesis**: The underlying network topology influences the rate and saturation of social contagion. We will test whether Barabási-Albert (scale-free) or Watts-Strogatz (small-world) networks diffuse the adoption cascade faster under identical contagion variables.
- **Model**: `SIR_ONLY`
- **Control Variables**: `n_agents=500`, `timesteps=24`, `recovery_duration=2`
- **Independent Variables (Sweep)**: 
  - `beta` (Influence): `[0.05, 0.15, 0.3]`
  - `topology`: `["watts_strogatz", "barabasi_albert"]`
- **Seeds**: 15 per configuration
- **Metrics**: 
  - Adoption trajectory
  - Final adoption rate
  - Tipping-point timestep
  - Peak new-adoption rate
  - Time to 25% adoption
  - Time to 50% adoption
  - Fraction of runs reaching tipping point

## 2. Experiment 2 — Economic Nonlinearity
**Hypothesis**: Solar adoption exhibits a highly nonlinear transition around a specific economic threshold. We hypothesize an empirical "cliff" where subsidy increases tip the deterministic affordability score into a mathematically inevitable cascade.
- **Model**: `DETERMINISTIC_ABM` (Fixed mathematical logic)
- **Control Variables**: `n_agents=500`, `timesteps=24`, `topology="watts_strogatz"`, `beta=0.1`, `dynamic_subsidy=False`
- **Independent Variables (Sweep)**: 
  - `subsidy`: `[500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]`
- **Seeds**: 10 per configuration
- **Metrics**:
  - Final adoption rate
  - Tipping-point timestep
  - Adoption trajectory

## 3. Experiment 3A — Controlled Cognitive Ablation (Architectural Control)
**Hypothesis**: The routing mechanics of the cognitive layer function deterministically under isolated architectural controls. Using a Mock LLM ensures that any pipeline differences between pure math and cognitive bypass are purely structural and verifiable.
- **Models**: `DETERMINISTIC_ABM` vs `FULL_COGNITIVE_ABM` (configured with `MockLLM`)
- **Control Variables**: `n_agents=100`, `timesteps=12`, identical initial seeds and environments.
- **Independent Variables**: LLM cognitive routing toggle (Math vs MockLLM)
- **Seeds**: 5 per configuration
- **Metrics**:
  - Adoption trajectory
  - Final adoption rate
  - Tipping-point timestep
  - Total LLM calls
  - Total cache hits
  - Cache hit rate
  - Fallback decisions
- *Note: The MockLLM is strictly an architectural control. Results are not interpreted as realistic cognitive behavior.*

## 4. Experiment 3B — Real LLM Validation
**Hypothesis**: Real LLM-driven bounded rationality introduces realistic human friction into otherwise obvious mathematical cascades, altering both the S-curve trajectory and the effective tipping point threshold.
- **Model**: `FULL_COGNITIVE_ABM` (Configured with Real API Provider, e.g., OpenAI)
- **Control Variables**: `n_agents=100`, `timesteps=12`
- **Constraints**: Will not be executed automatically during CI/pytest to prevent unintended API billing and flakiness.
- **Metrics**:
  - Provider/Model identifier
  - Model configuration (temperature, timeouts)
  - Prompt version/hash
  - Total LLM calls
  - Failures
  - Fallbacks
  - Cache statistics (hits, misses, hit rate)

## 5. Statistical Analysis Plan
To ensure rigorous scientific validity, results across all experiments will be evaluated using:
1. **Central Tendency & Dispersion**: Mean and Standard Deviation across independent seeds.
2. **Confidence Intervals**: 95% CIs calculated for final adoption rates and tipping-point timesteps.
3. **Effect Size**: Cohen's *d* (or equivalent) to measure the magnitude of the difference between topologies (Exp 1) or models (Exp 3A/3B).
4. **Distribution Metrics**: Histograms/Density plotting of the distribution of tipping points.
5. **Success Rates**: The explicit proportion (fraction) of independent runs that successfully reach the tipping point threshold under specific configurations.

## 6. Data Preservation
- **Seed Determinism**: Every configuration uses explicitly recorded integer seeds.
- **Raw Artifacts**: Per-seed raw JSON outputs will be permanently persisted.
- **Aggregate Artifacts**: Summarized statistics will not overwrite raw files.
- **Metadata**: Each experiment directory encapsulates the full configuration schema payload used to generate it.
- **Core Engine Integrity**: No changes are made to the core Mesa, SIR, or LangGraph architectures to support these observations.
