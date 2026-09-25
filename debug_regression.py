import time
import mesa
import numpy as np
import pandas as pd
from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.agents.consumer import ConsumerAgent

# Exact configuration from the bug report
config = ExperimentConfig()
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
config.cognitive.lower_threshold = 0.5
config.cognitive.upper_threshold = 0.5

print("=" * 80)
print("CONFIGURATION")
print("=" * 80)
print(f"subsidy: {config.government.base_subsidy}")
print(f"beta: {config.sir.beta}")
print(f"population: {config.simulation.n_agents}")
print(f"horizon: {config.simulation.timesteps}")
print(f"topology: {config.network.topology}")
print(f"household_mode: {config.simulation.baseline_provider}")
print(f"cognitive_mode: deterministic")
print(f"policy: fixed")
print(f"initial_adoption: 5")
print(f"recovery: {config.sir.recovery_duration_quarters}")
print(f"seed: {config.simulation.seed}")

# Set seeds
np.random.seed(config.simulation.seed)

# Create model
model = SangamVidyutModel(config)

# Load population
pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
pop_df = pd.read_parquet(pop_path).head(config.simulation.n_agents)

# Remove default mock consumer agents
for agent in list(model.agents):
    if isinstance(agent, ConsumerAgent):
        if hasattr(agent, 'pos') and agent.pos is not None:
            model.grid.remove_agent(agent)
        model.agents.remove(agent)

# Inject synthetic agents
for i, row in pop_df.iterrows():
    agent = create_consumer_from_household_record(model, row)
    model.grid.place_agent(agent, i)

# Verify all empirical agents have required fields
print("\n" + "=" * 80)
print("1. EMPIRICAL AGENT FIELD VERIFICATION")
print("=" * 80)
empirical_agents = [a for a in model.agents if isinstance(a, ConsumerAgent)]
print(f"Total ConsumerAgents: {len(empirical_agents)}")

required_fields = ['derived_mpce', 'household_size', 'sector', 'dwelling_type', 
                   'electricity_access', 'free_electricity']
for field in required_fields:
    has_field = all(hasattr(a, field) for a in empirical_agents)
    print(f"  {field}: {'ALL HAVE' if has_field else 'MISSING'}")

# Check for NaN in dwelling_type
nan_dwelling = sum(1 for a in empirical_agents if pd.isna(getattr(a, 'dwelling_type', None)))
print(f"  dwelling_type NaN count: {nan_dwelling}")

# Override initial adoption
initial_adoption = 5
for a in model.agents:
    if hasattr(a, 'is_adopter'):
        a.is_adopter = False
        a.sir_state = 0

initial_nodes = np.random.choice(model.G.nodes(), size=initial_adoption, replace=False)
print(f"\nInitial adopter nodes: {initial_nodes}")
for node in initial_nodes:
    agent_list = model.grid.get_cell_list_contents([node])
    for a in agent_list:
        if hasattr(a, 'is_adopter'):
            a.is_adopter = True
            a.sir_state = 1

# Verify initial adopters
print(f"\nInitial adopters after seeding: {sum(1 for a in model.agents if getattr(a, 'is_adopter', False))}")
print(f"Initial SIR=1 count: {sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 1)}")

# Get p_base distribution
print("\n" + "=" * 80)
print("2. P_BASE DISTRIBUTION (t=0, before any steps)")
print("=" * 80)
p_base_vals = []
for agent in empirical_agents:
    p_base = model.baseline_provider.predict(agent)
    p_base_vals.append(p_base)
p_base_vals = np.array(p_base_vals)
print(f"  min: {p_base_vals.min():.6f}")
print(f"  max: {p_base_vals.max():.6f}")
print(f"  mean: {p_base_vals.mean():.6f}")
print(f"  std: {p_base_vals.std():.6f}")

# Print threshold
lower_thresh = config.cognitive.lower_threshold
upper_thresh = config.cognitive.upper_threshold
print(f"\nDecision thresholds: lower={lower_thresh}, upper={upper_thresh}")

# Manually run first step with detailed instrumentation
print("\n" + "=" * 80)
print("3. FIRST STEP DETAILED INSTRUMENTATION (t=1)")
print("=" * 80)

# Government and Industry step
model.government.step()
model.industry.step()

