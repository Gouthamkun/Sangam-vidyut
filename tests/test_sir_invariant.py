import pytest
import networkx as nx
from src.models.diffusion.sir import PureSIRModel

def test_population_conservation_invariant():
    """
    S + I + R = N must hold at every timestep.
    Test across multiple timesteps and configurations.
    """
    n_nodes = 50
    graph = nx.erdos_renyi_graph(n_nodes, 0.2, seed=42)
    
    # Test case 1: High infection rate
    sir = PureSIRModel(graph, beta=0.8, recovery_quarters=2)
    sir.seed_infection([0, 1, 2])
    
    for _ in range(10):
        counts = sir.get_counts()
        assert counts["S"] + counts["I"] + counts["R"] == n_nodes
        sir.step()
        
    # Test case 2: Low infection rate, long recovery
    sir2 = PureSIRModel(graph, beta=0.01, recovery_quarters=5)
    sir2.seed_infection([5, 6, 7])
    
    for _ in range(20):
        counts = sir2.get_counts()
        assert counts["S"] + counts["I"] + counts["R"] == n_nodes
        sir2.step()
        
    # Test case 3: Edge case - 0 initial infections
    sir3 = PureSIRModel(graph, beta=0.5, recovery_quarters=2)
    for _ in range(5):
        counts = sir3.get_counts()
        assert counts["S"] + counts["I"] + counts["R"] == n_nodes
        sir3.step()
