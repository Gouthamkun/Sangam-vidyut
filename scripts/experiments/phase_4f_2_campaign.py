import os
import json
import pandas as pd
import numpy as np
import hashlib
from joblib import Parallel, delayed

from src.config.schema import ExperimentConfig
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

OUT_DIR = "outputs/experiments/phase_4f_2"

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

def setup_model(config, constant_pbase=None):
    model = setup_synthetic_model(config)
    if constant_pbase is not None:
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
            
        if "run_id" not in reopened_sum: return False
        if len(reopened_traj) != (quarters + 1): return False
        if manifest.get("status") != "COMPLETED": return False
        return True
    except:
        return False

def run_single_simulation(run_id, model_class, topo, beta, seed, subsidy, p_base_mode, quarters=24, constant_val=None, n_agents=500):
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
                "adoption_rate": adopters / max(1, pop),
                "new_adoptions": model.new_adoptions_last_step if t > 0 else adopters,
                "mean_p_base": np.mean(p_bases),
                "median_p_base": np.median(p_bases),
                "p90_p_base": np.percentile(p_bases, 90),
                "mean_sir_score": np.mean(sir_scores),
                "mean_affordability": np.mean([min(model.current_subsidy / max(model.current_panel_price, 1.0), 1.0) for _ in consumers]),
                "llm_calls": getattr(model, 'step_llm_decisions', 0),
                "llm_failures": getattr(model, 'step_llm_failures', 0)
            })
            
        traj_df = pd.DataFrame(trajectory)
        
        # Tipping calculation (5% in a single quarter)
        tipping_quarter = None
        for t_idx in range(1, len(traj_df)):
            if traj_df.iloc[t_idx]["new_adoptions"] / pop >= 0.05:
                tipping_quarter = t_idx
                break
                
        # S+I+R=N check
        sir_sum = traj_df["susceptible_count"] + traj_df["infected_count"] + traj_df["recovered_count"]
        if not (sir_sum == pop).all():
            raise ValueError(f"S+I+R != N invariant violated. Pop: {pop}, Sums: {sir_sum.tolist()}")
            
        # Manifest
        manifest = {
            "run_id": run_id,
            "experiment_id": "phase_4f_2",
            "model_class": model_class,
            "topology": topo,
            "beta": beta,
            "seed": seed,
            "subsidy": subsidy,
            "population_size": pop,
            "horizon": quarters,
            "status": "COMPLETED",
            "provider": config.llm.provider if config.llm.enabled else "N/A",
            "baseline_provider": "constant" if p_base_mode == "constant" else "empirical",
            "calibration_artifact_sha256": "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241" if p_base_mode == "empirical" else None,
            "calibration_artifact_note": "Empirical baseline artifact used for prediction." if p_base_mode == "empirical" else "Constant mean proxy used; empirical artifact bypassed.",
        }
        
        # Summary
        summary = {
            "run_id": run_id,
            "model_class": model_class,
            "topology": topo,
            "beta": beta,
            "seed": seed,
            "subsidy": subsidy,
            "p_base_mode": p_base_mode,
            "final_adoption": int(traj_df.iloc[-1]["adoption_count"]),
            "peak_adoption_velocity": int(traj_df["new_adoptions"].max()),
            "tipping_occurred": tipping_quarter is not None,
            "tipping_quarter": tipping_quarter,
            "total_llm_calls": int(traj_df["llm_calls"].sum()),
            "total_llm_failures": int(traj_df["llm_failures"].sum())
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

def build_experiment_grid(is_smoke=False):
    seeds = [42] if is_smoke else [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    subsidies = [0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0]
    topologies = ["watts_strogatz", "barabasi_albert"]
    betas = [0.05, 0.15, 0.30]
    
    tasks = []
    
    # 1. Deterministic Empirical ABM
    for seed in seeds:
        for sub in subsidies:
            for topo in topologies:
                for beta in betas:
                    tasks.append({
                        "run_id": f"R_{seed}_{topo}_{beta}_{sub}_emp",
                        "model_class": "DETERMINISTIC_EMPIRICAL_ABM",
                        "topo": topo,
                        "beta": beta,
                        "seed": seed,
                        "subsidy": sub,
                        "p_base_mode": "empirical"
                    })
                    
    # 2. Constant Ablation (Only WS, Beta=0.15 to save compute, or full grid? Let's do full for parity or WS/Beta0.15 to save)
    # The prompt says: "empirical p_base vs constant p_base equal to empirical-population mean". Let's run full grid for WS to compare.
    for seed in seeds:
        for sub in subsidies:
            for beta in betas:
                tasks.append({
                    "run_id": f"R_{seed}_ws_{beta}_{sub}_const",
                    "model_class": "DETERMINISTIC_EMPIRICAL_ABM",
                    "topo": "watts_strogatz",
                    "beta": beta,
                    "seed": seed,
                    "subsidy": sub,
                    "p_base_mode": "constant",
                    "constant_val": 0.001238 # Empirical population mean
                })

    # 3. Hybrid Cognitive ABM
    # Only run on transition subsidies to save compute
    for seed in seeds:
        for sub in [2000.0, 3000.0]:
            tasks.append({
                "run_id": f"R_{seed}_ws_0.15_{sub}_cog",
                "model_class": "HYBRID_COGNITIVE_ABM",
                "topo": "watts_strogatz",
                "beta": 0.15,
                "seed": seed,
                "subsidy": sub,
                "p_base_mode": "empirical"
            })
                
    return tasks

def main(is_smoke=False):
    ensure_dirs()
    tasks = build_experiment_grid(is_smoke)
    print(f"Total tasks planned: {len(tasks)}")
    
    pending = []
    for t in tasks:
        if not validate_run(t["run_id"], quarters=24):
            pending.append(t)
            
    print(f"Pending tasks to run: {len(pending)}")
    
    if len(pending) > 0:
        results = Parallel(n_jobs=4)(
            delayed(run_single_simulation)(**kw) for kw in pending
        )
        failures = [r for r in results if r["status"] != "COMPLETED"]
        if failures:
            print(f"Encountered {len(failures)} failures.")
        else:
            print("All pending runs completed successfully.")
    else:
        print("All runs already completed.")
        
if __name__ == "__main__":
    main(is_smoke=False) # Start full campaign
