import pytest
import pandas as pd
import numpy as np
from src.models.statistical.baseline import AdoptionLogisticRegression
from src.models.diffusion.sir import PureSIRModel
import networkx as nx

def test_logistic_regression():
    model = AdoptionLogisticRegression(random_state=42)
    model.mock_fit(n_features=2)
    assert model.is_fitted
    
    X_test = pd.DataFrame(np.random.rand(5, 2))
    probs = model.predict_proba(X_test)
    assert len(probs) == 5
    assert all(0 <= p <= 1 for p in probs)

def test_sir_model():
    graph = nx.complete_graph(10)
    # beta=1.0 guarantees infection
    sir = PureSIRModel(graph, beta=1.0, recovery_quarters=2)
    
    sir.seed_infection([0])
    counts = sir.get_counts()
    assert counts["I"] == 1
    assert counts["S"] == 9
    assert counts["R"] == 0
    
    sir.step()
    # node 0 infects everyone since beta=1.0
    counts = sir.get_counts()
    assert counts["I"] == 10
    assert counts["S"] == 0
    assert counts["R"] == 0
    
    sir.step() # node 0 hits 2 quarters infected (0 was seeded, infected at step 0)
    # Wait, node 0 time_infected:
    # After seed: time=1
    # After step 1: time=2 (so it recovers in step 2)
    counts = sir.get_counts()
    assert counts["R"] == 1
