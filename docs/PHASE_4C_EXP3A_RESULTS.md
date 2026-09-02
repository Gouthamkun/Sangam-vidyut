# Phase 4C Experiment 3A Results: Controlled Cognitive Ablation

## 1. Research Question
What is the structural and computational difference between a purely deterministic rigid-threshold ABM (`DETERMINISTIC_ABM`) and a cognitively routed ABM (`FULL_COGNITIVE_ABM`) under identical environmental parameters, using a probabilistic `MockLLM` as a baseline cognitive proxy?

## 2. Experimental Design
- **Models**: 
  1. `DETERMINISTIC_ABM` (Strict `score >= 0.5` mathematical routing)
  2. `FULL_COGNITIVE_ABM` (Ambiguous decisions routed to `MockLLM`)
- **Population**: `n_agents = 100`
- **Timesteps**: `12`
- **Seeds**: `[42, 100, 200, 300, 400]` (5 total runs per model)
- **Cognitive Proxy**: The `MockLLM` evaluates the underlying score with a uniform probabilistic noise band (`[-0.15, +0.15]`) to simulate boundedly rational human variance.

## 3. Results Summary

| Metric | DETERMINISTIC_ABM | FULL_COGNITIVE_ABM (MockLLM) | Difference |
|--------|-------------------|------------------------------|------------|
| **Mean Final Adoption** | 5.00% (Exactly the seed) | 6.20% | +1.20% |
| **Max Final Adoption** | 5.00% | 11.00% (Seed 42) | +6.00% |
| **Std Dev Adoption** | 0.00% | 2.68% | +2.68% |
| **Frac Reaching Tipping Pt** | 0.00 | 0.20 (1/5 runs) | +0.20 |
| **Mean Peak New Adoption** | 0.00% | 1.20% | +1.20% |

## 4. Computational and Caching Overhead
The introduction of the cognitive layer natively routes ambiguous `[0.3, 0.7]` scores to the `LLMInterface`.
- **Mean LLM Invocations per Run**: `128.2` evaluations (across 12 timesteps × 100 agents = 1200 decisions). Roughly 10% of decisions fell into the ambiguous band requiring cognitive processing.
- **Mean Cache Hit Rate**: **54.86%**.
- **Cache Efficacy**: The structural cache key remediations implemented in Phase 3C (e.g., binning continuous variables and discarding absolute timestep) successfully trapped over half of all cognitive decisions, preventing redundant evaluations even in a highly stochastic environment.

## 5. Scientific Interpretation
**Conclusion: Cognitive Model > Deterministic Model** in overcoming algorithmic rigidity.

The hypothesis is structurally validated:
- The **Deterministic Model** suffers from algorithmic rigidity. As proven in Experiment 2, because the structural affordability weights are mathematically bounded, the absolute `score >= 0.5` threshold creates a completely impenetrable barrier. Without external network influence, agents are perpetually frozen in `WAIT` states (evidenced by 0% standard deviation and 5.0% flat baseline adoption).
- The **Cognitive Model (MockLLM)** injects bounded rationality. The stochastic noise band `[-0.15, +0.15]` allows marginal economic profiles (e.g., scores of `0.40`) to occasionally cross the cognitive threshold (`0.40 + 0.12 noise = 0.52 -> ADOPT`). 
- Once these probabilistic adoptions occur, they incrementally increase the localized `sir_score` for their neighbors. In Seed 42, this catalyzed a minor cascade pushing adoption to 11.0% and successfully hitting the tipping point metric, which the deterministic model proved mathematically incapable of doing under these parameters.

## 6. Limitations
- The `MockLLM` is ultimately still a probability distribution, not true semantic reasoning. It demonstrates *why* smoothing the threshold is important, but a real LLM API (Phase 5) is required to determine whether *actual human-like reasoning* produces similar noise distributions or exhibits deeper contextual logic (e.g., recognizing specific policy synergies).
- The 54.86% cache hit rate indicates that while Phase 3C fragmentation was heavily mitigated, the continuously floating internal `sir_score` still forces a large number of unique cache states over time.
