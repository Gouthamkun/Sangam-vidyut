import sys
import os
import mesa
sys.path.insert(0, os.path.abspath("."))

from src.config.schema import ExperimentConfig, BehaviorPolicyConfig, CognitiveConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.agents.consumer import ConsumerAgent
import pandas as pd
import numpy as np

# Minimal test - just run 1 step with LLM and check decisions
config = ExperimentConfig()
config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
config.cognitive.sync_policy_thresholds()
config.simulation.baseline_provider = "empirical"
config.simulation.n_agents = 100  # Smaller for speed
config.simulation.timesteps = 1
config.simulation.seed = 42
config.network.topology = "watts_strogatz"
config.sir.beta = 0.15
config.sir.recovery_duration_quarters = 2
config.government.dynamic_subsidy = False
config.government.base_subsidy = 2500.0
config.llm.enabled = False
config.llm.provider = "mock"
config.government.initial_budget = 1000000.0

np.random.seed(config.simulation.seed)

model = SangamVidyutModel(config)

pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
pop_df = pd.read_parquet(pop_path).head(config.simulation.n_agents)

for agent in list(model.agents):
    if isinstance(agent, ConsumerAgent):
        if hasattr(agent, 'pos') and agent.pos is not None:
            model.grid.remove_agent(agent)
        model.agents.remove(agent)

for i, row in pop_df.iterrows():
    agent = create_consumer_from_household_record(model, row)
    model.grid.place_agent(agent, i)

initial_adoption = 5
for a in model.agents:
    if hasattr(a, 'is_adopter'):
        a.is_adopter = False
        a.sir_state = 0

initial_nodes = np.random.choice(model.G.nodes(), size=initial_adoption, replace=False)
for node in initial_nodes:
    agent_list = model.grid.get_cell_list_contents([node])
    for a in agent_list:
        if hasattr(a, 'is_adopter'):
            a.is_adopter = True
            a.sir_state = 1

consumers = [a for a in model.agents if isinstance(a, ConsumerAgent)]

# Manually run government/industry step
model.government.step()
model.industry.step()

print(f"Panel price: {model.industry.panel_price:.0f}")
print(f"Subsidy: {model.government.subsidy:.0f}")
print(f"Affordability: {model.government.subsidy / max(model.industry.panel_price, 1.0):.4f}")

# Test MockLLM directly
from src.simulation.llm.providers import MockLLMProvider
mock_llm = MockLLMProvider(config)

# Test with a high-score agent context
test_context = {
    "combined_score": 0.195,
    "income": 3000,
    "home_owner": -1,
    "sir_score": 0.0,
    "affordability": 0.75,
    "panel_price": 3317,
    "subsidy": 2500,
    "adopting_neighbors": 0,
    "total_neighbors": 4,
    "prompt_version": "v1",
    "model_identifier": "mock",
    "provider": "mock",
    "temperature": 0.1
}

print("\nTesting MockLLM directly:")
for i in range(10):
    decision = mock_llm.generate_decision(test_context)
    print(f"  Call {i+1}: decision={decision}")

# Now test with actual agent contexts
print("\nTesting with actual agent contexts:")
adopt_count = 0
for agent in consumers[:20]:
    if agent.is_adopter:
        continue
    
    p_base = model.baseline_provider.predict(agent)
    neighbors = model.grid.get_neighbors(agent.pos, include_center=False)
    infected_neighbors = 0
    for item in neighbors:
        if isinstance(item, mesa.Agent):
            if getattr(item, 'sir_state', 0) == 1:
                infected_neighbors += 1
        else:
            agents_in_cell = model.grid.get_cell_list_contents([item])
            for a in agents_in_cell:
                if isinstance(a, ConsumerAgent) and getattr(a, 'sir_state', 0) == 1:
                    infected_neighbors += 1
    
    sir_score = 1.0 - (1.0 - config.sir.beta) ** infected_neighbors
    affordability = min(model.government.subsidy / max(model.industry.panel_price, 1.0), 1.0)
    score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
    
    context = {
        "agent_id": agent.unique_id,
        "timestep": model.timestep,
        "income": agent.income,
        "home_owner": agent.home_owner,
        "sir_score": sir_score,
        "affordability": affordability,
        "combined_score": score,
        "panel_price": model.industry.panel_price,
        "subsidy": model.government.subsidy,
        "adopting_neighbors": infected_neighbors,
        "total_neighbors": len(neighbors),
        "prompt_version": config.llm.prompt_version,
        "model_identifier": config.llm.model,
        "provider": config.llm.provider,
        "temperature": config.llm.temperature
    }
    
    decision = mock_llm.generate_decision(context)
    if decision:
        adopt_count += 1
        print(f"  Agent {agent.unique_id}: p_base={p_base:.6f}, score={score:.6f}, decision=ADOPT")
    else:
        print(f"  Agent {agent.unique_id}: p_base={p_base:.6f}, score={score:.6f}, decision=REJECT")

print(f"\nTotal adoptions in sample: {adopt_count}")