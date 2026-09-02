import os
import json
from typing import List
from experiments.schemas import ExperimentConfig, ExperimentResult
from experiments.runners import run_experiment

def run_batch_experiments(configs: List[ExperimentConfig], output_dir: str = "outputs") -> List[ExperimentResult]:
    """
    Run a batch of experiments sequentially and save the results.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for config in configs:
        print(f"Running {config.experiment_id} (Seed {config.seed})...")
        res = run_experiment(config)
        results.append(res)
        
        # Save individually to outputs
        out_path = os.path.join(output_dir, f"{config.experiment_id}.json")
        with open(out_path, 'w') as f:
            json.dump(res.model_dump(), f, indent=2)
            
    return results
