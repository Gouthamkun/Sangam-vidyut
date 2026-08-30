import pandas as pd
from typing import List, Dict
from src.models.diffusion.sir import PureSIRModel
from src.simulation.network.generators import generate_network

class BasicMathematicalSimulation:
    """
    Runs a basic adoption simulation using only mathematical models (no Mesa, no LLMs).
    """
    def __init__(self, config, seed: int = None):
        self.config = config
        self.seed = seed
        self.history: List[Dict[str, int]] = []
        
        # Setup Network
        self.graph = generate_network(
            n=config.simulation.n_agents, 
            config=config.network, 
            seed=seed
        )
            
        # Setup SIR
        self.sir_model = PureSIRModel(
            graph=self.graph,
            beta=config.sir.beta,
            recovery_quarters=config.sir.recovery_duration_quarters
        )
        
    def seed_initial_adopters(self, n_adopters: int = 5):
        import numpy as np
        if self.seed is not None:
            np.random.seed(self.seed)
        nodes = list(self.graph.nodes())
        initial_nodes = np.random.choice(nodes, size=n_adopters, replace=False)
        self.sir_model.seed_infection(initial_nodes)
        
    def run(self) -> pd.DataFrame:
        """Run the simulation for the configured number of timesteps."""
        self.history = []
        # Record initial state
        self.history.append(self.sir_model.get_counts())
        
        for _ in range(self.config.simulation.timesteps):
            self.sir_model.step()
            self.history.append(self.sir_model.get_counts())
            
        from src.analysis.metrics import calculate_adoption_curve
        return calculate_adoption_curve(self.history)
