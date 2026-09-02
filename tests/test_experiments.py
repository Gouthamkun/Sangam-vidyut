import pytest
import os
from experiments.schemas import ExperimentConfig
from experiments.runners import run_experiment

@pytest.fixture
def base_exp_config():
    return ExperimentConfig(
        experiment_id="test_exp",
        model_type="STATIC_BASELINE",
        seed=42,
        n_agents=100,
        timesteps=6
    )

def test_static_baseline(base_exp_config):
    res = run_experiment(base_exp_config)
    assert res.population == 100
    assert len(res.cumulative_adoptions) == 6
    assert res.total_llm_calls == 0

def test_sir_only(base_exp_config):
    base_exp_config.model_type = "SIR_ONLY"
    res = run_experiment(base_exp_config)
    assert len(res.cumulative_adoptions) == 6
    assert res.cumulative_adoptions[-1] >= 5 # Initial seed is 5

def test_deterministic_abm(base_exp_config):
    base_exp_config.model_type = "DETERMINISTIC_ABM"
    res = run_experiment(base_exp_config)
    assert res.total_llm_calls == 0
    assert res.cumulative_co2_displaced is not None
    assert res.final_adoption >= 5

def test_full_cognitive_abm(base_exp_config):
    base_exp_config.model_type = "FULL_COGNITIVE_ABM"
    res = run_experiment(base_exp_config)
    assert res.total_llm_calls >= 0
    assert res.cumulative_co2_displaced is not None

def test_reproducibility(base_exp_config):
    base_exp_config.model_type = "FULL_COGNITIVE_ABM"
    
    # Run once
    res1 = run_experiment(base_exp_config)
    
    # Run twice
    res2 = run_experiment(base_exp_config)
    
    assert res1.final_adoption == res2.final_adoption
    assert res1.cumulative_adoptions == res2.cumulative_adoptions
    assert res1.total_llm_calls == res2.total_llm_calls

def test_different_seeds_vary(base_exp_config):
    base_exp_config.model_type = "SIR_ONLY"
    
    base_exp_config.seed = 42
    res1 = run_experiment(base_exp_config)
    
    base_exp_config.seed = 99
    res2 = run_experiment(base_exp_config)
    
    # Due to random initial placement and diffusion, final adoptions often vary.
    # We just assert that at least *some* internal metric or the exact curve differs.
    assert res1.cumulative_adoptions != res2.cumulative_adoptions

def test_population_conservation(base_exp_config):
    base_exp_config.model_type = "DETERMINISTIC_ABM"
    res = run_experiment(base_exp_config)
    assert res.final_adoption <= res.population
    for step_val in res.cumulative_adoptions:
        assert step_val <= res.population
        
def test_tipping_point_consistency(base_exp_config):
    base_exp_config.model_type = "SIR_ONLY"
    res = run_experiment(base_exp_config)
    if res.tipping_point is not None:
        assert 0 <= res.tipping_point <= res.timesteps
