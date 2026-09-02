# Phase 4A Implementation: Experimental Framework

## Objective
Establish a reproducible, modular experimental runner to quantitatively compare four model permutations of Sangam Vidyut (STATIC_BASELINE, SIR_ONLY, DETERMINISTIC_ABM, FULL_COGNITIVE_ABM) under controlled configurations.

## Architecture & Modules
The experiment runner is fully decoupled from the core simulation logic, living in `experiments/`:
- `experiments/schemas.py`: Strictly defines `ExperimentConfig` and `ExperimentResult` schemas using Pydantic.
- `experiments/runners.py`: Maps configs to one of the four executable models, executing the appropriate simulation logic and scraping results into the unified output schema.
- `experiments/batch.py`: Sequentially executes multiple `ExperimentConfig` definitions and saves the outputs directly to the `outputs/` directory.

## Model Configurations
1. **STATIC_BASELINE**: Instantiates an independent set of agents, extracts their properties, and predicts uniform probabilities using the fitted Logistic Regression model. Diffusion and step time are ignored.
2. **SIR_ONLY**: Seeds exactly 5 nodes into a constructed Watts-Strogatz network and performs pure numerical diffusion utilizing `src.models.diffusion.sir.PureSIRModel`. No ABM cognition applies.
3. **DETERMINISTIC_ABM**: Instantiates `SangamVidyutModel` but overrides the routing configuration (`lower_threshold=0.5`, `upper_threshold=0.5`) to strictly bypass the cognitive LLM interface, forcing purely mathematical consumer responses.
4. **FULL_COGNITIVE_ABM**: Instantiates `SangamVidyutModel` using standard thresholds (`0.3` to `0.7`) and active structural caching. Routes ambiguous decisions to LangGraph (utilizing a safely fallback-mocked ChatModel if no API keys are present in CI).

## Metrics & Outputs
Every run strictly saves a JSON record satisfying this schema:
```json
{
  "experiment_id": "string",
  "model_type": "string",
  "seed": "int",
  "population": "int",
  "timesteps": "int",
  "final_adoption": "int",
  "final_adoption_rate": "float",
  "cumulative_adoptions": ["list of int"],
  "tipping_point": "int or null",
  "total_llm_calls": "int",
  "total_cache_hits": "int",
  "total_llm_failures": "int",
  "cumulative_co2_displaced": "float or null"
}
```
*Note*: The separation between per-step and cumulative metrics (enforced in Phase 3C) provides the data for these end-of-simulation scalars.

## Reproducibility Strategy
All permutations derive from a unified `ExperimentConfig`. The `seed` variable is explicitly passed into the configuration, cascading deterministic consistency to Numpy, NetworkX, and the MockLLM instances. A strict check verifies that identical seeds yield identical `final_adoption` curves, while altered seeds yield topological and temporal variation.

## Limitations
- **No GUI**: Experimental execution is purely programmatic.
- **LLM CI Bypass**: Running `FULL_COGNITIVE_ABM` during automated pipelines utilizes `MockLLMProvider` or `FakeListChatModel` via `langgraph`, rather than consuming real API tokens, fulfilling testing safety protocols. Real usage requires an explicit `OPENAI_API_KEY` loaded in the runtime environment.
