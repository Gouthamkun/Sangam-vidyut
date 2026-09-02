import os
import json
import concurrent.futures
from experiments.schemas import AblationConfig, MultiSeedExperimentConfig
from experiments.engine import run_multiseed_experiment

def run_experiment_3a():
    print("=== EXPERIMENT 3A: CONTROLLED COGNITIVE ABLATION ===")
    
    n_agents = 100
    timesteps = 12
    seeds = [42, 100, 200, 300, 400]
    
    configs = []
    
    # 1. Deterministic ABM
    configs.append(MultiSeedExperimentConfig(
        experiment_name="exp3a_deterministic",
        model_type="DETERMINISTIC_ABM",
        seeds=seeds,
        n_agents=n_agents,
        timesteps=timesteps,
        ablation=AblationConfig(disable_llm=True)
    ))
    
    # 2. Cognitive ABM with MockLLM
    configs.append(MultiSeedExperimentConfig(
        experiment_name="exp3a_cognitive_mock",
        model_type="FULL_COGNITIVE_ABM",
        seeds=seeds,
        n_agents=n_agents,
        timesteps=timesteps,
        ablation=AblationConfig(force_mock_llm=True)
    ))
    
    print("\nSTEP 1 & 2: Running smoke test for deterministic...")
    smoke_det = configs[0].model_copy(deep=True)
    smoke_det.seeds = [42]
    agg_det = run_multiseed_experiment(smoke_det)
    print(f"Smoke Deterministic Final Adoption: {agg_det.mean_final_adoption_rate}")
    
    print("\nRunning smoke test for cognitive mock...")
    smoke_cog = configs[1].model_copy(deep=True)
    smoke_cog.seeds = [42]
    agg_cog = run_multiseed_experiment(smoke_cog)
    print(f"Smoke Cognitive Mock Final Adoption: {agg_cog.mean_final_adoption_rate}")
    
    print("\nSTEP 3: Executing full matrix (parallel)...")
    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(run_multiseed_experiment, config): config for config in configs}
        for future in concurrent.futures.as_completed(futures):
            config = futures[future]
            print(f"Completed {config.experiment_name}")
            results.append(future.result())
            
    results.sort(key=lambda x: x.experiment_name)
    
    print("\n=== EXPERIMENT 3A EXECUTION COMPLETE ===")
    os.makedirs("outputs/experiments/exp3a_controlled_cognitive_ablation", exist_ok=True)
    with open("outputs/experiments/exp3a_controlled_cognitive_ablation/summary.json", "w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)

if __name__ == "__main__":
    run_experiment_3a()
