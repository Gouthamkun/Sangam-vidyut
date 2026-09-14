# Sangam Vidyut: Live Simulation Dashboard

The **Live Simulation Dashboard** is a genuinely interactive modeling application designed to execute fresh instances of the Sangam Vidyut computational simulation upon request, keeping results completely separate from the locked historical experiment campaigns (Phase 4F.1 - 4F.3).

## Architecture

```mermaid
graph TD
    UI[Streamlit Controls] --> |Run Simulation| LSR[LiveSimulationRunner]
    LSR --> |Arbitrary Inputs| Config[ExperimentConfig]
    Config --> Model[SangamVidyutModel]
    Model --> |step() x Horizon| Runner[Model Execution]
    Runner --> |datacollector + metrics| LSR
    LSR --> |LiveSimulationResult| UI_Tabs[Live Simulation Tab]
    UI_Tabs --> |Plotly| Charts[Interactive Visualizations]
```

## Available Parameters

Users can inject arbitrary numeric and categorical parameters that map directly to the underlying `SangamVidyutModel`.

- **Subsidy (`subsidy`)**: Float. The base subsidy value (e.g., 2500.5, 3333.5).
- **Beta (`beta`)**: Float. Transmission rate bounding the SIR process (e.g., 0.15, 0.173).
- **Population (`population`)**: Integer. Scales the NetworkX graph and the number of ConsumerAgents.
- **Simulation Horizon (`horizon`)**: Integer. Number of quarters to run the model.
- **Government Budget (`budget`)**: Float. Total available finite budget.
- **Seed (`seed`)**: Integer. Guarantees reproducible node placement and base random numbers.
- **Topology**: Categorical (`watts_strogatz`, `barabasi_albert`). Determines network formation.
- **Household Representation**: Categorical (`empirical`, `constant`). Determines probability mapping.
- **Policy Mode**: Categorical (`fixed`, `dynamic`). Enables target-seeking subsidy adjustment.
- **Cognitive Mode**: Categorical (`deterministic`, `mock`, `ollama`). Defines the LLM strategy.

## Distinction from Locked Research Results

The Sangam Vidyut dashboard is strictly split into two layers to preserve scientific integrity:

1. **Live Simulation**: Executes fresh models. Does NOT utilize precomputed CSVs. Outputs are strictly temporary session data and are NOT saved to the locked artifact directories.
2. **Locked Research Results**: Read-only visualization of the finalized 1,060 runs from Phase 4F.1, 4F.2, and 4F.3.

## Cognitive Modes

- **Deterministic**: LLM routing is fully disabled (`lower_threshold` and `upper_threshold` forced to 0.5). All decisions fall to pure rule-based math.
- **MockLLM**: Evaluates ambiguities using deterministic noise simulation, preserving structural API integration logic.
- **Ollama**: Employs LangGraph to query a locally running Ollama engine (`llama3.2:3b`). Failures will accurately report in the UI cognitive metrics section.

## Performance Considerations
Due to the computational intensity of ABMs, the Live Simulation sets sensible interactive defaults (N=500, Horizon=24). Setting a population >= 5000 will produce a user warning as it may severely impact execution times and memory.
