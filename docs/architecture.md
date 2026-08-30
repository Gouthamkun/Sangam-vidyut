# Architecture Document: Sangam Vidyut

## 1. Project Overview
Sangam Vidyut is a research-grade simulation framework for studying household adoption of renewable/solar energy. It strictly separates data, modeling, simulation, cognition, analysis, and visualization. The primary research objective is to compare a conventional static statistical baseline (Logistic Regression) against a dynamic, agent-based simulation (Mesa) that incorporates social influence (SIR), policy feedback, and bounded-rationality reasoning (LangGraph).

## 2. Proposed Directory Structure
```
sangam_vidyut/
├── data/
│   ├── raw/                  # Immutable empirical datasets
│   ├── processed/            # Cleaned data ready for modeling
│   └── synthetic/            # Generated data (e.g., personas, network graphs)
├── src/
│   ├── data/                 # Data loading, cleaning, and synthetic generation
│   ├── models/
│   │   ├── statistical/      # Logistic Regression baseline models
│   │   ├── forecasting/      # PyTorch LSTM price/demand models
│   │   └── diffusion/        # SIR mathematical models
│   ├── simulation/
│   │   ├── agents/           # Consumer, Government, Industry, Environment, Analysis
│   │   ├── environment/      # Grid, NetworkX topologies
│   │   └── engine/           # Mesa model definition and scheduler
│   ├── cognition/
│   │   ├── langgraph_flows/  # LLM reasoning orchestration pipelines
│   │   └── prompts/          # Bounded-rationality prompt templates
│   ├── analysis/             # Cascade detection, comparison metrics, emissions math
│   └── visualization/        # Streamlit dashboards, Matplotlib/Plotly scripts
├── tests/                    # Pytest suite (unit, integration, regression)
├── configs/                  # YAML config files for experiments (seeds, params)
├── experiments/              # Scripts to run specific research scenarios
├── outputs/                  # Saved simulation states, logs, and plots
├── docs/                     # Documentation (Architecture, specifications)
├── requirements.txt
└── README.md
```

## 3. Module Boundaries
- **DATA**: Responsible strictly for I/O and preprocessing. Does not run simulations or make predictions.
- **MODELS (Math/Stat)**: Deterministic models (LogReg, LSTM, SIR). Pure mathematical I/O. Independent of Mesa.
- **SIMULATION (Mesa)**: The authoritative engine. Manages time (quarterly steps), agent states, and network updates.
- **COGNITION (LangGraph)**: The reasoning engine. Stateless from a simulation perspective; receives state from Mesa, computes a decision via LLM, and returns it. Does not advance time.
- **ANALYSIS**: Post-processing or mid-simulation observer. Reads state, computes metrics (tipping points, emissions).
- **VISUALIZATION**: Purely presentational. Reads from `outputs/` or active memory to render dashboards.

## 4. Data Contracts Between Modules
- **Data -> Models**: Cleaned Pandas DataFrames or NumPy arrays.
- **Models -> Simulation**: Base probabilities, price forecasts, and network topologies supplied during model initialization.
- **Simulation -> Cognition**: Context dictionary (Household traits, Price, Subsidy, Neighbor Adoption Status, Mathematical Probability).
- **Cognition -> Simulation**: Structured JSON/Pydantic object containing the decision (`adopt: bool`) and a concise reasoning trace (`reasoning: str`).
- **Simulation -> Analysis**: Step-by-step state dictionaries collected via Mesa's `DataCollector`.
- **Analysis -> Visualization**: Aggregated DataFrames and cascade metrics.

## 5. Simulation State Model
The global authoritative state is held entirely in Mesa.
- **Global Environment**: Current Step (Quarter), Global Panel Price, Current Subsidy Tier, Total Adoptions.
- **Network State**: NetworkX graph defining household connections and current SIR statuses (S, I, R).
- **Agent State**: `is_adopter` (bool), `financial_status`, `sir_state`, `cached_reasoning_hash`.

## 6. Mesa and LangGraph Communication
Mesa acts as the master controller.
- During a Mesa step, a `ConsumerAgent` computes its mathematical probability to adopt.
- If the probability falls in the "ambiguous middle band" (e.g., $0.4 < P < 0.6$), the agent constructs a `CognitiveRequest` object.
- Mesa synchronously invokes a LangGraph workflow passing the `CognitiveRequest`.
- LangGraph orchestrates the LLM reasoning, validates the output, and returns a `CognitiveResponse`.
- Mesa applies the decision to the agent's authoritative state.

