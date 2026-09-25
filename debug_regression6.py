import time
import mesa
import numpy as np
import pandas as pd
from src.config.schema import ExperimentConfig, BehaviorPolicyConfig, CognitiveConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.agents.consumer import ConsumerAgent

# Replicate the exact DETERMINISTIC_EMPIRICAL_ABM configuration from phase_4f_1_campaign
config = ExperimentConfig()
config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
config.cognitive.sync_policy_thresholds()  # Explicitly call to sync thresholds
config.simulation.baseline_provider = "empirical"
config.simulation.n_agents = 500
config.simulation.timesteps = 24
config.simulation.seed = 42
config.network.topology = "watts_strogatz"
config.sir.beta = 0.15
config.sir.recovery_duration_quarters = 2
config.government.dynamic_subsidy = False
config.government.base_subsidy = 2500.0
config.llm.enabled = False
config.llm.provider = "mock"

print(f"Thresholds: lower={config.cognitive.lower_threshold}, upper={config.cognitive.upper_threshold}")
print(f"LLM enabled: {config.llm.enabled}")
print(f"LLM provider: {config.llm.provider}")

print("=" * 80)
print("CONFIGURATION (DETERMINISTIC_EMPIRICAL_ABM from campaign)")
print("=" * 80)

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

print(f"\nInitial adopters after seeding: {sum(1 for a in model.agents if getattr(a, 'is_adopter', False))}")

consumers = [a for a in model.agents if isinstance(a, ConsumerAgent)]

# First step detailed
model.government.step()
model.industry.step()

current_subsidy = model.government.subsidy
current_price = model.industry.panel_price
print(f"\nSubsidy at t=1: {current_subsidy}")
print(f"Panel price at t=1: {current_price}")
print(f"Affordability: {current_subsidy / max(current_price, 1.0):.6f}")

# Check first step decisions for a few agents
for i, agent in enumerate(consumers[:10]):
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
    affordability = min(current_subsidy / max(current_price, 1.0), 1.0)
    score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
    print(f"  Agent {i}: p_base={p_base:.6f}, sir_score={sir_score:.6f}, affordability={affordability:.6f}, score={score:.6f}")

# Full run
print("\n" + "=" * 80)
print("FULL SIMULATION RUN (24 steps)")
print("=" * 80)

model.new_adoptions = 0
model.new_adoptions_last_step = 0

adoption_trajectory = []
new_adoptions_trajectory = []

for step in range(config.simulation.timesteps):
    model.step()
    
    total_adopters = model.total_adopters
    new_adoptions = model.new_adoptions_last_step
    
    adoption_trajectory.append(total_adopters)
    new_adoptions_trajectory.append(new_adoptions)
    
    print(f"  t={step+1}: adopters={total_adopters}, new={new_adoptions}, llm_calls={getattr(model.llm_interface.provider, 'call_count', 0)}")

print(f"\nFinal adoption: {adoption_trajectory[-1]}")
print(f"Total new adoptions: {sum(new_adoptions_trajectory)}")
print("Adoption trajectory:", adoption_trajectory)
print("New adoptions trajectory:", new_adoptions_trajectory)