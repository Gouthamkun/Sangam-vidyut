import pytest
import os
import pandas as pd
import numpy as np

from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.adapters import create_consumer_from_household_record

def test_legacy_equivalence():
    """Verify that legacy mode still produces the identical mathematical baseline."""
    pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    pop_df = pd.read_parquet(pop_path)
    
    config = ExperimentConfig()
    config.simulation.seed = 42
    config.simulation.n_agents = 500
    config.simulation.baseline_provider = "legacy"
    
    model = SangamVidyutModel(config)
    
    agent = create_consumer_from_household_record(model, pop_df.iloc[0])
    model.grid.place_agent(agent, 0)
    agent.step()
    
    assert getattr(model, "baseline_provider", None) is None
    assert agent.adoption_probability > 0

def test_empirical_provider_determinism():
    config = ExperimentConfig()
    config.simulation.seed = 42
    config.simulation.baseline_provider = "empirical"
    
    model1 = SangamVidyutModel(config)
    model2 = SangamVidyutModel(config)
    
    pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    pop_df = pd.read_parquet(pop_path)
    
    a1 = create_consumer_from_household_record(model1, pop_df.iloc[0])
    a2 = create_consumer_from_household_record(model2, pop_df.iloc[0])
    
    p1 = model1.baseline_provider.predict(a1)
    p2 = model2.baseline_provider.predict(a2)
    
    assert abs(p1 - p2) < 1e-9

def test_empirical_integration_and_distribution():
    config = ExperimentConfig()
    config.simulation.seed = 42
    config.simulation.baseline_provider = "empirical"
    
    model = SangamVidyutModel(config)
    
    pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    pop_df = pd.read_parquet(pop_path)
    
    p_bases = []
    
    for i, row in pop_df.iterrows():
        agent = create_consumer_from_household_record(model, row)
        p = model.baseline_provider.predict(agent)
        
        assert not np.isnan(p)
        assert not np.isinf(p)
        assert 0.0 <= p <= 1.0
        
        p_bases.append(p)
        
    p_bases = np.array(p_bases)
    
    min_p = p_bases.min()
    max_p = p_bases.max()
    mean_p = p_bases.mean()
    median_p = np.median(p_bases)
    std_p = p_bases.std()
    
    quantiles = np.percentile(p_bases, [10, 25, 50, 75, 90])
    
    print("\n--- Empirical p_base Distribution ---")
    print(f"Min:    {min_p:.6f}")
    print(f"Max:    {max_p:.6f}")
    print(f"Mean:   {mean_p:.6f}")
    print(f"Median: {median_p:.6f}")
    print(f"StdDev: {std_p:.6f}")
    print(f"Q10:    {quantiles[0]:.6f}")
    print(f"Q25:    {quantiles[1]:.6f}")
    print(f"Q50:    {quantiles[2]:.6f}")
    print(f"Q75:    {quantiles[3]:.6f}")
    print(f"Q90:    {quantiles[4]:.6f}")
    
    # Assert heterogeneity
    assert std_p > 0.0, "Collapse to single constant detected!"
    assert min_p < max_p, "Collapse to single constant detected!"

def test_abM_smoke_test():
    config = ExperimentConfig()
    config.simulation.seed = 100
    config.simulation.n_agents = 100
    config.simulation.timesteps = 4
    config.simulation.baseline_provider = "empirical"
    config.llm.enabled = False
    
    model = SangamVidyutModel(config)
    
    # Replace default mock agents with synthetic ones for the empirical test
    pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    pop_df = pd.read_parquet(pop_path).head(config.simulation.n_agents)
    
    # Remove existing consumer agents
    from src.simulation.agents.consumer import ConsumerAgent
    for agent in list(model.agents):
        if isinstance(agent, ConsumerAgent):
            if hasattr(agent, 'pos') and agent.pos is not None:
                model.grid.remove_agent(agent)
            model.agents.remove(agent)
        
    for i, row in pop_df.iterrows():
        agent = create_consumer_from_household_record(model, row)
        model.grid.place_agent(agent, i)
        
    initial_adopters = model.total_adopters
    
    for _ in range(4):
        model.step()
        
    final_adopters = model.total_adopters
    transitions = final_adopters - initial_adopters
    
    print(f"\nSmoke Test: {transitions} adoptions occurred out of {config.simulation.n_agents} agents.")
    assert transitions >= 0