current_subsidy = model.government.subsidy
current_price = model.industry.panel_price
print(f"Subsidy at t=1: {current_subsidy}")
print(f"Panel price at t=1: {current_price}")
print(f"Affordability (subsidy/price): {current_subsidy / max(current_price, 1.0):.6f}")

sir_scores = []
affordability_vals = []
combined_scores = []
decisions = []
p_base_at_t1 = []

for agent in empirical_agents:
    if agent.is_adopter:
        continue
    
    # p_base
    p_base = model.baseline_provider.predict(agent)
    p_base_at_t1.append(p_base)
    
    # SIR score
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
    
    # Affordability
    affordability = min(current_subsidy / max(current_price, 1.0), 1.0)
    affordability_vals.append(affordability)
    
    # Combined score
    score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
    combined_scores.append(score)
    
    # Decision
    decision = False
    if score >= upper_thresh:
        decision = True
    elif score <= lower_thresh:
        decision = False
    else:
        # Would call LLM, but disabled
        decision = False  # fallback
    
    decisions.append(decision)

p_base_at_t1 = np.array(p_base_at_t1)
sir_scores = np.array(sir_scores)
affordability_vals = np.array(affordability_vals)
combined_scores = np.array(combined_scores)
decisions = np.array(decisions)

print(f"\nInfected neighbors distribution: {np.bincount([int(s / config.sir.beta) for s in sir_scores if s > 0]) if len(sir_scores) > 0 else 'none'}")
print(f"Number of susceptible agents: {len(p_base_at_t1)}")

print(f"\np_base at t=1: min={p_base_at_t1.min():.6f}, max={p_base_at_t1.max():.6f}, mean={p_base_at_t1.mean():.6f}")
print(f"sir_score at t=1: min={sir_scores.min():.6f}, max={sir_scores.max():.6f}, mean={sir_scores.mean():.6f}")
print(f"affordability at t=1: min={affordability_vals.min():.6f}, max={affordability_vals.max():.6f}, mean={affordability_vals.mean():.6f}")
print(f"combined score at t=1: min={combined_scores.min():.6f}, max={combined_scores.max():.6f}, mean={combined_scores.mean():.6f}")
print(f"adopt decisions at t=1: {decisions.sum()} / {len(decisions)}")

# Score distribution histogram
print(f"\nCombined score histogram (bins=10):")
hist, bins = np.histogram(combined_scores, bins=10, range=(0, 1))
for i in range(len(hist)):
    print(f"  [{bins[i]:.2f}, {bins[i+1]:.2f}): {hist[i]}")

# Threshold crossing analysis
print(f"\nAgents above upper threshold ({upper_thresh}): {(combined_scores >= upper_thresh).sum()}")
print(f"Agents below lower threshold ({lower_thresh}): {(combined_scores <= lower_thresh).sum()}")
print(f"Agents in ambiguous zone: {((combined_scores > lower_thresh) & (combined_scores < upper_thresh)).sum()}")

# Now run full simulation and track trajectory
print("\n" + "=" * 80)
print("4. FULL SIMULATION RUN (24 steps)")
print("=" * 80)

model.new_adoptions = 0
model.new_adoptions_last_step = 0

adoption_trajectory = []
expenditure_trajectory = []
new_adoptions_trajectory = []

for step in range(config.simulation.timesteps):
    model.step()
    
    total_adopters = model.total_adopters
    new_adoptions = model.new_adoptions_last_step
    subsidy = model.government.subsidy
    
    adoption_trajectory.append(total_adopters)
    new_adoptions_trajectory.append(new_adoptions)
    expenditure_trajectory.append(new_adoptions * subsidy)
    
    print(f"  t={step+1}: adopters={total_adopters}, new={new_adoptions}, subsidy={subsidy:.0f}, price={model.industry.panel_price:.0f}")

print("\n" + "=" * 80)
print("5. SUMMARY")
print("=" * 80)
print(f"Final adoption: {adoption_trajectory[-1]}")
print(f"Total new adoptions: {sum(new_adoptions_trajectory)}")
print(f"Total expenditure: {sum(expenditure_trajectory):.0f}")
print(f"Budget remaining: {config.government.initial_budget - sum(expenditure_trajectory):.0f}")

print("\nAdoption trajectory:", adoption_trajectory)
print("New adoptions trajectory:", new_adoptions_trajectory)
print("Expenditure trajectory:", expenditure_trajectory)