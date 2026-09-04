import os
import json
import pandas as pd
import numpy as np
import hashlib
import time

from src.config.schema import ExperimentConfig
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

OUT_DIR = "outputs/experiments/phase_4f_1_rerun"

def atomic_write_json(data, path):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)

def atomic_write_csv(df, path):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)

def detect_tipping_point(cumulative_series, population):
    for t in range(1, len(cumulative_series)):
        new_adoptions = cumulative_series[t] - cumulative_series[t-1]
        if (new_adoptions / population) >= 0.05:
            return t
    return None

def setup_model(config, constant_pbase=None):
    model = setup_synthetic_model(config)
    if constant_pbase is not None:
        # Override baseline provider to return a constant
        class ConstantProvider:
            def predict(self, agent):
                return constant_pbase
        model.baseline_provider = ConstantProvider()
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
            
        if "run_id" not in reopened_sum:
            return False
        if len(reopened_traj) != (quarters + 1):
            return False
        if manifest.get("status") != "COMPLETED":
            return False
        return True
    except:
        return False

def run_single_simulation(run_id, model_class, topo, beta, seed, subsidy, p_base_mode, quarters=24, constant_val=None, n_agents=5000):
    try:
        config = ExperimentConfig()
        config.simulation.baseline_provider = "empirical"
        config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
        config.cognitive.sync_policy_thresholds()
        config.simulation.n_agents = n_agents
        config.simulation.timesteps = quarters
        config.simulation.seed = seed
        
        config.network.topology = topo if topo != "NA" else "watts_strogatz"
        config.sir.beta = beta if beta != "NA" else 0.0
        config.sir.recovery_duration_quarters = 2
        
        config.government.dynamic_subsidy = False
        config.government.base_subsidy = subsidy
        
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

        model = setup_model(config, constant_pbase=constant_val)
        
        trajectory = []
        consumers = [a for a in model.agents if isinstance(a, ConsumerAgent)]
        pop = len(consumers)
        
        for t in range(quarters + 1):
            if t > 0:
                model.step()
            
            s = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 0)
            i = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 1)
            r = sum(1 for a in consumers if getattr(a, 'sir_state', -1) == 2)
            adopters = sum(1 for a in consumers if getattr(a, 'is_adopter', False))
            
            p_bases = [model.baseline_provider.predict(a) for a in consumers]
            
            sir_scores = []
            eff_beta = beta if beta != "NA" else 0.0
            for a in consumers:
                if hasattr(model, 'grid') and a.pos is not None:
                    neighbors = model.grid.get_neighbors(a.pos, include_center=False)
                    infected = sum(1 for n in neighbors if getattr(n, 'sir_state', 0) == 1)
                    sir_scores.append(1.0 - (1.0 - eff_beta) ** infected)
                else:
                    sir_scores.append(0.0)
                    
            affordabilities = [min(subsidy / max(model.current_panel_price, 1.0), 1.0) for a in consumers]
            
            trajectory.append({
                "run_id": run_id,
                "model_class": model_class,
                "topology": topo,
                "beta": beta,
                "seed": seed,
                "subsidy": subsidy,
                "p_base_mode": p_base_mode,
                "quarter": t,
                "susceptible_count": s,
                "infected_count": i,
                "recovered_count": r,
                "adoption_count": adopters,
                "adoption_rate": adopters / pop,
                "new_adoptions": model.new_adoptions_last_step if t > 0 else 5,
                "mean_p_base": np.mean(p_bases),
                "median_p_base": np.median(p_bases),
                "p90_p_base": np.percentile(p_bases, 90),
                "mean_sir_score": np.mean(sir_scores),
                "mean_affordability": np.mean(affordabilities),
                "llm_calls": getattr(model, 'llm_interface', type('obj', (object,), {'provider': type('obj', (object,), {'call_count': 0}), 'failures': 0})).provider.call_count if hasattr(model, 'llm_interface') else 0,
                "llm_failures": getattr(model, 'llm_interface', type('obj', (object,), {'provider': type('obj', (object,), {'call_count': 0}), 'failures': 0})).failures if hasattr(model, 'llm_interface') else 0
            })

        cum_adoptions = [row["adoption_count"] for row in trajectory]
        diffs = [trajectory[t]["new_adoptions"] for t in range(1, len(trajectory))]
        peak_new = max(diffs) if diffs else 0
        tp = detect_tipping_point(cum_adoptions, pop)
        
        t25, t50 = None, None
        for row in trajectory:
            if t25 is None and row["adoption_count"] >= 0.25 * pop:
                t25 = row["quarter"]
            if t50 is None and row["adoption_count"] >= 0.50 * pop:
                t50 = row["quarter"]
                
        summary = {
            "run_id": run_id,
            "model_class": model_class,
            "topology": topo,
            "beta": beta,
            "seed": seed,
            "subsidy": subsidy,
            "p_base_mode": p_base_mode,
            "final_adoption": cum_adoptions[-1],
            "peak_adoption_velocity": peak_new,
            "tipping_occurred": tp is not None,
            "tipping_quarter": tp,
            "time_to_25_percent": t25,
            "time_to_50_percent": t50,
            "total_llm_calls": trajectory[-1]["llm_calls"],
            "total_llm_failures": trajectory[-1]["llm_failures"]
        }

        sum_path = f"{OUT_DIR}/raw/{run_id}_summary.json"
        traj_path = f"{OUT_DIR}/raw/{run_id}_trajectory.csv"
        man_path = f"{OUT_DIR}/manifests/{run_id}_manifest.json"
        
        atomic_write_json(summary, sum_path)
        df_traj = pd.DataFrame(trajectory)
        atomic_write_csv(df_traj, traj_path)

        manifest = {
            "run_id": run_id,
            "experiment_id": "phase_4f_1",
            "model_class": model_class,
            "topology": topo,
            "beta": beta,
            "seed": seed,
            "population_size": n_agents,
            "horizon": quarters,
            "config_hash": "mock",
            "calibration_hash": "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241",
            "artifact_path": sum_path,
            "trajectory_path": traj_path,
            "status": "COMPLETED"
        }
        atomic_write_json(manifest, man_path)

        if not validate_run(run_id, quarters):
            return {"run_id": run_id, "status": "FAILED_PERSISTENCE"}
        
        return {"run_id": run_id, "status": "COMPLETED"}
    except Exception as e:
        return {"run_id": run_id, "status": "FAILED_EXECUTION", "error": str(e)}

