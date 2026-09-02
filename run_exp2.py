import os
import json
from experiments.schemas import AblationConfig
from experiments.engine import generate_sweep_configs, run_multiseed_experiment

def run_experiment_2():
    print("=== EXPERIMENT 2: ECONOMIC NONLINEARITY ===")
    
    # Common Parameters
    n_agents = 500
    timesteps = 24
    seeds = list(range(42, 42 + 10)) # 10 seeds
    
    sweeps = {
        "subsidy": [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    }
    
    print("\nSTEP 1: Validating config generation...")
    configs = generate_sweep_configs("exp2_economic_nonlinearity", "DETERMINISTIC_ABM", seeds, sweeps)
    print(f"Generated {len(configs)} configurations with {len(seeds)} seeds each.")
    assert len(configs) == 10
    
    # Apply standard constraints to all configs
    for c in configs:
        c.topology = "watts_strogatz"
        c.n_agents = n_agents
        c.timesteps = timesteps
        c.ablation = AblationConfig(disable_llm=True, disable_dynamic_subsidy=True)
    
    print("\nSTEP 2: Running ONE representative configuration (subsidy=3000, seed=42)...")
    rep_config = next(c for c in configs if c.parameters["subsidy"] == 3000)
    original_seeds = rep_config.seeds
    rep_config.seeds = [42]
    
    agg = run_multiseed_experiment(rep_config)
    print("Representative Run Completed successfully!")
    print(f"Final Adoption Rate: {agg.mean_final_adoption_rate}")
    print(f"Peak Adoption Rate: {agg.mean_peak_new_adoption_rate}")
    
    # Restore seeds
    rep_config.seeds = original_seeds
    
    print("\nSTEP 3 & 4: Executing full 100-run matrix and aggregating results...")
    
    import concurrent.futures
    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(run_multiseed_experiment, config): config for config in configs}
        for future in concurrent.futures.as_completed(futures):
            config = futures[future]
            print(f"\nCompleted {config.experiment_name}")
            results.append(future.result())
            
    # Sort results to maintain order
    results.sort(key=lambda x: x.experiment_name)
        
    print("\n=== EXPERIMENT 2 EXECUTION COMPLETE ===")
    print("Writing Summary Table...")
    
    os.makedirs("outputs/experiments/exp2_economic_nonlinearity", exist_ok=True)
    with open("outputs/experiments/exp2_economic_nonlinearity/summary.json", "w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)
        
if __name__ == "__main__":
    run_experiment_2()
