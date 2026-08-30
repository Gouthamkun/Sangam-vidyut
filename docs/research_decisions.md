# Sangam Vidyut — Research Principles

## 1. Research Reproducibility
Every experiment must be reproducible using fixed random seeds, documented configuration, versioned datasets where possible, and explicit experiment parameters. The simulation framework must yield identical results given identical initial states and random seeds.

## 2. Baseline vs Proposed Model
The project maintains a strict, quantitative separation between:
- **A. Statistical baseline**: Logistic Regression, LSTM models where applicable.
- **B. Classical diffusion baseline**: SIR-based network diffusion.
- **C. Proposed model**: Mesa Agent-Based Model featuring Consumer, Government, and Industry Agents, LangGraph orchestration, social-network diffusion, and policy feedback.

The system is designed to allow quantitative comparison between these approaches.

## 3. Modularity
Each major research component must be independently testable:
- Data
- Persona Generation
- Adoption Calibration
- Price-Demand Model
- Social Network
- SIR Diffusion
- Mesa Simulation
- LLM Agents
- Policy Model
- Emission Model
- Cascade Detection
- Evaluation
- Visualization

## 4. LLM Role
LLMs must not replace deterministic mathematical models without explicit justification. LLMs are responsible primarily for agent reasoning, qualitative decision-making, and bounded-rationality behavior. Statistical and mathematical models remain explicit and independently measurable.

## 5. Data Provenance
The framework will clearly distinguish between:
- **Real empirical data**
- **Derived data**
- **Synthetic data**
- **Simulated data**
Synthetic data will never be presented as empirical evidence.

## 6. Experimental Validity
Every proposed model defines its:
- **Input**
- **Processing**
- **Output**
- **Evaluation metric**
- **Baseline**
- **Assumptions**
- **Limitations**

---

## Simulation Granularity
Selecting an appropriate time-step is critical for validity.
- **Monthly**: Captures seasonal trends in adoption and subsidy announcements, but may be too fine-grained for large simulations, inflating compute costs.
- **Quarterly**: A strong balance. Household financial planning and major utility-scale decisions often happen on a quarterly cycle.
- **Yearly**: Computationally cheap, but too coarse to model rapid viral contagion cascades.

**Recommendation**: Default to **Quarterly (3 months/step)** to balance realistic household decision-latency with computational efficiency. The design will keep the time-step fully configurable as `T_step`.

---

## LLM Compute Strategy
To control costs and maintain research viability, LLM calls are **NOT** required for every household at every simulation step.
- **Persona Generation Once**: Generate agent personas at initialization.
- **Event-Triggered LLM Calls**: Call the LLM only when an agent is activated by a trigger (e.g., neighbor adopted, subsidy changed).
- **Decision Caching**: Cache agent reasoning for identical state vectors.
- **Representative-Agent Sampling**: LLMs simulate a subset of representative nodes; similar nodes follow deterministic nearest-neighbor policies.
- **Deterministic Fallback Behavior**: If no major state change occurs, use cheap mathematical probabilities instead of querying the LLM.
- **Batch Reasoning**: Group multiple households into a single LLM prompt to compute parallel decisions.
