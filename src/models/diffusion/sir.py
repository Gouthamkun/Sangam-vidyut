import networkx as nx
import numpy as np
from typing import Dict

class PureSIRModel:
    """
    Pure SIR mathematical diffusion model on a NetworkX graph.
    S = 0 (Susceptible)
    I = 1 (Infected - active adopter)
    R = 2 (Recovered - older adopter, reduced influence)
    """
    def __init__(self, graph: nx.Graph, beta: float, recovery_quarters: int):
        self.graph = graph
        self.beta = beta
        self.recovery_quarters = recovery_quarters
        
        # Initialize node states (0: Susceptible, 1: Infected, 2: Recovered)
        self.states = {node: 0 for node in self.graph.nodes()}
        # Track how long a node has been infected
        self.time_infected = {node: 0 for node in self.graph.nodes()}

    def seed_infection(self, nodes: list):
        """Seed the network with initial adopters (Infected)."""
        for node in nodes:
            if node in self.states:
                self.states[node] = 1
                self.time_infected[node] = 1

    def step(self):
        """Perform one discrete timestep (quarter) of diffusion."""
        new_states = self.states.copy()
        
        for node in self.graph.nodes():
            if self.states[node] == 1:
                # 1. Attempt to infect susceptible neighbors
                for neighbor in self.graph.neighbors(node):
                    if self.states[neighbor] == 0:
                        if np.random.rand() < self.beta:
                            new_states[neighbor] = 1
                            self.time_infected[neighbor] = 0 # Will be 1 next step
                
                # 2. Check for recovery
                if self.time_infected[node] >= self.recovery_quarters:
                    new_states[node] = 2
            
            # Increment time infected for current infections
            if new_states[node] == 1:
                self.time_infected[node] += 1
                
        self.states = new_states
        
    def get_counts(self) -> Dict[str, int]:
        """Return the count of S, I, and R nodes."""
        counts = {0: 0, 1: 0, 2: 0}
        for state in self.states.values():
            counts[state] += 1
        return {"S": counts[0], "I": counts[1], "R": counts[2]}
