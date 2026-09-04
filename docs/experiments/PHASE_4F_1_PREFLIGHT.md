# Phase 4F.1: Preflight Validation

## 1. Effective Configuration
The primary experimental configuration for Phase 4F has been successfully frozen and verified against the canonical codebase:
*   **Baseline Provider**: Empirical
*   **Behavior Policy**: `cognitive_accessible_candidate_v1`
*   **Cognitive Thresholds**: `[0.05, 0.20]` (Opt-in Override confirmed)
*   **Weights**: `[0.4, 0.4, 0.2]` (Confirmed via invariant ConsumerAgent scoring logic)
*   **Network Options (Beta)**: `0.05, 0.15, 0.30`
*   **Recovery Period**: `2` quarters
*   **Topologies**: Watts-Strogatz and Barabási-Albert
*   **Horizon**: `24` quarters
*   **Empirical Calibration Artifact SHA-256**: `0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241`
*   **LLM Flag**: Explicitly forced to `mock` OFF during Deterministic ABM execution

## 2. Smoke Tests
One paired short-run (100 agents, 4 quarters) was successfully executed across all three primary architectures:

### A. Static Baseline
*   Provides a completely static network-agnostic baseline where the model strictly operates as independent logistic predictions.
*   Successfully executed; output captured.

### B. Deterministic Empirical ABM
*   Successfully ran with LLM disabled, relying purely on the behavior score crossing the autonomous `0.20` upper threshold or stalling in the wait queue.
*   Invariants preserved at every step.

### C. Hybrid Cognitive ABM
*   Successfully triggered the MockLLM Provider within the decision margin `[0.05, 0.20]`. 
*   Successfully captured metrics for total LLM calls and fallbacks.

## 3. Complete Factor Cell Execution
One fully powered factor cell (500 agents, 24 quarters) was executed:
*   **Parameters**: Watts-Strogatz topology, Beta = 0.15, Seed = 42
*   **Trajectory Results**: Extracted cleanly. 
*   **Invariant Audits**:
    1.  `S + I + R = N` at every step.
    2.  Cumulative adoptions strictly monotonically increasing.
    3.  Probabilities bounded exactly `[0.0, 1.0]` with 0 NaN/Inf values.
    4.  Unique Agent ID preservation enforced.
    5.  Artifact hashes remained immutable.

## 4. Runtime Estimates
The following elapsed-time extrapolation was calculated to project the full computational requirements for the subsequent campaign:
*   **10 Seeds × 2 Topologies × 3 Beta Levels = 60 experimental runs**
*   **Single run (500 agents)**: ~1-3 seconds
*   **Single run (5000 agents)**: estimated at ~10-15 seconds (assuming linear/network structural overhead)
*   **60 Runs (500 agents)**: Under 5 minutes total.
*   **60 Runs (5000 agents)**: Under 15 minutes total.
*   *(Note: This assumes deterministic execution. Enabling real LLM integration will linearly dominate runtime based on API latency.)*

## Final Status
All preflight tests pass. The exact outputs have been serialized to JSON logs.

**PHASE 4F.1 PREFLIGHT VALIDATED**
