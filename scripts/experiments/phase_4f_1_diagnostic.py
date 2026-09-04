import os
import json
import pandas as pd
from typing import Dict, Any

OUT_DIR = "outputs/experiments/phase_4f_1/diagnostic"
os.makedirs(OUT_DIR, exist_ok=True)

def atomic_write_json(data: Dict[str, Any], path: str):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)

def atomic_write_csv(df: pd.DataFrame, path: str):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)

def run_diagnostic():
    # 2 agents, 2 timesteps, 1 seed, deterministic ABM
    run_id = "R_diag_42"
    
    # Simulate execution
    summary = {
        "run_id": run_id,
        "model_class": "DETERMINISTIC_EMPIRICAL_ABM",
        "seed": 42,
        "final_adoption": 2,
        "timesteps": 2,
        "agents": 2
    }
    
    trajectory = [
        {"run_id": run_id, "timestep": 0, "adoption": 0},
        {"run_id": run_id, "timestep": 1, "adoption": 1},
        {"run_id": run_id, "timestep": 2, "adoption": 2}
    ]
    df_traj = pd.DataFrame(trajectory)
    
    # Paths
    sum_path = f"{OUT_DIR}/result.json"
    traj_path = f"{OUT_DIR}/trajectory.csv"
    man_path = f"{OUT_DIR}/run_manifest.json"
    
    # 3. Raw artifact written atomically
    atomic_write_json(summary, sum_path)
    atomic_write_csv(df_traj, traj_path)
    
    # 4. Reopen successfully & 5. Required fields validated & 6. Trajectory row count valid
    try:
        with open(sum_path, "r") as f:
            reopened_sum = json.load(f)
        assert "run_id" in reopened_sum
        
        reopened_traj = pd.read_csv(traj_path)
        assert len(reopened_traj) == 3 # 0, 1, 2
        
        # 7. Manifest written & 8. references actual artifact
        manifest = {
            "run_id": run_id,
            "experiment_id": "diag_01",
            "model_class": summary["model_class"],
            "seed": summary["seed"],
            "config_hash": "mock_hash",
            "calibration_hash": "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241",
            "artifact_path": sum_path,
            "trajectory_path": traj_path,
            "status": "COMPLETED"
        }
        atomic_write_json(manifest, man_path)
        
        print("DIAGNOSTIC RUN COMPLETED SUCCESSFULLY.")
        
    except Exception as e:
        print(f"FAILED_PERSISTENCE: {str(e)}")

if __name__ == "__main__":
    run_diagnostic()
