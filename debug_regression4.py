import time
import mesa
import numpy as np
import pandas as pd
from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.agents.consumer import ConsumerAgent

# Test with cognitive_accessible_candidate_v1 thresholds (0.05, 0.20)
# Set policy name BEFORE creating config
config = ExperimentConfig()
config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
# Now the validator should have run
print(f"After policy name set: lower={config.cognitive.lower_threshold}, upper={config.cognitive.upper_threshold}")

config.government.base_subsidy = 2500.0
config.sir.beta = 0.15
config.simulation.n_agents = 500
config.simulation.timesteps = 24
config.simulation.seed = 42
config.government.initial_budget = 1000000.0
config.sir.recovery_duration_quarters = 2
config.network.topology = "watts_strogatz"
config.simulation.baseline_provider = "empirical"
config.llm.enabled = False

print("=" * 80)
print("CONFIGURATION (cognitive_accessible_candidate_v1 THRESHOLDS: lower=0.05, upper=0.20)")
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
print(f"Thresholds: lower={config.cognitive.lower_threshold}, upper={config.cognitive.upper_threshold}")

# p_base distribution
empirical_agents = [a for a in model.agents if isinstance(a, ConsumerAgent)]
p_base_vals = [model.baseline_provider.predict(a) for a in empirical_agents]
p_base_vals = np.array(p_base_vals)
print(f"\np_base: min={p_base_vals.min():.6f}, max={p_base_vals.max():.6f}, mean={p_base_vals.mean():.6f}")

# First step detailed
model.government.step()
model.industry.step()

current_subsidy = model.government.subsidy
current_price = model.industry.panel_price
print(f"\nSubsidy at t=1: {current_subsidy}")
print(f"Panel price at t=1: {current_price}")
print(f"Affordability: {current_subsidy / max(current_price, 1.0):.6f}")

sir_scores = []
affordability_vals = []
combined_scores = []
decisions = []

for agent in empirical_agents:
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
    sir_scores.append(sir_score)
    
    affordability = min(current_subsidy / max(current_price, 1.0), 1.0)
    affordability_vals.append(affordability)
    
    score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
    combined_scores.append(score)
    
    lower_thresh = config.cognitive.lower_threshold
    upper_thresh = config.cognitive.upper_threshold
    
    decision = False
    if score >= upper_thresh:
        decision = True
    elif score <= lower_thresh:
        decision = False
    else:
        decision = False  # LLM disabled
    
    decisions.append(decision)

sir_scores = np.array(sir_scores)
affordability_vals = np.array(affordability_vals)
combined_scores = np.array(combined_scores)
decisions = np.array(decisions)

print(f"\nsir_score: min={sir_scores.min():.6f}, max={sir_scores.max():.6f}, mean={sir_scores.mean():.6f}")
print(f"affordability: min={affordability_vals.min():.6f}, max={affordability_vals.max():.6f}, mean={affordability_vals.mean():.6f}")
print(f"combined score: min={combined_scores.min():.6f}, max={combined_scores.max():.6f}, mean={combined_scores.mean():.6f}")
print(f"adopt decisions at t=1: {decisions.sum()} / {len(decisions)}")

lower_thresh = config.cognitive.lower_threshold
upper_thresh = config.cognitive.upper_threshold
print(f"\nAgents above upper threshold ({upper_thresh}): {(combined_scores >= upper_thresh).sum()}")
print(f"Agents below lower threshold ({lower_thresh}): {(combined_scores <= lower_thresh).sum()}")
print(f"Agents in ambiguous zone: {((combined_scores > lower_thresh) & (combined_scores < upper_thresh)).sum()}")

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
    
    print(f"  t={step+1}: adopters={total_adopters}, new={new_adoptions}")

print(f"\nFinal adoption: {adoption_trajectory[-1]}")
print(f"Total new adoptions: {sum(new_adoptions_trajectory)}")
print("Adoption trajectory:", adoption_trajectory)
print("New adoptions trajectory:", new_adoptions_trajectory)