# Research Scope & Principles

Sangam Vidyut aims to study how households adopt renewable energy under the influence of various socio-economic factors. The scope is strictly limited to rigorous simulation modeling and reproducible experimentation.

## Boundaries
- **In-Scope**: Simulating household solar panel adoption, modeling government subsidies, analyzing pricing trends, comparing Agent-Based Models (ABM) against static regression, tracking emissions impact.
- **Out-of-Scope**: Designing actual solar hardware, enforcing real-world government regulations, real-time grid balancing simulations, or implementing reinforcement learning algorithms (unless explicitly added later).

## Research Principles
1. **Faithfulness**: The implementation must remain faithful to the specified research architecture.
2. **Scientific Integrity**: Do not invent scientific claims that are not supported by the project specification.
3. **Data Separation**: Clearly separate real datasets from synthetic/mock data.
4. **I/O Definition**: Every model must have clearly defined inputs and outputs.
5. **Documentation of Assumptions**: Every major research assumption must be documented in `assumptions.md`.
6. **Reproducibility**: The system must support reproducible experiments with fixed seeds and configurable parameters.
7. **Baseline Separation**: Baseline static models must be implemented separately from the proposed agent-based approach.
8. **Comparative Analysis**: The system must make it possible to compare baseline predictions against agent-based simulation results.
9. **No Silent Replacements**: LLM agents must not silently replace deterministic/statistical models where the architecture specifies Logistic Regression, LSTM, SIR, etc.
10. **Simplicity**: Avoid unnecessary complexity.
11. **Incremental Validation**: Build incrementally and test every module thoroughly.
