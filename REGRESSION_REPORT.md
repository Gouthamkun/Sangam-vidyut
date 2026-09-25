# Behavioral Regression Analysis: LiveSimulationRunner Empirical Deterministic Mode

## Executive Summary

The LiveSimulationRunner with `cognitive_mode="deterministic"` produces **zero adoption** (final adoption = 5, no new adoptions) because it sets cognitive thresholds to `lower=0.5, upper=0.5`, eliminating the ambiguous zone entirely. All agents receive rule-based REJECT decisions since combined scores (~0.11–0.17) fall below 0.5.

The "earlier isolated empirical live diagnostic" that showed **5 → 17 → 79 adoption** used the `cognitive_accessible_candidate_v1` policy (thresholds `lower=0.05, upper=0.20`), which creates an ambiguous zone where the MockLLM makes stochastic adoption decisions.

---

## 1. Empirical ConsumerAgent Field Verification ✓

All 500 empirical ConsumerAgents have required fields:
- `derived_mpce`: ALL HAVE (range: 200–19,333, mean: 3,571)
- `household_size`: ALL HAVE
- `sector`: ALL HAVE (values: 1, 2)
- `dwelling_type`: ALL HAVE (2 NaN values present)
- `electricity_access`: ALL HAVE (values: 1, 6, 9)
- `free_electricity`: ALL HAVE (values: 1, 2)

---

## 2. P_Base Distribution (500 agents, seed=42)

| Statistic | Value |
|-----------|-------|
| min | 0.000019 |
| max | 0.111450 |
| mean | 0.001238 |
| std | 0.005634 |
| median | 0.000156 |

**Key insight**: P_base is extremely low for virtually all agents. Only 1 agent has p_base > 0.1.

---

## 3. First-Step SIR_Score Distribution (t=1)

| Statistic | Value |
|-----------|-------|
| min | 0.000000 |
| max | 0.150000 |
| mean | 0.006061 |

- 475 agents: 0 infected neighbors → sir_score = 0.0
- 20 agents: 1 infected neighbor → sir_score = 0.15
- 0 agents: 2+ infected neighbors

Initial 5 adopters are randomly placed; only 20 agents are connected to them in the Watts-Strogatz (k=4, p=0.1) network.

---

## 4. Affordability Distribution (t=1)

| Statistic | Value |
|-----------|-------|
| min = max = mean | 0.552632 |

Single value for all agents: `subsidy(2625) / panel_price(4750) = 0.5526`

---

## 5. Combined Decision Score Distribution (t=1)

Formula: `score = 0.4*p_base + 0.4*sir_score + 0.2*affordability`

| Statistic | Value |
|-----------|-------|
| min | 0.110534 |
| max | 0.171033 |
| mean | 0.113449 |

**All 495 susceptible agents have scores in [0.11, 0.17]**

---

## 6. Decision Threshold Comparison

| Configuration | Lower Thresh | Upper Thresh | Ambiguous Zone | Result |
|---------------|--------------|--------------|----------------|--------|
| **LiveSimulationRunner (deterministic)** | 0.50 | 0.50 | **NONE** (lower==upper) | All agents: score ≤ 0.5 → **RULE REJECT** |
| Default Schema | 0.30 | 0.70 | (0.30, 0.70) | All agents: score ≤ 0.30 → **RULE REJECT** |
| **cognitive_accessible_candidate_v1** (earlier diagnostic) | **0.05** | **0.20** | **(0.05, 0.20)** | All agents: score ∈ (0.05, 0.20) → **LLM DECIDES** |

---

## 7. Adopt Decisions at t=1

| Configuration | Rule Adopt | Rule Reject | LLM Calls | New Adoptions |
|---------------|------------|-------------|-----------|---------------|
| LiveRunner (deterministic) | 0 | 495 | 0 | **0** |
| cognitive_accessible_candidate_v1 | 0 | 0 | 495 | Stochastic (MockLLM) |

---

## 8. Initial Adopter Synchronization ✓

- Initial 5 adopters correctly seeded on random network nodes
- `is_adopter = True` and `sir_state = 1` properly set
- SIR conservation verified: S + I + R = 500 at all timesteps
- Initial adopters recover after 2 quarters (recovery_duration_quarters=2)

---

## 9. ConsumerAgent.step() Execution ✓

