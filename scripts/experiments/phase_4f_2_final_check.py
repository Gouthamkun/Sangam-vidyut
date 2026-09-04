import os
import json
import pandas as pd

def check_counts():
    man_dir = "outputs/experiments/phase_4f_2/manifests"
    raw_dir = "outputs/experiments/phase_4f_2/raw"
    
    manifests = [f for f in os.listdir(man_dir) if f.endswith(".json") and not f.startswith("R_RECOVERY_TEST")]
    summaries = [f for f in os.listdir(raw_dir) if f.endswith("_summary.json")]
    trajectories = [f for f in os.listdir(raw_dir) if f.endswith("_trajectory.csv")]
    
    print(f"Artifact counts:")
    print(f"Manifests: {len(manifests)}")
    print(f"Summaries: {len(summaries)}")
    print(f"Trajectories: {len(trajectories)}")
    
    if len(manifests) == 560:
        print("\nAll 560 runs exist.")
    else:
        print(f"\nMissing runs: {560 - len(manifests)}")
        
    records = []
    for fn in manifests:
        with open(os.path.join(man_dir, fn)) as f:
            records.append(json.load(f))
            
    df = pd.DataFrame(records)
    print("\nFactorial Breakdown:")
    print(df.groupby(["model_class", "baseline_provider"]).size())
    
    print("\nTest Status:")
    os.system("python -m pytest -q")

if __name__ == "__main__":
    check_counts()
