import os
import json
import pandas as pd
import numpy as np
import hashlib
from joblib import Parallel, delayed

from src.config.schema import ExperimentConfig
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

OUT_DIR = "outputs/experiments/phase_4f_3"

def ensure_dirs():
    for d in ["manifests", "raw", "aggregated", "plots", "tables", "reports"]:
        os.makedirs(os.path.join(OUT_DIR, d), exist_ok=True)

def atomic_write_json(data, path):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)

def atomic_write_csv(df, path):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)

def setup_model(config):
    model = setup_synthetic_model(config)
    return model

def validate_run(run_id, quarters):
    sum_path = f"{OUT_DIR}/raw/{run_id}_summary.json"
    traj_path = f"{OUT_DIR}/raw/{run_id}_trajectory.csv"
    man_path = f"{OUT_DIR}/manifests/{run_id}_manifest.json"
    
    if not (os.path.exists(sum_path) and os.path.exists(traj_path) and os.path.exists(man_path)):
        return False
        
    try:
        with open(sum_path, "r") as f:
            reopened_sum = json.load(f)
        reopened_traj = pd.read_csv(traj_path)
        with open(man_path, "r") as f:
            manifest = json.load(f)
            
        if "run_id" not in reopened_sum: return False
        if len(reopened_traj) != (quarters + 1): return False
        if manifest.get("status") != "COMPLETED": return False
        return True
    except:
        return False

def run_single_simulation(run_id, model_class, topo, seed, subsidy, dynamic_policy, quarters=24, n_agents=500):
    if validate_run(run_id, quarters):
        return {"run_id": run_id, "status": "COMPLETED", "note": "Already completed"}
        
    try:
        config = ExperimentConfig()
        config.simulation.baseline_provider = "empirical"
        config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
        config.cognitive.sync_policy_thresholds()
        config.simulation.n_agents = n_agents
        config.simulation.timesteps = quarters
        config.simulation.seed = seed
        
        config.network.topology = topo
        config.sir.beta = 0.15
        config.sir.recovery_duration_quarters = 2
        
        config.government.dynamic_subsidy = dynamic_policy
        config.government.base_subsidy = subsidy
        config.government.initial_budget = 1_000_000.0
        
        if model_class == "STATIC_BASELINE":
            config.sir.beta = 0.0
            config.llm.enabled = False
            config.llm.provider = "mock"
        elif model_class == "DETERMINISTIC_EMPIRICAL_ABM":
            config.llm.enabled = False
            config.llm.provider = "mock"
        elif model_class == "HYBRID_COGNITIVE_ABM":
            config.llm.enabled = True
            config.llm.provider = "mock"
            config.llm.cache_enabled = True

        model = setup_model(config)
        
        trajectory = []
        consumers = [a for a in model.agents if isinstance(a, ConsumerAgent)]
        pop = len(consumers)
        
        gov = model.government
        
        exhaustion_quarter = None
        exhaustion_subsidy = None
        exhaustion_adoption = None
        target_reached = False
        saturation_reached = False
        
        for t in range(quarters + 1):
            if t > 0:
                model.step()
            
            s = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 0)
            i = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 1)
            r = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 2)
            adopters = sum(1 for a in consumers if getattr(a, 'is_adopter', False))
            
            adoption_rate = adopters / max(1, pop)
            if adoption_rate >= 0.5:
                target_reached = True
            if adoption_rate >= 0.95:
                saturation_reached = True
                
            if gov.budget <= 0 and exhaustion_quarter is None:
                exhaustion_quarter = t
                exhaustion_subsidy = gov.subsidy
                exhaustion_adoption = adopters
                
            trajectory.append({
                "run_id": run_id,
                "model_class": model_class,
                "quarter": t,
                "susceptible_count": s,
                "infected_count": i,
                "recovered_count": r,
                "adoption_count": adopters,
                "new_adoptions": model.new_adoptions_last_step if t > 0 else adopters,
                "subsidy_level": gov.subsidy,
                "budget_remaining": gov.budget,
                "llm_calls": getattr(model, 'step_llm_decisions', 0)
            })
            
        traj_df = pd.DataFrame(trajectory)
        
        # S+I+R=N check
        sir_sum = traj_df["susceptible_count"] + traj_df["infected_count"] + traj_df["recovered_count"]
        if not (sir_sum == pop).all():
            raise ValueError(f"S+I+R != N invariant violated. Pop: {pop}, Sums: {sir_sum.tolist()}")
            
        config_hash = hashlib.sha256(config.model_dump_json().encode()).hexdigest()
            
        manifest = {
            "run_id": run_id,
            "experiment_id": "phase_4f_3",
            "model_class": model_class,
            "topology": topo,
            "beta": 0.15,
            "seed": seed,
            "subsidy": subsidy,
            "dynamic_policy": dynamic_policy,
            "population_size": pop,
            "horizon": quarters,
            "status": "COMPLETED",
            "provider": config.llm.provider if config.llm.enabled else "N/A",
            "calibration_artifact_sha256": "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241",
            "config_sha256": config_hash
        }
        
        extracted_interface = getattr(model, 'llm_interface', None)
        if extracted_interface and hasattr(extracted_interface, 'provider'):
            extracted_hits = getattr(extracted_interface.provider, 'cache_hits', 0)
            extracted_misses = getattr(extracted_interface.provider, 'cache_misses', 0)
        else:
            extracted_hits = 0
            extracted_misses = 0
            
        summary = {
            "run_id": run_id,
            "model_class": model_class,
            "dynamic_policy": dynamic_policy,
            "final_adoption": int(traj_df.iloc[-1]["adoption_count"]),
            "initial_budget": config.government.initial_budget,
            "total_expenditure": config.government.initial_budget - gov.budget,
            "exhaustion_quarter": exhaustion_quarter,
            "exhaustion_subsidy": exhaustion_subsidy,
            "exhaustion_adoption": exhaustion_adoption,
            "target_reached": target_reached,
            "saturation_reached": saturation_reached,
            "total_llm_calls": int(traj_df["llm_calls"].sum()),
            "total_cache_hits": extracted_hits,
            "total_cache_misses": extracted_misses
        }
        
        sum_path = f"{OUT_DIR}/raw/{run_id}_summary.json"
        traj_path = f"{OUT_DIR}/raw/{run_id}_trajectory.csv"
        atomic_write_csv(traj_df, traj_path)
        atomic_write_json(summary, sum_path)
        
        def hash_file(filepath):
            h = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""): h.update(chunk)
            return h.hexdigest()
            
        manifest["summary_sha256"] = hash_file(sum_path)
        manifest["trajectory_sha256"] = hash_file(traj_path)
        
        man_path = f"{OUT_DIR}/manifests/{run_id}_manifest.json"
        atomic_write_json(manifest, man_path)
        
        return {"run_id": run_id, "status": "COMPLETED"}
        
    except Exception as e:
        print(f"Error in {run_id}: {str(e)}")
        return {"run_id": run_id, "status": "FAILED", "error": str(e)}