def update_checkpoint(stats, completed_ids, remaining_ids):
    os.makedirs(f"{OUT_DIR}/checkpoints", exist_ok=True)
    ckpt = {
        "timestamp": time.time(),
        **stats,
        "completed_run_ids": list(completed_ids),
        "remaining_run_ids": list(remaining_ids)
    }
    atomic_write_json(ckpt, f"{OUT_DIR}/checkpoints/progress.json")

def main():
    print("Starting Phase 4F.1 Resumable Campaign...")
    
    os.makedirs(f"{OUT_DIR}/raw", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/manifests", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/checkpoints", exist_ok=True)
    
    seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    topologies = ["watts_strogatz", "barabasi_albert"]
    betas = [0.05, 0.15, 0.30]
    
    print("Pre-calculating empirical mean p_base...")
    temp_config = ExperimentConfig()
    temp_config.simulation.baseline_provider = "empirical"
    temp_model = setup_model(temp_config)
    cons = [a for a in temp_model.agents if isinstance(a, ConsumerAgent)]
    emp_p_bases = [temp_model.baseline_provider.predict(a) for a in cons]
    emp_mean = float(np.mean(emp_p_bases))
    print(f"Empirical mean p_base: {emp_mean}")
    
    all_jobs = []
    
    # Core Deterministic
    for seed in seeds:
        all_jobs.append({"run_id": f"R_{seed}_STATIC_0_emp", "model_class": "STATIC_BASELINE", "topo": "NA", "beta": "NA", "seed": seed, "subsidy": 0, "p_base_mode": "empirical"})
        for topo in topologies:
            for beta in betas:
                all_jobs.append({"run_id": f"R_{seed}_{topo}_{beta}_0_emp", "model_class": "DETERMINISTIC_EMPIRICAL_ABM", "topo": topo, "beta": beta, "seed": seed, "subsidy": 0, "p_base_mode": "empirical"})
                all_jobs.append({"run_id": f"R_{seed}_{topo}_{beta}_0_const", "model_class": "DETERMINISTIC_EMPIRICAL_ABM", "topo": topo, "beta": beta, "seed": seed, "subsidy": 0, "p_base_mode": "constant", "constant_val": emp_mean})

    # Economic
    for seed in seeds:
        for sub in [1000.0, 5000.0]:
            all_jobs.append({"run_id": f"R_{seed}_STATIC_{sub}_emp", "model_class": "STATIC_BASELINE", "topo": "NA", "beta": "NA", "seed": seed, "subsidy": sub, "p_base_mode": "empirical"})
            all_jobs.append({"run_id": f"R_{seed}_ws_0.15_{sub}_emp", "model_class": "DETERMINISTIC_EMPIRICAL_ABM", "topo": "watts_strogatz", "beta": 0.15, "seed": seed, "subsidy": sub, "p_base_mode": "empirical"})

    # Cognitive
    for seed in seeds:
        all_jobs.append({"run_id": f"R_{seed}_ws_0.15_0_emp_cog", "model_class": "HYBRID_COGNITIVE_ABM", "topo": "watts_strogatz", "beta": 0.15, "seed": seed, "subsidy": 0, "p_base_mode": "empirical"})
        
    planned_runs = len(all_jobs)
    
    # Filter jobs based on validation
    jobs_to_run = []
    skipped_existing_runs = 0
    completed_run_ids = set()
    remaining_run_ids = set([job["run_id"] for job in all_jobs])
    
    for job in all_jobs:
        if validate_run(job["run_id"], 24):
            skipped_existing_runs += 1
            completed_run_ids.add(job["run_id"])
            remaining_run_ids.remove(job["run_id"])
        else:
            jobs_to_run.append(job)
            
    submitted_runs = len(jobs_to_run)
    executed_runs = 0
    persisted_runs = 0
    validated_runs = 0
    failed_runs = 0

    stats = {
        "planned_runs": planned_runs,
        "submitted_runs": submitted_runs,
        "executed_runs": executed_runs,
        "persisted_runs": persisted_runs,
        "validated_runs": validated_runs,
        "skipped_existing_runs": skipped_existing_runs,
        "failed_runs": failed_runs
    }
    update_checkpoint(stats, completed_run_ids, remaining_run_ids)
    
    print(f"Total jobs planned: {planned_runs}")
    print(f"Skipping {skipped_existing_runs} already validated runs.")
    print(f"Submitting {submitted_runs} jobs to the pool.")
    
    if submitted_runs > 0:
        from joblib import Parallel, delayed
        # Use return_as="generator" if available, else standard
        results = Parallel(n_jobs=4, return_as="generator")(
            delayed(run_single_simulation)(**job) for job in jobs_to_run
        )
        
        for res in results:
            executed_runs += 1
            stats["executed_runs"] = executed_runs
            
            if res["status"] == "COMPLETED":
                persisted_runs += 1
                stats["persisted_runs"] = persisted_runs
                if validate_run(res["run_id"], 24):
                    validated_runs += 1
                    stats["validated_runs"] = validated_runs
                    completed_run_ids.add(res["run_id"])
                    remaining_run_ids.remove(res["run_id"])
                else:
                    failed_runs += 1
                    stats["failed_runs"] = failed_runs
            else:
                failed_runs += 1
                stats["failed_runs"] = failed_runs
                
            update_checkpoint(stats, completed_run_ids, remaining_run_ids)
            
            if executed_runs % 10 == 0:
                print(f"Progress: {executed_runs}/{submitted_runs} executed.")

    print(f"PLANNED: {planned_runs}")
    print(f"SUBMITTED: {submitted_runs}")
    print(f"EXECUTED: {executed_runs}")
    print(f"PERSISTED: {persisted_runs}")
    print(f"VALIDATED: {validated_runs}")
    print(f"SKIPPED_EXISTING: {skipped_existing_runs}")
    print(f"FAILED: {failed_runs}")
    
    if (validated_runs + skipped_existing_runs) == planned_runs:
        print(f"CAMPAIGN COMPLETED SUCCESSFULLY")
    else:
        print(f"CAMPAIGN INCOMPLETE")

if __name__ == "__main__":
    main()
