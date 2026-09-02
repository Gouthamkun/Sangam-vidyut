import os
from experiments.schemas import ExperimentConfig
from experiments.batch import run_batch_experiments

def run_smoke_experiments():
    configs = [
        ExperimentConfig(
            experiment_id="smoke_static",
            model_type="STATIC_BASELINE",
            seed=42,
            n_agents=100,
            timesteps=4
        ),
        ExperimentConfig(
            experiment_id="smoke_sir",
            model_type="SIR_ONLY",
            seed=42,
            n_agents=100,
            timesteps=4
        ),
        ExperimentConfig(
            experiment_id="smoke_abm_det",
            model_type="DETERMINISTIC_ABM",
            seed=42,
            n_agents=100,
            timesteps=4
        ),
        ExperimentConfig(
            experiment_id="smoke_abm_cog",
            model_type="FULL_COGNITIVE_ABM",
            seed=42,
            n_agents=100,
            timesteps=4
        )
    ]
    
    results = run_batch_experiments(configs, output_dir="outputs")
    
    print("\n=== Smoke Experiment Results ===")
    for r in results:
        print(f"[{r.model_type}] Adoptions: {r.final_adoption} | LLM Calls: {r.total_llm_calls} | Cache Hits: {r.total_cache_hits}")

if __name__ == "__main__":
    run_smoke_experiments()
