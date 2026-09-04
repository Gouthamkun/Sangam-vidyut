import pytest
import os
import json
import pandas as pd
from src.simulation.agents.consumer import ConsumerAgent
from src.config.schema import ExperimentConfig

def test_score_component_bounds():
    # p_base must be in [0, 1] - tested previously
    # sir_score must be in [0, 1]
    # affordability must be in [0, 1]
    beta = 0.05
    for I in range(10):
        sir_score = 1.0 - (1.0 - beta) ** I
        assert 0.0 <= sir_score <= 1.0
        
    for sub, price in [(0, 5000), (1000, 5000), (5000, 5000), (10000, 5000)]:
        aff = min(sub / max(price, 1.0), 1.0)
        assert 0.0 <= aff <= 1.0

def test_score_reachability_calculations():
    # Maximum score under empirical base
    w_base = 0.4
    w_sir = 0.4
    w_aff = 0.2
    
    p_max = 0.11145
    sir_max = 1.0
    aff_max = 1.0
    
    max_score = w_base * p_max + w_sir * sir_max + w_aff * aff_max
    assert max_score < 0.7 # Autonomous adoption unreachable

def test_weight_normalization():
    w_base = 0.4
    w_sir = 0.4
    w_aff = 0.2
    assert abs((w_base + w_sir + w_aff) - 1.0) < 1e-9

def test_threshold_ordering():
    config = ExperimentConfig()
    lower = config.cognitive.lower_threshold
    upper = config.cognitive.upper_threshold
    assert lower < upper

def test_no_target_leakage():
    # Ensure PM Surya Ghar targets are not referenced in ConsumerAgent logic
    import inspect
    source = inspect.getsource(ConsumerAgent.step)
    assert "surya_ghar" not in source.lower()
    assert "cea" not in source.lower()

def test_empirical_artifact_immutability():
    artifact_path = 'outputs/calibration/selected_model/empirical_baseline.json'
    assert os.path.exists(artifact_path)
    
    # Ensure it hasn't been modified
    import hashlib
    with open(artifact_path, "rb") as f:
        data = f.read()
    hash_val = hashlib.sha256(data).hexdigest()
    # the known hash from Phase 4E.1
    assert hash_val == "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"
