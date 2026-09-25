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

# Run full simulation but with detailed tracking
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

# Run to t=8
for step in range(8):
    model.step()

print(f"t=8: adopters={model.total_adopters}, price={model.industry.panel_price:.0f}, subsidy={model.government.subsidy:.0f}")

# Check scores at t=8 (before t=9 step)
# Government/Industry step for t=9
model.government.step()
model.industry.step()

print(f"\nAfter gov/industry step (t=9 start): price={model.industry.panel_price:.0f}, subsidy={model.government.subsidy:.0f}")
print(f"Affordability: {model.government.subsidy / max(model.industry.panel_price, 1.0):.4f}")
print(f"Upper threshold: {config.cognitive.upper_threshold}")

# Check which agents would have score >= upper_thresh (0.20)
rule_adopt_candidates = []
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
    
    if score >= config.cognitive.upper_threshold:
        rule_adopt_candidates.append((agent, p_base, sir_score, affordability, score))

print(f"\nAgents with score >= upper_thresh ({config.cognitive.upper_threshold}): {len(rule_adopt_candidates)}")
for a, pb, ss, aff, sc in rule_adopt_candidates[:10]:
    print(f"  Agent {a.unique_id}: p_base={pb:.6f}, sir_score={ss:.6f}, aff={aff:.6f}, score={sc:.6f}")

# Now run the actual t=9 step
print("\n=== Running actual t=9 step ===")
# Reset model state for step
model.new_adoptions_last_step = model.new_adoptions
model.new_adoptions = 0
model.step_rule_decisions = 0
model.step_llm_decisions = 0

# Government and Industry already stepped above
# Now consumer step
for agent in consumers:
    if isinstance(agent, ConsumerAgent):
        agent.step()

print(f"After consumer step: new_adoptions={model.new_adoptions}, rule_decisions={model.step_rule_decisions}, llm_decisions={model.step_llm_decisions}")

# Check decision paths of new adopters
new_adopters = [a for a in consumers if a.is_adopter and a.time_infected == 0]
print(f"New adopters at t=9: {len(new_adopters)}")
for a in new_adopters:
    print(f"  Agent {a.unique_id}: decision_path={a.decision_path}, p_base={model.baseline_provider.predict(a):.6f}")

# Now check t=10
model.government.step()
model.industry.step()
print(f"\nBefore t=10 consumer step: price={model.industry.panel_price:.0f}, subsidy={model.government.subsidy:.0f}")
print(f"Infected agents: {sum(1 for a in consumers if a.sir_state == 1)}")

# Check scores for t=10
rule_adopt_candidates_10 = []
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
    
    if score >= config.cognitive.upper_threshold:
        rule_adopt_candidates_10.append((agent, p_base, sir_score, affordability, score, infected_neighbors))

print(f"\nAgents with score >= upper_thresh at t=10: {len(rule_adopt_candidates_10)}")
for a, pb, ss, aff, sc, inf in sorted(rule_adopt_candidates_10, key=lambda x: -x[4])[:15]:
    print(f"  Agent {a.unique_id}: p_base={pb:.6f}, inf_neighbors={inf}, sir_score={ss:.6f}, aff={aff:.6f}, score={sc:.6f}")