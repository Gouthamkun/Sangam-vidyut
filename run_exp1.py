import os
import json
from experiments.engine import generate_sweep_configs, run_multiseed_experiment

def run_experiment_1():
    print("=== EXPERIMENT 1: TOPOLOGICAL DIFFUSION ===")
    
    # Common Parameters
    n_agents = 500
    timesteps = 24
    seeds = list(range(42, 42 + 15)) # 15 seeds
    
    sweeps = {
        "beta": [0.05, 0.15, 0.30],
        "topology": ["watts_strogatz", "barabasi_albert"]
    }
    
    print("\nSTEP 1: Validating config generation...")
    configs = generate_sweep_configs("exp1_topological_diffusion", "SIR_ONLY", seeds, sweeps)
    print(f"Generated {len(configs)} configurations with {len(seeds)} seeds each.")
    assert len(configs) == 6
    
    print("\nSTEP 2: Running ONE representative configuration (beta=0.15, WS, seed=42)...")
    rep_config = next(c for c in configs if c.parameters["beta"] == 0.15 and c.parameters["topology"] == "watts_strogatz")
    # Backup seeds and run just one
    original_seeds = rep_config.seeds
    rep_config.seeds = [42]
    rep_config.n_agents = n_agents
    rep_config.timesteps = timesteps
    
    agg = run_multiseed_experiment(rep_config)
    print("Representative Run Completed successfully!")
    print(f"Final Adoption Rate: {agg.mean_final_adoption_rate}")
    print(f"Peak Adoption Rate: {agg.mean_peak_new_adoption_rate}")
    
    # Restore seeds
    rep_config.seeds = original_seeds
    
    print("\nSTEP 3 & 4: Executing full 90-run matrix and aggregating results...")
    
    results = []
    for config in configs:
        config.n_agents = n_agents
        config.timesteps = timesteps
        print(f"\nExecuting {config.experiment_name} (beta={config.parameters['beta']}, topology={config.parameters['topology']})")
        agg_res = run_multiseed_experiment(config)
        results.append(agg_res)
        
    print("\n=== EXPERIMENT 1 EXECUTION COMPLETE ===")
    print("Writing Summary Table...")
    
    with open("outputs/experiments/exp1_topological_diffusion/summary.json", "w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)
        
if __name__ == "__main__":
    run_experiment_1()
