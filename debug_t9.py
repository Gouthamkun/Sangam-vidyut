import time
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

# Replicate the exact DETERMINISTIC_EMPIRICAL_ABM configuration from phase_4f_1_campaign
config = ExperimentConfig()
config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
config.cognitive.sync_policy_thresholds()
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

# Run to t=8 (just before adoption happens)
for step in range(8):
    model.step()
    print(f"t={step+1}: adopters={model.total_adopters}, new={model.new_adoptions_last_step}, price={model.industry.panel_price:.0f}, subsidy={model.government.subsidy:.0f}")

# Now at t=8, check combined scores before t=9 step
print("\n=== At t=8 (before t=9 step) ===")
print(f"Panel price: {model.industry.panel_price:.0f}")
print(f"Subsidy: {model.government.subsidy:.0f}")
print(f"Affordability: {model.government.subsidy / max(model.industry.panel_price, 1.0):.4f}")

# Count infected agents
infected_count = sum(1 for a in consumers if a.sir_state == 1)
recovered_count = sum(1 for a in consumers if a.sir_state == 2)
print(f"Infected agents: {infected_count}")
print(f"Recovered agents: {recovered_count}")

# Check combined scores for all susceptible agents
scores = []
for agent in consumers:
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
    
    scores.append({
        'p_base': p_base,
        'infected_neighbors': infected_neighbors,
        'sir_score': sir_score,
        'affordability': affordability,
        'score': score
    })

scores_df = pd.DataFrame(scores)
print(f"\nScore stats: min={scores_df['score'].min():.4f}, max={scores_df['score'].max():.4f}, mean={scores_df['score'].mean():.4f}")
print(f"Score percentiles:")
for p in [0, 10, 25, 50, 75, 90, 95, 99, 100]:
    print(f"  P{p}: {scores_df['score'].quantile(p/100):.4f}")

print(f"\nInfected neighbors distribution:")
print(scores_df['infected_neighbors'].value_counts().sort_index())

# Check agents with highest scores
top_scores = scores_df.nlargest(10, 'score')
print(f"\nTop 10 scores:")
print(top_scores.to_string())

# Now step to t=9
print("\n=== Stepping to t=9 ===")
model.step()
print(f"t=9: adopters={model.total_adopters}, new={model.new_adoptions_last_step}")

# Check who adopted
new_adopters = [a for a in consumers if a.is_adopter and a.time_infected == 0]
print(f"New adopters at t=9: {len(new_adopters)}")
for a in new_adopters[:5]:
    print(f"  Agent {a.unique_id}: p_base={model.baseline_provider.predict(a):.6f}")