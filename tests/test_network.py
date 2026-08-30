import pytest
from src.simulation.network.generators import generate_watts_strogatz, generate_barabasi_albert

def test_watts_strogatz():
    G = generate_watts_strogatz(100, 4, 0.1, seed=42)
    assert len(G.nodes()) == 100
    assert len(G.edges()) > 0

def test_barabasi_albert():
    G = generate_barabasi_albert(100, 2, seed=42)
    assert len(G.nodes()) == 100
    assert len(G.edges()) > 0
