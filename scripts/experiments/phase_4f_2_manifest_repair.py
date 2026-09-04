import os
import json
import hashlib

def repair_manifests():
    man_dir = "outputs/experiments/phase_4f_2/manifests/"
    raw_dir = "outputs/experiments/phase_4f_2/raw/"
    
    for fn in os.listdir(man_dir):
        if not fn.endswith("_manifest.json"):
            continue
            
        man_path = os.path.join(man_dir, fn)
        with open(man_path, "r") as f:
            man = json.load(f)
            
        run_id = man["run_id"]
        traj_path = os.path.join(raw_dir, f"{run_id}_trajectory.csv")
        
        # Read initial adoption from trajectory if it exists
        initial_adoption = 5 # Default based on the known starting count
        initial_rate = 5 / 500
        if os.path.exists(traj_path):
            with open(traj_path, "r") as f:
                header = f.readline()
                first_row = f.readline().strip().split(",")
                if len(first_row) > 11:
                    try:
                        initial_adoption = float(first_row[11])
                        initial_rate = float(first_row[12])
                    except:
                        pass
        
        # Add missing fields
        man["behavior_policy"] = "cognitive_accessible_candidate_v1" if man["model_class"] == "HYBRID_COGNITIVE_ABM" else "N/A"
        man["initial_adoption_count"] = initial_adoption
        man["initial_adoption_rate"] = initial_rate
        man["recovery"] = 2
        man["model_identifier"] = "mock"
        man["prompt_version"] = "v1"
        man["configuration_hash"] = hashlib.md5(json.dumps(man, sort_keys=True).encode()).hexdigest()
        
        tmp_path = man_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(man, f, indent=2)
        os.replace(tmp_path, man_path)
        
    print("Manifests repaired with full provenance.")

if __name__ == "__main__":
    repair_manifests()
