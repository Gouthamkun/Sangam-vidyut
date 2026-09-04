import os
import numpy as np
import pandas as pd
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.consumer import ConsumerAgent
from src.config.schema import ExperimentConfig
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

def run_diagnostic():
    config = ExperimentConfig()
    config.simulation.n_agents = 500
    config.simulation.baseline_provider = "empirical"
    config.network.topology = "watts_strogatz"
    config.sir.beta = 0.30
    config.sir.recovery_duration_quarters = 2
    
    model = setup_synthetic_model(config)
    
    adopters = [a for a in model.agents if isinstance(a, ConsumerAgent) and getattr(a, 'is_adopter', False)]
    infected = [a for a in model.agents if isinstance(a, ConsumerAgent) and getattr(a, 'sir_state', 0) == 1]
    
    print(f"Total Adopters: {len(adopters)}")
    print(f"Total Infected: {len(infected)}")

    # Check cognitive routing
    p_bases = []
    sir_scores = []
    affordability = []
    scores = []
    
    for a in model.agents:
        if isinstance(a, ConsumerAgent):
            p = model.baseline_provider.predict(a)
            # just mock sir_score
            sir = 1.0 - (1.0 - config.sir.beta) ** 1  # Assume 1 infected neighbor
            aff = min(config.government.base_subsidy / 1.0, 1.0)
            score = 0.4 * p + 0.4 * sir + 0.2 * aff
            
            p_bases.append(p)
            sir_scores.append(sir)
            affordability.append(aff)
            scores.append(score)
            
    scores = np.array(scores)
    print(f"Scores <= 0.05: {(scores <= 0.05).sum()}")
    print(f"Scores 0.05 - 0.20: {((scores > 0.05) & (scores < 0.20)).sum()}")
    print(f"Scores >= 0.20: {(scores >= 0.20).sum()}")
    print(f"Sample scores: {scores[:5]}")

if __name__ == "__main__":
    run_diagnostic()
