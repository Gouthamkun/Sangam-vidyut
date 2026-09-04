import pytest
import pandas as pd
from src.config.schema import ExperimentConfig
from scripts.validation.run_empirical_abm_validation import setup_synthetic_model, calculate_distribution

def test_empirical_abm_validation_seeding():
    config = ExperimentConfig()
    config.simulation.baseline_provider = "empirical"
    config.simulation.timesteps = 1
    
    model = setup_synthetic_model(config)
    
    # 500 consumer agents + 4 singletons = 504
    assert len(model.agents) == 504
    
    # 5 initial adopters seeded
    adopters = sum(1 for a in model.agents if getattr(a, 'is_adopter', False))
    assert adopters == 5
    
    # 1 timestep
    model.step()
    
    # Ensure they remain 5 (unless bounds cross, which they shouldn't in this baseline config)
    adopters_after = sum(1 for a in model.agents if getattr(a, 'is_adopter', False))
    assert adopters_after == 5

def test_distribution_bounds():
    config = ExperimentConfig()
    config.simulation.baseline_provider = "empirical"
    model = setup_synthetic_model(config)
    
    from src.simulation.agents.consumer import ConsumerAgent
    
    p_bases = []
    for a in model.agents:
        if isinstance(a, ConsumerAgent):
            p = model.baseline_provider.predict(a)
            assert 0.0 <= p <= 1.0
            p_bases.append(p)
        
    dist = calculate_distribution(p_bases)
    assert dist["std"] > 0
    assert dist["mean"] < 0.15 # Bounded rationally low prior to subsidies/network effects
