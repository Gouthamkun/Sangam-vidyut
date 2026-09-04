# Phase 4C - Economic Nonlinearity and Subsidy Sweep Results

## 1. Experimental Protocol
This experiment executed a parameter sweep over government subsidy levels to evaluate if adoption exhibits a non-linear tipping point (a cascade). 

**Configurations:**
- **Population:** 500 agents
- **Duration:** 24 quarters
- **Seeds:** 10 independent seeds per configuration (42-51)
- **Subsidy Sweep:** 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000

## 2. Execution Status
**STATUS = PARTIAL / INTERRUPTED**

- **Completed Deterministic Evidence:** 100/100 runs successfully generated.
- **Completed Cognitive Evidence:** 18/100 runs successfully generated (Subsidy 500 completed 10 seeds; Subsidy 1000 completed 8 seeds).

*Note: The cognitive sweep was interrupted. A full cognitive subsidy curve cannot and will not be inferred from only 18 runs.*

## 3. Completed Deterministic Evidence (100/100 runs)
| Subsidy | Seeds | Mean Final Adoption | Tipping Fraction |
| :--- | :--- | :--- | :--- |
| 500 | 10 | 1.0% | 0.0 |
| 1000 | 10 | 1.0% | 0.0 |
| 1500 | 10 | 1.0% | 0.0 |
| 2000 | 10 | 1.0% | 0.0 |
| 2500 | 10 | 1.0% | 0.0 |
| 3000 | 10 | 1.0% | 0.0 |
| 3500 | 10 | 1.0% | 0.0 |
| 4000 | 10 | 1.0% | 0.0 |
| 4500 | 10 | 1.0% | 0.0 |
| 5000 | 10 | 1.0% | 0.0 |

*Note: 1.0% corresponds exactly to the initial 5 seed adopters out of 500 agents. Zero new adoptions occurred.*

## 4. Completed Cognitive Evidence (18/100 runs)
| Subsidy | Seeds | Mean Final Adoption | Mean Cache Hit Rate | LLM Failures |
| :--- | :--- | :--- | :--- | :--- |
| 500 | 10 | 1.0% | 83.8% | 0 |
| 1000 | 8 | ~1.1% | N/A (Partial) | 0 |

## 5. Subsidy Mechanism Audit & Deadlock Analysis
Following the flat adoption curve observed in the deterministic sweep, a rigorous mathematical audit was performed on the subsidy dataflow and decision mechanics.

### 5.1 Subsidy Dataflow
1. **ExperimentConfig**: `subsidy` is injected via `run_exp4c.py` sweeps.
2. **GovernmentAgent**: Initializes `self.subsidy = base_subsidy`. `dynamic_subsidy` is disabled via ablation, so the value remains perfectly constant for all 24 quarters.
3. **ConsumerAgent**: Reads `model.current_subsidy` during `step()`.
4. **Affordability**: Calculated as `min(subsidy / max(price, 1.0), 1.0)`.
5. **Decision Score**: `score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability`.

### 5.2 Saturation and Capping
Affordability correctly clips to `[0,1]`. It normalizes against `config.industry.base_price` (₹5000). Thus, it saturates perfectly at exactly `subsidy = 5000` (`5000/5000 = 1.0`). No budgets prematurely constrain the subsidy.

### 5.3 Mathematical Bootstrap Barrier (Deadlock)
The system suffers from a structural diffusion deadlock. 
- Maximum possible `p_base` (Income=0, Homeowner=1) = `0.636`. Weight = `0.4` -> max contribution `0.254`.
- Maximum affordability (Subsidy=5000) = `1.0`. Weight = `0.2` -> max contribution `0.200`.
- Maximum possible score when `sir_score = 0`: **0.454**.

Because `0.454 < 0.50` (the adoption threshold), **zero agents can adopt spontaneously without infected neighbors**, regardless of how high the subsidy goes.

To cross the threshold at max subsidy (5000), an agent requires a `sir_score` of at least `(0.500 - 0.454) / 0.4 = 0.115`. 
With `beta = 0.1`, a single infected neighbor provides a `sir_score` of `0.10`. 
Therefore, even the most optimal household at 100% subsidy requires **at least two initial seed adopters as direct neighbors** to cross the threshold deterministically. Given 5 random seeds in 500 agents, the probability of this occurring is virtually zero, stranding the simulation in deadlock.

### 5.4 Bug vs Design Classification
**C. Diffusion/bootstrap formulation creates a structural deadlock.**
The subsidy propagates perfectly. However, the fixed `0.4 / 0.4 / 0.2` weights mathematically neuter the economic dimension, making spontaneous adoption fundamentally impossible and stranding the network before cascades can bootstrap.

## 6. Recommendations
A scientific tuning experiment is required to adjust the mathematical weights (e.g., increasing affordability weight to `0.4` and reducing `p_base` or `sir_score`) or to introduce spontaneous innovator adoption (`beta_spontaneous`), breaking the bootstrap deadlock before resuming the large compute sweeps.
