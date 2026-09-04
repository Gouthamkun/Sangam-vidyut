import pytest
import os
import hashlib
from src.config.schema import ExperimentConfig
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

def test_threshold_ordering_and_opt_in():
    # Default is legacy
    config = ExperimentConfig()
    assert config.cognitive.policy.name == "legacy_defaults"
    assert config.cognitive.lower_threshold == 0.3
    assert config.cognitive.upper_threshold == 0.7
    
    # Opt-in triggers values
    config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
    config.cognitive.sync_policy_thresholds()
    assert config.cognitive.lower_threshold == 0.05
    assert config.cognitive.upper_threshold == 0.20
    assert config.cognitive.lower_threshold < config.cognitive.upper_threshold

def test_legacy_regression_isolation():
    # Legacy must still exist and reproduce safely
    config = ExperimentConfig()
    config.simulation.baseline_provider = "legacy"
    config.simulation.timesteps = 1
    
    model = setup_synthetic_model(config)
    assert len(model.agents) == 504 # 500 + 4
    
    # 5 adopters seeded
    adopters = sum(1 for a in model.agents if getattr(a, 'is_adopter', False))
    assert adopters == 5
    
    model.step()
    adopters_after = sum(1 for a in model.agents if getattr(a, 'is_adopter', False))
    assert adopters_after == 5

def test_empirical_artifact_immutability_p4e5():
    artifact_path = 'outputs/calibration/selected_model/empirical_baseline.json'
    assert os.path.exists(artifact_path)
    
    with open(artifact_path, "rb") as f:
        data = f.read()
    hash_val = hashlib.sha256(data).hexdigest()
    assert hash_val == "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"

def test_no_target_leakage_p4e5():
    import inspect
    import scripts.validation.phase_4e_5_validation as pv
    source = inspect.getsource(pv)
    assert "surya_ghar" not in source.lower()
    assert "cea" not in source.lower()

def test_sir_conservation():
    config = ExperimentConfig()
    config.simulation.baseline_provider = "empirical"
    config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
    config.simulation.timesteps = 1
    model = setup_synthetic_model(config)
    model.step()
    
    s = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 0)
    i = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 1)
    r = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 2)
    consumers = sum(1 for a in model.agents if isinstance(a, ConsumerAgent))
    assert s + i + r == consumers

def test_probability_bounds():
    config = ExperimentConfig()
    config.simulation.baseline_provider = "empirical"
    model = setup_synthetic_model(config)
    for a in model.agents:
        if isinstance(a, ConsumerAgent):
            p = model.baseline_provider.predict(a)
            assert 0.0 <= p <= 1.0