## 7. Consumer Agent Decision Pipeline
1. **Mathematical Baseline**: Calculate base adoption probability $P_{base}$ using Scikit-Learn Logistic Regression based on demographics.
2. **Economic Adjustment**: Adjust $P_{base}$ based on current PyTorch LSTM Price and Government Subsidy.
3. **Social Influence**: Add the SIR score calculated from adopting neighbors (NetworkX edges).
4. **Threshold Check**: Yield final probability $P_{final}$.
   - If $P_{final} > \tau_{upper}$ (e.g., 0.75): Deterministic YES.
   - If $P_{final} < \tau_{lower}$ (e.g., 0.25): Deterministic NO.
   - If $\tau_{lower} \le P_{final} \le \tau_{upper}$: Ambiguous.
5. **Cognitive Fallback**: Invoke LangGraph. The LLM acts under bounded rationality to output YES/NO based on the ambiguous context.
6. **State Update**: Apply decision. Update SIR state (S $\rightarrow$ I).

## 8. Baseline vs. ABM Experiment Design
The framework runs two parallel tracks for a given scenario:
- **Track A (Static Baseline)**: Projects $N$ quarterly steps using only the Logistic Regression model, establishing a linear/logistic adoption curve without network effects or dynamic policy changes.
- **Track B (ABM)**: Runs the full Mesa simulation for $N$ steps.
- **Comparison**: The Analysis module calculates the Delta between Track A and Track B adoption curves, isolating the quantitative impact of social contagion (SIR) and dynamic policy feedback.

## 9. Reproducibility Requirements
- **Config-Driven**: Every run is defined by a YAML configuration file specifying hyperparameters, network topology, LLM temperature, and paths to datasets.
- **Deterministic Seeds**: All random number generators (Python, NumPy, PyTorch, Mesa, NetworkX) initialized with a fixed seed from the config.
- **LLM Caching**: LangGraph LLM responses are cached with a hash of the input state. This controls costs and ensures the exact same simulation trajectory can be replayed.
- **Data Versioning**: Input data remains read-only.
- **Structured Logs**: Mesa DataCollector writes step-by-step state to immutable CSV/Parquet files.

## 10. Testing Strategy
- **Unit Tests (Pytest)**: Test mathematical models (LogReg, LSTM, SIR) independently with mock data. Test LangGraph output parsing.
- **Integration Tests**: Verify that Mesa correctly calls LangGraph and correctly applies the state transition.
- **Deterministic Regression Tests**: Run a short simulation (e.g., 10 steps, 100 agents) with a fixed seed and assert the final state matches a known good snapshot exactly.

## 11. Implementation Roadmap
- **Phase 1: Foundation**: Set up directory structure, configuration management, data loaders, and basic tests.
- **Phase 2: Mathematical Baselines**: Implement Scikit-learn LogReg, PyTorch LSTM, and pure SIR diffusion math.
- **Phase 3: Mesa Core**: Implement Mesa environment, `NetworkGrid`, and deterministic agents (no LLMs yet).
- **Phase 4: Cognition**: Integrate LangGraph, prompt templates, decision thresholds, and LLM caching.
- **Phase 5: Analysis & Visualization**: Implement cascade detection, environment metrics, and Streamlit dashboards.

## 12. Ambiguities & Missing Research Decisions
- **SIR Recovery Rate**: What is the biological equivalent of "Recovery" for a household with solar panels? Does word-of-mouth influence decay over 1 year (4 quarters)? This parameter requires a clear research definition.
- **LSTM Data Sufficiency**: Do we have enough historical quarterly panel pricing data to train a meaningful PyTorch LSTM? If not, do we fall back to a simpler statistical time-series model (ARIMA)?
- **Government Budget Constraints**: Is the Government Agent constrained by a hard budget, or can it issue infinite subsidies if adoption targets are missed?
- **Network Sizing**: What is the target number of agents $N$? Performance degrades non-linearly with large networks when LangGraph is involved.

## 13. Architectural Risks
- **Compute Runaway**: Even with the threshold design, a "tipping point" cascade could push a massive number of agents into the ambiguous band simultaneously, causing a spike in API costs and latency.
- **LangGraph Leaking State**: If LangGraph is allowed to maintain long-term memory internally rather than relying on Mesa state, the simulation will become impossible to pause, serialize, or reproduce deterministically.
- **Threshold Tuning**: If $\tau_{upper}$ and $\tau_{lower}$ are not calibrated properly, the LLM might either never be called (defeating the purpose) or always be called (destroying the budget). Calibration experiments must precede actual research runs.
