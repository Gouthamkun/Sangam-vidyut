# Phase 3C: Real LangGraph + LLM Cognitive Layer

## Architecture Overview
Phase 3C replaces the simulated mock LLM with a robust, production-ready cognitive workflow orchestrated by **LangGraph**. The simulation remains fully driven by Mesa, treating the LLM as a stateless, bounded-rationality inference engine used strictly for evaluating "ambiguous" household decisions.

### Provider Abstraction
We maintain strict modularity via the `LLMInterface` and `BaseLLMProvider`.
- `MockLLMProvider`: Preserved for rapid, API-free deterministic testing.
- `LangGraphLLMProvider`: Compiles and invokes a LangGraph workflow to resolve ambiguous decisions using a real Chat Model.

### LangGraph Workflow
The orchestration leverages `langgraph` and `langchain-core` to construct a minimal, directed acyclic graph:
1. **Prepare Context Node**: Transforms numerical agent state (income, neighbors, affordability) into a structured string prompt, establishing the persona and constraints.
2. **Reason and Decide Node**: Invokes the LLM using `.with_structured_output(HouseholdDecision)`.
3. **Structured Output**: Forces the LLM to return a strictly typed `pydantic` schema containing:
   - `decision`: "ADOPT" or "WAIT"
   - `confidence`: float (0.0 to 1.0)
   - `reasoning_summary`: concise explanation string.

### Strict State Authority
Mesa remains the sole authoritative engine.
- The LLM receives contextual snapshots (read-only).
- The LLM cannot mutate `ConsumerAgent` state, advance time, or modify policies.
- The LLM returns a structured decision, which the agent (running in the Mesa `step` loop) interprets and acts upon.

## LLM Cost Control & Fallback

### Mathematical Routing
Only households in the "ambiguous" zone of the mathematical prior (default `0.3 < score < 0.7`) invoke the LLM. Clear decisions instantly bypass the LLM, tracking explicitly via the `decision_path` ("rule" vs "llm").

### Cognitive Caching
A secure cache hashes the structural context of the decision (omitting the `agent_id`). If multiple agents encounter structurally identical environments (same income, neighbor states, and economic conditions), the cache intercepts the request, returning the previous LLM evaluation and preventing an API call.

### Fallback Mechanism
If the LLM fails (e.g., rate limits, context length, parsing errors), a fallback layer catches the exception. If `fallback_enabled=True`, it reverts to a simple mathematical threshold (e.g., `combined_score >= 0.5`) and logs the failure without crashing the simulation or dropping the timestep.

## Research Logging & Metrics
The `DataCollector` now observes detailed cognitive metrics per timestep:
- `rule_decisions`: Decisions handled purely by mathematics.
- `llm_decisions`: Decisions handled by the LangGraph workflow.
- `llm_calls`: Distinct requests passed to the underlying provider.
- `cache_hits` / `cache_misses`: Cache efficiency tracking.
- `llm_failures` / `fallback_decisions`: Robustness tracking.

These metrics enable comprehensive ablation studies (e.g., comparing network diffusion rates between "Rule-only" and "Hybrid LLM" configurations).

## Security & Reproducibility
- **No Hardcoded Credentials**: API Keys must be provided via the local environment (`OPENAI_API_KEY`, etc.).
- **CI/CD Compatibility**: Standard pytest runs leverage `FakeListChatModel` or dummy implementations, ensuring tests execute instantly offline without requiring real API billing.
- **Reproducibility Limit**: Because real LLMs introduce token stochasticity (even at `temperature=0`), strict bit-for-bit deterministic reproducibility is no longer guaranteed when traversing the `LangGraphLLMProvider`. However, the mathematical foundation remains locked by seed.

## Test Results
- **Total Tests Executed**: 27
- **Passed**: 27
- **Failed**: 0
- **Warnings**: 0

*Tests seamlessly swap `MockLLMProvider` and `LangGraphLLMProvider`, verifying cache functionality, threshold boundaries, fallback triggers, and structured output parsing.*
