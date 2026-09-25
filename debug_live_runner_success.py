import time
import sys
import os
sys.path.insert(0, os.path.abspath("."))

# Manually create the "successful" configuration using the campaign approach
from src.config.schema import ExperimentConfig, BehaviorPolicyConfig, CognitiveConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.agents.consumer import ConsumerAgent
import pandas as pd
import numpy as np
import uuid

# Replicate the exact DETERMINISTIC_EMPIRICAL_ABM configuration from phase_4f_1_campaign
# which is what the "earlier isolated empirical live diagnostic" likely used
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

print(f"Thresholds: lower={config.cognitive.lower_threshold}, upper={config.cognitive.upper_threshold}")
print(f"LLM enabled: {config.llm.enabled}")

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

# Update the already collected step 0 data
if "adoption_count" in model.datacollector.model_vars:
    model.datacollector.model_vars["adoption_count"][0] = initial_adoption
    model.datacollector.model_vars["infected_count"][0] = initial_adoption
    model.datacollector.model_vars["susceptible_count"][0] = config.simulation.n_agents - initial_adoption
    model.datacollector.model_vars["adoption_rate"][0] = initial_adoption / config.simulation.n_agents

print(f"\nInitial adopters after seeding: {sum(1 for a in model.agents if getattr(a, 'is_adopter', False))}")

start = time.time()

horizon = config.simulation.timesteps
for step in range(horizon):
    model.step()

df = model.datacollector.get_model_vars_dataframe()
df["timestep"] = range(len(df))
df["new_adoptions"] = df["new_adoptions"].shift(-1).fillna(0)
df["step_expenditure"] = df["new_adoptions"] * df["subsidy"]
df["cumulative_expenditure"] = df["step_expenditure"].cumsum()
df["budget_remaining"] = config.government.initial_budget - df["cumulative_expenditure"]

elapsed = time.time() - start

print(f"\nRuntime: {elapsed:.1f} seconds")
print(f"Final adoption: {df['adoption_count'].iloc[-1]}")

print(f"\nTrajectory:")
for _, row in df.iterrows():
    print(f"  t={int(row['timestep'])}: adopters={int(row['adoption_count'])}, new={int(row['new_adoptions'])}, subsidy={row['subsidy']:.0f}, price={row['panel_price']:.0f}")

print(f"\nTotal expenditure: {df['cumulative_expenditure'].iloc[-1]:.0f}")
print(f"Budget remaining: {df['budget_remaining'].iloc[-1]:.0f}")
print(f"LLM calls: {getattr(model.llm_interface.provider, 'call_count', 0)}")
print(f"Rule decisions: {getattr(model, 'step_rule_decisions', 0)}")
print(f"LLM decisions: {getattr(model, 'step_llm_decisions', 0)}")