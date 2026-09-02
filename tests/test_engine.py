import pytest
import os
import shutil
from experiments.schemas import MultiSeedExperimentConfig, AblationConfig
from experiments.engine import generate_sweep_configs, run_multiseed_experiment

@pytest.fixture
def cleanup_outputs():
    yield
    if os.path.exists("outputs/experiments/test_multiseed"):
        shutil.rmtree("outputs/experiments/test_multiseed")
    if os.path.exists("outputs/experiments/test_sweep_0"):
        shutil.rmtree("outputs/experiments/test_sweep_0")
    if os.path.exists("outputs/experiments/test_sweep_1"):
        shutil.rmtree("outputs/experiments/test_sweep_1")

def test_generate_sweep_configs():
    sweeps = {
        "beta": [0.1, 0.2],
        "topology": ["watts_strogatz", "barabasi_albert"]
    }
    configs = generate_sweep_configs("test_sweep", "DETERMINISTIC_ABM", [42], sweeps)
    
    assert len(configs) == 4
    assert configs[0].parameters["beta"] == 0.1
    assert configs[0].parameters["topology"] == "watts_strogatz"
    assert configs[3].parameters["beta"] == 0.2
    assert configs[3].parameters["topology"] == "barabasi_albert"

def test_multiseed_aggregation(cleanup_outputs):
    multi_config = MultiSeedExperimentConfig(
        experiment_name="test_multiseed",
        model_type="DETERMINISTIC_ABM",
        seeds=[42, 43],
        n_agents=100,
        timesteps=4
    )
    
    agg_res = run_multiseed_experiment(multi_config)
    
    assert agg_res.num_seeds == 2
    assert agg_res.mean_final_adoption_rate >= 0.0
    
    # Check directory structure
    assert os.path.exists("outputs/experiments/test_multiseed/raw/seed_42.json")
    assert os.path.exists("outputs/experiments/test_multiseed/raw/seed_43.json")
    assert os.path.exists("outputs/experiments/test_multiseed/aggregated/aggregated.json")
    assert os.path.exists("outputs/experiments/test_multiseed/metadata/config.json")

def test_ablation_logic(cleanup_outputs):
    # Disable LLM entirely through ablation, even though we ask for FULL_COGNITIVE_ABM
    multi_config = MultiSeedExperimentConfig(
        experiment_name="test_multiseed",
        model_type="FULL_COGNITIVE_ABM",
        seeds=[42],
        n_agents=100,
        timesteps=2,
        ablation=AblationConfig(disable_llm=True)
    )
    
    agg_res = run_multiseed_experiment(multi_config)
    
    # LLM calls should be exactly 0 due to ablation
    assert agg_res.mean_llm_calls == 0.0

def test_topology_comparison(cleanup_outputs):
    multi_config_ws = MultiSeedExperimentConfig(
        experiment_name="test_ws",
        model_type="SIR_ONLY",
        seeds=[42],
        n_agents=100,
        timesteps=2,
        topology="watts_strogatz"
    )
    
    multi_config_ba = MultiSeedExperimentConfig(
        experiment_name="test_ba",
        model_type="SIR_ONLY",
        seeds=[42],
        n_agents=100,
        timesteps=2,
        topology="barabasi_albert"
    )
    
    res_ws = run_multiseed_experiment(multi_config_ws)
    res_ba = run_multiseed_experiment(multi_config_ba)
    
    # Just asserting they run and aggregate without error
    assert res_ws.num_seeds == 1
    assert res_ba.num_seeds == 1
    
    if os.path.exists("outputs/experiments/test_ws"):
        shutil.rmtree("outputs/experiments/test_ws")
    if os.path.exists("outputs/experiments/test_ba"):
        shutil.rmtree("outputs/experiments/test_ba")
