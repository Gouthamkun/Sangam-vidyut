import pytest
import os
import hashlib
import numpy as np
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_4_design_study import compute_family_1, compute_family_2, compute_family_3, compute_family_4

def test_mathematical_bounds():
    p_base = 0.11145
    sir = 1.0
    aff = 1.0
    
    assert 0.0 <= compute_family_1(p_base, sir, aff) <= 1.0
    assert 0.0 <= compute_family_2(p_base, sir, aff) <= 1.0
    assert 0.0 <= compute_family_3(p_base, sir, aff) <= 1.0
    assert 0.0 < compute_family_4(p_base, sir, aff) < 1.0

def test_deterministic_transformations():
    # Calling the same parameters must yield same exact score
    assert compute_family_2(0.05, 0.5, 0.5) == compute_family_2(0.05, 0.5, 0.5)
    assert compute_family_4(0.05, 0.5, 0.5) == compute_family_4(0.05, 0.5, 0.5)

def test_score_invariants():
    # Higher p_base must yield higher score, holding sir and aff constant
    score_low = compute_family_1(0.001, 0.5, 0.5)
    score_high = compute_family_1(0.1, 0.5, 0.5)
    assert score_high > score_low

def test_no_target_leakage_in_design():
    # Ensure PM Surya Ghar targets are not referenced in the design script
    import inspect
    import scripts.validation.phase_4e_4_design_study as ds
    source = inspect.getsource(ds)
    assert "surya_ghar" not in source.lower()
    assert "cea" not in source.lower()

def test_empirical_artifact_immutability_p4e4():
    artifact_path = 'outputs/calibration/selected_model/empirical_baseline.json'
    assert os.path.exists(artifact_path)
    
    with open(artifact_path, "rb") as f:
        data = f.read()
    hash_val = hashlib.sha256(data).hexdigest()
    assert hash_val == "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"