def build_experiment_grid():
    seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    subsidies = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0]
    topologies = ["watts_strogatz", "barabasi_albert"]
    modes = [False, True]
    
    tasks = []
    
    # 1. Deterministic Empirical ABM (200 runs)
    for sub in subsidies:
        for mode in modes:
            for topo in topologies:
                for s in seeds:
                    tasks.append({
                        "run_id": f"R3_DET_{sub}_{mode}_{topo}_{s}",
                        "model_class": "DETERMINISTIC_EMPIRICAL_ABM",
                        "topo": topo,
                        "seed": s,
                        "subsidy": sub,
                        "dynamic_policy": mode
                    })
                    
    # 2. Static Baseline (100 runs)
    for sub in subsidies:
        for topo in topologies:
            for s in seeds:
                tasks.append({
                    "run_id": f"R3_STAT_{sub}_False_{topo}_{s}",
                    "model_class": "STATIC_BASELINE",
                    "topo": topo,
                    "seed": s,
                    "subsidy": sub,
                    "dynamic_policy": False
                })
                
    # 3. Hybrid Cognitive ABM (20 runs)
    for topo in topologies:
        for s in seeds:
            tasks.append({
                "run_id": f"R3_COG_3000.0_False_{topo}_{s}",
                "model_class": "HYBRID_COGNITIVE_ABM",
                "topo": topo,
                "seed": s,
                "subsidy": 3000.0,
                "dynamic_policy": False
            })
            
    return tasks

def main():
    ensure_dirs()
    print("=== PHASE 4F.3 EXECUTION CAMPAIGN ===")
    
    tasks = build_experiment_grid()
    print(f"Total tasks generated: {len(tasks)}")
    
    # Check how many are missing
    missing_tasks = []
    for t in tasks:
        if not validate_run(t["run_id"], 24):
            missing_tasks.append(t)
            
    print(f"Tasks remaining to execute: {len(missing_tasks)}")
    if len(missing_tasks) == 0:
        print("Campaign already complete.")
        return
        
    print(f"Executing {len(missing_tasks)} runs...")
    
    # Limit n_jobs to avoid starving MockLLM loops on Windows
    results = Parallel(n_jobs=4, verbose=10)(
        delayed(run_single_simulation)(**t) for t in missing_tasks
    )
    
    success = sum(1 for r in results if r["status"] == "COMPLETED")
    failed = len(results) - success
    print(f"\nExecution Complete! Success: {success}, Failed: {failed}")

if __name__ == "__main__":
    main()