All 500 ConsumerAgents execute `step()` each timestep. Verified via:
- `step_rule_decisions` counter increments correctly (495 at t=1 for deterministic mode)
- `step_llm_decisions` counter works (0 for deterministic, 495 for ambiguous zone config)

---

## 10. Configuration Pathway Comparison

| Parameter | Bug Report Config | Earlier Successful Diagnostic |
|-----------|-------------------|-------------------------------|
| subsidy | 2500 | 2500 |
| beta | 0.15 | 0.15 |
| population | 500 | 500 (or 5000 in campaign) |
| horizon | 24 | 24 |
| topology | watts_strogatz | watts_strogatz |
| household_mode | empirical | empirical |
| cognitive_mode | **deterministic** | **Not used** (direct config) |
| policy | fixed | fixed |
| initial_adoption | 5 | 5 |
| recovery | 2 | 2 |
| seed | 42 | 42 |
| **cognitive policy** | N/A (thresholds hardcoded) | **cognitive_accessible_candidate_v1** |
| **lower_threshold** | **0.5 (hardcoded)** | **0.05** |
| **upper_threshold** | **0.5 (hardcoded)** | **0.20** |
| **LLM enabled** | False | False (but MockLLM still called in ambiguous zone) |

**Root Cause**: `LiveSimulationRunner.__init__()` hardcodes thresholds to 0.5/0.5 for `cognitive_mode="deterministic"`, but the empirical p_base distribution + affordability + SIR effects produce scores ~0.11–0.17, which can never exceed 0.5.

---

## 11. Runtime Analysis

| Configuration | Population | Horizon | Runtime | Notes |
|---------------|------------|---------|---------|-------|
| LiveRunner (deterministic) | 500 | 24 | **47.5 sec** | No LLM calls, pure Python loops |
| cognitive_accessible_candidate_v1 | 500 | 24 | **28.1 sec** | 3,077 MockLLM calls (cached) |
| User reported | 500 | 24 | **~447 sec** | Likely different environment or config |

The 447s reported by user is ~10x slower than observed. Possible causes:
- Different Python environment / hardware
- LLM provider not mock (e.g., ollama/langgraph with real API calls)
- Larger population (campaign used 5000 agents)
- Memory pressure from cache growth

---

## Adoption Trajectory Comparison

### LiveSimulationRunner (deterministic, thresholds=0.5/0.5) — **BROKEN**
```
t=0:  5 adopters
t=1:  5 adopters (new=0)
...
t=24: 5 adopters (new=0)
Final: 5 | Expenditure: 0 | Budget: 1,000,000
```

### cognitive_accessible_candidate_v1 (thresholds=0.05/0.20) — **WORKS**
```
t=0:  5 adopters
t=1:  5 adopters (new=0)
...
t=8:  5 adopters (new=0)
t=9:  42 adopters (new=37)  ← First adoption (1 rule-based + 36 LLM?)
t=10: 494 adopters (new=452) ← Cascade
t=11-24: 494 adopters
Final: 494 | Expenditure: 1,222,500 | Budget: -222,500
```

**Note**: The earlier diagnostic's "5 → 17 → 79" trajectory differs from the campaign's "5 → 42 → 494", suggesting different population size (500 vs 5000) or seed.

---

## Root Cause & Fix

### Root Cause
`LiveSimulationRunner.__init__()` lines 44-47:
```python
if kwargs["cognitive_mode"] == "deterministic":
    self.config.llm.enabled = False
    self.config.cognitive.lower_threshold = 0.5
    self.config.cognitive.upper_threshold = 0.5
```

This eliminates the ambiguous zone. With empirical p_base (mean 0.0012) + max SIR (0.15) + affordability (0.55), combined scores max at ~0.17 << 0.5.

### Required Fix
The `deterministic` mode should use thresholds that allow rule-based adoption for high-scoring agents, e.g.:
- Option A: Use default schema thresholds (0.3/0.7) — but scores still too low
- Option B: Use `cognitive_accessible_candidate_v1` thresholds (0.05/0.20) — enables LLM-driven adoption
- Option C: Add a `deterministic_threshold` parameter to configure rule-based cutoff

**Recommendation**: Remove hardcoded threshold override in LiveSimulationRunner; let the config's CognitiveConfig validator handle threshold policy. Or add a "deterministic" policy name that sets appropriate thresholds.