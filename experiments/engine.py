import os
import json
import itertools
import statistics
from typing import List, Dict, Any
from experiments.schemas import (
    MultiSeedExperimentConfig, 
    ExperimentConfig, 
    AggregatedResult, 
    ExperimentResult,
    AblationConfig
)
from experiments.runners import run_experiment

def generate_sweep_configs(base_name: str, base_type: str, seeds: List[int], sweep_params: Dict[str, List[Any]]) -> List[MultiSeedExperimentConfig]:
    """
    Generate a list of MultiSeedExperimentConfigs based on a grid search of sweep_params.
    """
    if not sweep_params:
        return [MultiSeedExperimentConfig(experiment_name=base_name, model_type=base_type, seeds=seeds)]
        
    keys = list(sweep_params.keys())
    values = list(sweep_params.values())
    combinations = list(itertools.product(*values))
    
    configs = []
    for i, combination in enumerate(combinations):
        param_dict = dict(zip(keys, combination))
        name = f"{base_name}_sweep_{i}"
        configs.append(MultiSeedExperimentConfig(
            experiment_name=name,
            model_type=base_type,
            seeds=seeds,
            parameters=param_dict
        ))
    return configs

def aggregate_results(name: str, model_type: str, results: List[ExperimentResult]) -> AggregatedResult:
    rates = [r.final_adoption_rate for r in results]
    tps = [r.tipping_point for r in results if r.tipping_point is not None]
    calls = [r.total_llm_calls for r in results if r.total_llm_calls is not None]
    hits = [r.total_cache_hits for r in results if r.total_cache_hits is not None]
    
    mean_tp = statistics.mean(tps) if tps else None
    mean_calls = statistics.mean(calls) if calls else 0.0
    
    total_calls = sum(calls)
    total_hits = sum(hits)
    total_evals = total_calls + total_hits
    hit_rate = (total_hits / total_evals) if total_evals > 0 else 0.0
    
    frac_tipping = sum(1 for r in results if r.tipping_point_reached) / len(results)
    
    peak_rates = [r.peak_new_adoption_rate for r in results]
    t25s = [r.time_to_25_percent for r in results if r.time_to_25_percent is not None]
    t50s = [r.time_to_50_percent for r in results if r.time_to_50_percent is not None]
    
    return AggregatedResult(
        experiment_name=name,
        model_type=model_type,
        num_seeds=len(results),
        mean_final_adoption_rate=statistics.mean(rates),
        std_final_adoption_rate=statistics.stdev(rates) if len(rates) > 1 else 0.0,
        min_final_adoption_rate=min(rates),
        max_final_adoption_rate=max(rates),
        mean_tipping_point=mean_tp,
        fraction_tipping_point_reached=frac_tipping,
        mean_peak_new_adoption_rate=statistics.mean(peak_rates),
        mean_time_to_25_percent=statistics.mean(t25s) if t25s else None,
        mean_time_to_50_percent=statistics.mean(t50s) if t50s else None,
        mean_llm_calls=mean_calls,
        mean_cache_hit_rate=hit_rate
    )

def run_multiseed_experiment(multi_config: MultiSeedExperimentConfig, root_dir: str = "outputs/experiments") -> AggregatedResult:
    exp_dir = os.path.join(root_dir, multi_config.experiment_name)
    raw_dir = os.path.join(exp_dir, "raw")
    agg_dir = os.path.join(exp_dir, "aggregated")
    meta_dir = os.path.join(exp_dir, "metadata")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(agg_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)
    
    # Save metadata
    with open(os.path.join(meta_dir, "config.json"), "w") as f:
        json.dump(multi_config.model_dump(), f, indent=2)
        
    raw_results = []
    
    for seed in multi_config.seeds:
        single_config = ExperimentConfig(
            experiment_id=f"{multi_config.experiment_name}_seed_{seed}",
            model_type=multi_config.model_type,
            seed=seed,
            n_agents=multi_config.n_agents,
            timesteps=multi_config.timesteps,
            topology=multi_config.topology
        )
        
        print(f"Running {single_config.experiment_id}...")
        res = run_experiment(single_config, multi_config)
        raw_results.append(res)
        
        with open(os.path.join(raw_dir, f"seed_{seed}.json"), "w") as f:
            json.dump(res.model_dump(), f, indent=2)
            
    agg_res = aggregate_results(multi_config.experiment_name, multi_config.model_type, raw_results)
    
    with open(os.path.join(agg_dir, "aggregated.json"), "w") as f:
        json.dump(agg_res.model_dump(), f, indent=2)
        
    return agg_res
