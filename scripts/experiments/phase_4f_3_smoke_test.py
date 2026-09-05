import os
import json
import pandas as pd
import numpy as np
import hashlib
from src.config.schema import ExperimentConfig
from src.simulation.agents.consumer import ConsumerAgent
from scripts.validation.phase_4e_5_validation import setup_synthetic_model

OUT_DIR = "outputs/experiments/phase_4f_3_smoke"

def ensure_dirs():
    for d in ["manifests", "raw"]:
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

def run_single_simulation(run_id, model_class, topo, seed, subsidy, dynamic_policy, quarters=24, n_agents=500):
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
            
            adoption_rate = adopters / pop
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
                "llm_calls": getattr(model, 'step_llm_decisions', 0),
                "cache_hits": getattr(model.llm_provider, 'cache_hits', 0) if hasattr(model, 'llm_provider') else 0
            })
            
        traj_df = pd.DataFrame(trajectory)
        
        # S+I+R=N check
        sir_sum = traj_df["susceptible_count"] + traj_df["infected_count"] + traj_df["recovered_count"]
        if not (sir_sum == pop).all():
            raise ValueError(f"S+I+R != N invariant violated.")
            
        config_hash = hashlib.sha256(config.model_dump_json().encode()).hexdigest()
            
        manifest = {
            "run_id": run_id,
            "experiment_id": "phase_4f_3_smoke",
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
        man_path = f"{OUT_DIR}/manifests/{run_id}_manifest.json"
        
        atomic_write_csv(traj_df, traj_path)
        atomic_write_json(summary, sum_path)
        atomic_write_json(manifest, man_path)
        
        return summary
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"run_id": run_id, "status": "FAILED", "error": str(e)}

def run_smoke_test():
    ensure_dirs()
    print("=== PHASE 4F.3 SMOKE TEST ===")
    
    tasks = [
        {"run_id": "R_SMOKE_COG", "model_class": "HYBRID_COGNITIVE_ABM", "topo": "watts_strogatz", "seed": 42, "subsidy": 3000.0, "dynamic_policy": False}
    ]
    
    results = []
    for t in tasks:
        print(f"Running {t['run_id']}...")
        r = run_single_simulation(**t)
        results.append(r)
        
    print("\nResults:")
    for r in results:
        print(f"[{r['run_id']}] Adoptions: {r.get('final_adoption', 'N/A')}, Spent: {r.get('total_expenditure', 'N/A')}, Exhausted: {r.get('exhaustion_quarter', 'N/A')}")
        if "total_cache_hits" in r and r["total_cache_hits"] > 0:
            print(f"WARNING: Cache hits non-zero for {r['run_id']}: {r['total_cache_hits']}")

if __name__ == "__main__":
    run_smoke_test()
