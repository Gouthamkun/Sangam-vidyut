# Phase 4C Experiment 3B Plan: Real LLM Validation

## 1. Research Objective
Evaluate the `FULL_COGNITIVE_ABM` initialized with a *real* LangGraph + LLM provider against the `DETERMINISTIC_ABM` baseline, under strictly controlled architectural boundaries.

## 2. Experimental Controls
- **Agents**: `n_agents = 100`
- **Simulation Duration**: `12` timesteps (quarters)
- **Seeds**: `[42, 100, 200, 300, 400]` 
- **Topology**: Fixed (`watts_strogatz`)
- **Economic Mechanics**: Identical initialization of baseline subsidy and panel pricing.

## 3. Infrastructure & Safeguards Implemented
Prior to executing the real API calls, the simulation infrastructure has been augmented and hardened:

- **Provenance Tracking**: Both `ExperimentResult` and `AggregatedResult` schemas have been updated to explicitly capture the `provider` name (`LangGraphLLMProvider` vs `MockLLMProvider`), the `model_identifier` (e.g., `gpt-4o-mini`), the `prompt_version`, and any specific `model_configuration` hyperparameters (like `temperature`).
- **Strict API Validation**: The LangGraph workflow (`workflow.py`) has been modified to eliminate silent degradation. If a real LLM is requested but no `OPENAI_API_KEY` is present, it explicitly throws a `ValueError` rather than falling back to the dummy runnable. The dummy runnable is now exclusively invoked only via explicit flags (like `SANGAM_VIDYUT_DRY_RUN`).
- **Failure & Fallback Telemetry**: The LLM interface rigorously catches provider exceptions (like API timeouts or token limits) and increments `LLMInterface.failures` and `LLMInterface.fallbacks`, forcing the agent to cleanly drop back to the mathematical baseline (`score >= 0.5`). These fallback rates are recorded.
- **Dry-Run Validation**: A dry-run version of this script (`run_exp3b.py`) was successfully executed using the explicit dummy flag, verifying parallel execution, data collection, and schema validation.

## 4. Scientific Approach & Expected Outcomes
We **do not assume** that replacing the mock probabilistic noise with genuine LLM cognition will necessarily increase the adoption rate. 

Three distinct hypotheses are plausible:
1. **Real LLM > Deterministic**: The LLM may interpret borderline affordability scores favorably, recognizing the long-term utility of the subsidy, thus tipping adoption where the math fails.
2. **Real LLM < Deterministic**: The LLM might act strictly conservative, placing heavy emphasis on the "WAIT" logic due to the upfront cost, suppressing adoption even lower than mathematical expectations.
3. **Real LLM ≈ Deterministic**: The LLM may closely mirror the strict mathematical boundaries if the prompt structure heavily clamps the response vectors.

## 5. Next Steps
The infrastructure is ready. No real API calls have been made.
**Awaiting User Authorization** to remove the `dry_run` flag and execute the 10-run (5-seed) full experiment utilizing real OpenAI credits.
