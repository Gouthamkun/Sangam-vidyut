# Phase 3A: Deterministic Agent-Based Simulation (Mesa)

## Architecture Overview
Phase 3A integrates the statistical models and graph structures from Phase 1 & 2 into a formal Agent-Based Simulation using the **Mesa 3.0+** framework. 

Mesa acts as the **sole authoritative engine**, controlling simulation time, agent lifecycle, state progression, and schedule. It guarantees that all transitions and interactions occur within a strict timestep lifecycle, preventing desynchronization.

### State Ownership & Mappings
- **Graph State**: The network topology is managed by Mesa's `NetworkGrid` which wraps the underlying `NetworkX` graph generator output.
- **Consumer State**: `ConsumerAgent`s are mapped directly to nodes on the `NetworkGrid`. Attributes like `is_adopter`, `sir_state` (0: Susceptible, 1: Infected, 2: Recovered), and `time_infected` are explicitly owned and mutated by the agent instance itself.
- **Global Economic State**: The `GovernmentAgent` and `IndustryAgent` hold global variables (e.g., `budget`, `subsidy`, `panel_price`) that consumers read during their decision step.
- **Metrics State**: The `EnvironmentAgent` and `AnalysisAgent` calculate aggregate statistics (e.g., total CO2 offset, tipping points) using information observed from the consumers and global variables.

## Timestep Lifecycle
During a single timestep (`Model.step()`), activation occurs in a structured sequence to ensure economic bounds exist before consumer decisions:

1. **Global Economic Update**:
   - `GovernmentAgent.step()`: Deducts budget based on adoptions from the *previous* step, and adjusts the subsidy to meet adoption rate targets.
   - `IndustryAgent.step()`: Adjusts the solar panel base price depending on whether demand (previous adoptions) exceeded the pricing threshold.
2. **Consumer Decisions & Transitions**:
   - `ConsumerAgents` step in an arbitrary sequence managed by Mesa's `self.agents`.
   - **SIR Update**: If infected (`sir_state == 1`), `time_infected` increments. Reaching the threshold causes recovery (`sir_state == 2`).
   - **Adoption Decision**: Susceptible agents (`is_adopter == False`) evaluate a deterministic linear combination of:
     1. Baseline probability (Logistic Regression).
     2. Network Influence (derived from infected neighbors on the grid).
     3. Affordability (subsidy / panel_price).
   - If the combined score exceeds a fixed deterministic threshold (0.4), the agent adopts and transitions to the infected state.
3. **Environment & Analysis**:
   - `EnvironmentAgent.step()` calculates total carbon displacement based on total cumulative adoptions.
   - `AnalysisAgent.step()` observes the historical trajectory and attempts algorithmic tipping-point detection.
4. **Data Collection**:
   - The Mesa `DataCollector` snapshots state variables into a structured pandas-compatible row.

## Deterministic Decision Mechanism
To preserve the boundaries required for future LLM integration, consumer decisions remain strictly mathematical in Phase 3A. The hybrid pipeline combines baseline propensity, peer effects, and economic viability. By holding the random seed constant, the trajectory is strictly deterministic, generating identical pandas DataFrames every run.

## Testing Results
- **Total Tests Executed**: 22
- **Passed**: 22
- **Failed**: 0
- **Warnings**: 0

The test suite validates agent mappings, ensures $S+I+R = N$ is strictly conserved at every state transition, confirms finite bounds on the government budget, and strictly verifies identical stochastic outcomes given identical seeds.

## Known Limitations
- The decision function is currently a naive linear combination of variables and uses a hardcoded cutoff (0.4) as a placeholder for the future LLM cognitive engine.
- Industry and Government rules are highly simplified linear adjustments, lacking reinforcement learning or macro-economic forecasting (LSTM) which will be built in later phases.
