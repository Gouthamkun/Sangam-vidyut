# Simulation Design

## Mesa + LangGraph Separation

The architecture enforces a strict boundary between the simulation environment and the cognitive reasoning engine. **LangGraph must not become the simulation engine.**

### Mesa Responsibilities
- **Simulation State**: Holds the global grid/network and current step count.
- **Agents**: Maintains instances of agents and their spatial/network relationships.
- **Environment**: Manages exogenous variables like global temperature or macroeconomic markers.
- **Time Progression**: Steps the simulation forward (e.g., `model.step()`).
- **Interactions**: Handles message passing between nodes on the graph.
- **Data Collection**: Employs `DataCollector` to gather state data at every step.

### LangGraph Responsibilities
- **LLM Reasoning Workflows**: Structures the prompts and sequence of thoughts for complex agents.
- **Agent Orchestration**: Maps cognitive state transitions (e.g., "Analyze Subsidy" -> "Evaluate Affordability" -> "Make Decision").
- **Structured Decision Processes**: Guarantees deterministic output parsing from LLM text.
- **Tool Invocation**: Allows LLM agents to call calculators or look up policy rules.
- **Stateful Reasoning**: Maintains short-term memory of the agent's thought process within a single decision step.

## Simulation Outputs
The framework will capture and produce the following final artifacts:
1. **Renewable Adoption Curve Forecast**
2. **Confidence Intervals** (derived from Monte Carlo iterations of the ABM)
3. **Policy Scenario Comparison**
4. **Static Baseline vs Agent-Based Model Comparison**
5. **Cascade/Tipping-Point Detection**
6. **Emission Impact** (CO2 mitigated)
7. **Subsidy Recommendation**
8. **Experiment Results Data**
