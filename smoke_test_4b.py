from experiments.engine import generate_sweep_configs, run_multiseed_experiment

def run_phase_4b_smoke():
    # Sweep over Network Topology with FULL_COGNITIVE_ABM and Mock LLM
    sweeps = {
        "topology": ["watts_strogatz", "barabasi_albert"]
    }
    
    print("Generating sweep configs...")
    configs = generate_sweep_configs("smoke_topology_comp", "FULL_COGNITIVE_ABM", [42, 100], sweeps)
    
    for c in configs:
        # Force LLM mock just to ensure it runs instantly without hitting network
        c.parameters["lower_threshold"] = 0.0
        c.parameters["upper_threshold"] = 1.0
        
    print(f"Generated {len(configs)} configurations across 2 seeds each.")
    
    for config in configs:
        print(f"\nExecuting {config.experiment_name}...")
        config.n_agents = 100
        config.timesteps = 4
        
        agg = run_multiseed_experiment(config)
        
        print(f"Results for {agg.experiment_name}:")
        print(f"  Seeds: {agg.num_seeds}")
        print(f"  Mean Final Adoption Rate: {agg.mean_final_adoption_rate:.4f} (±{agg.std_final_adoption_rate:.4f})")
        print(f"  Mean Tipping Point: {agg.mean_tipping_point}")
        print(f"  Mean Cache Hit Rate: {agg.mean_cache_hit_rate:.2f}")

if __name__ == "__main__":
    run_phase_4b_smoke()
