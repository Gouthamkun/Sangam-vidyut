import os
import pandas as pd
import pytest
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.simulation.agents.adapters import create_consumer_from_household_record
from src.simulation.model import SangamVidyutModel

from src.config.schema import ExperimentConfig

def test_hces_consumer_integration():
    # 1. Load synthetic population
    pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    assert os.path.exists(pop_path), "Synthetic population file must exist"
    
    pop_df = pd.read_parquet(pop_path)
    assert len(pop_df) == 500
    
    # 2. Instantiate Base Model
    # Note: SangamVidyutModel automatically creates agents in __init__ 
    # but we will manually create our synthetic agents via the adapter and verify them.
    config = ExperimentConfig()
    config.simulation.seed = 42
    config.simulation.n_agents = 500
    config.network.topology = "watts_strogatz"
    config.llm.provider = "mock"
    
    model = SangamVidyutModel(config)
    
    # 3. Instantiate ConsumerAgents from the synthetic population
    synthetic_agents = []
    for _, row in pop_df.iterrows():
        agent = create_consumer_from_household_record(model, row)
        synthetic_agents.append(agent)
        
    # 4. Verify properties
    assert len(synthetic_agents) == 500
    
    # Unique synthetic agent IDs
    unique_ids = set(a.synthetic_agent_id for a in synthetic_agents)
    assert len(unique_ids) == 500
    
    # State / Sector distributions preserved
    agent_states = [a.state for a in synthetic_agents]
    agent_sectors = [a.sector for a in synthetic_agents]
    assert agent_states == pop_df['state'].tolist()
    assert agent_sectors == pop_df['sector'].tolist()
    
    # Valid attributes check
    for a in synthetic_agents:
        assert a.household_size > 0
        assert a.derived_mpce >= 0
        assert 1 <= a.mpce_decile <= 10
        assert hasattr(a, 'source_hces_household_key')
        
        # Missing fields check
        assert not hasattr(a, 'system_size_kw')
        # home_owner is physically present as a fallback property with value -1
        assert a.home_owner == -1 
        
    # 5. Reproducibility & Mathematical Decision Preservation Test
    # We will step the very first synthetic agent and verify the calculation
    agent = synthetic_agents[0]
    
    # Place agent in grid so it can find neighbors
    # (Just placing on node 0 for test purposes)
    model.grid.place_agent(agent, 0)
    
    # Trigger a step to compute score
    agent.step()
    
    # Verify the decision equation mathematically
    # features = [[agent.income, agent.home_owner]] => [[derived_mpce, -1]]
    features = pd.DataFrame([[agent.derived_mpce, -1]])
    expected_p_base = model.baseline_model.predict_proba(features)[0]
    
    # Neighbors infected logic (agent on node 0, network varies but sir_state default is 0)
    neighbors = model.grid.get_neighbors(agent.pos, include_center=False)
    infected_neighbors = sum(1 for item in neighbors if getattr(item, 'sir_state', 0) == 1)
    
    expected_sir_score = 1.0 - (1.0 - config.sir.beta) ** infected_neighbors
    
    expected_affordability = min(model.current_subsidy / max(model.current_panel_price, 1.0), 1.0)
    
    expected_score = 0.4 * expected_p_base + 0.4 * expected_sir_score + 0.2 * expected_affordability
    
    assert abs(agent.adoption_probability - expected_score) < 1e-6, "Decision equation has been mathematically altered!"

    print("Integration test passed: agent properties valid and decision equation strictly preserved.")
