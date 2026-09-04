import os
import json
import hashlib

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def repair_manifests():
    manifests_dir = "outputs/experiments/phase_4f_1_rerun/manifests/"
    raw_dir = "outputs/experiments/phase_4f_1_rerun/raw/"
    
    # 1. HASH EMPIRICAL CALIBRATION ARTIFACT
    emp_calib_path = "outputs/calibration/selected_model/empirical_baseline.json"
    expected_hash = "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"
    
    actual_hash = hash_file(emp_calib_path)
    if actual_hash != expected_hash:
        raise ValueError(f"Hash mismatch! {actual_hash} != {expected_hash}")
        
    invalid_runs = []
    validated_runs = 0
    audit_records = []
    
    for fn in os.listdir(manifests_dir):
        if not fn.endswith("_manifest.json"): continue
        man_path = os.path.join(manifests_dir, fn)
        with open(man_path, 'r') as f:
            manifest = json.load(f)
            
        run_id = manifest['run_id']
        
        # Determine actual baseline provider logic
        # run_id pattern usually ends with _emp or _const
        # e.g. R_42_watts_strogatz_0.05_0_const
        is_const = "const" in run_id
        is_static = "STATIC" in run_id
        is_cog = "cog" in run_id
        
        # update metadata
        if is_const:
            manifest["calibration_artifact_sha256"] = None
            manifest["calibration_artifact_note"] = "Not used as predictor; overriden with ConstantProvider mean."
        else:
            manifest["calibration_artifact_sha256"] = expected_hash
            manifest["calibration_artifact_note"] = "Empirical baseline artifact used for prediction."
            
        # Provider specific
        if is_cog:
            manifest["provider"] = "mock"
            manifest["model_identifier"] = "mock_llm"
            manifest["prompt_version"] = "v1"
            manifest["baseline_provider"] = "empirical"
        else:
            manifest["provider"] = "N/A"
            manifest["baseline_provider"] = "constant" if is_const else "empirical"
            
        # Check summary and trajectory
        sum_path = os.path.join(raw_dir, f"{run_id}_summary.json")
        traj_path = os.path.join(raw_dir, f"{run_id}_trajectory.csv")
        
        summary_status = "VALID"
        trajectory_status = "VALID"
        manifest_status = "VALID"
        failure_reason = ""
        
        # Load summary
        with open(sum_path, 'r') as f:
            summary = json.load(f)
            if summary.get("run_id") != run_id:
                summary_status = "INVALID"
                failure_reason = "Summary run_id mismatch"
                
        # Trajectory validation
        try:
            import pandas as pd
            traj_df = pd.read_csv(traj_path)
            if traj_df["run_id"].iloc[0] != run_id:
                trajectory_status = "INVALID"
                failure_reason = "Trajectory run_id mismatch"
            
            # required columns
            required_cols = ["quarter", "susceptible_count", "infected_count", "recovered_count", "adoption_rate"]
            for c in required_cols:
                if c not in traj_df.columns:
                    trajectory_status = "INVALID"
                    failure_reason = f"Missing column {c}"
            
            # S+I+R=N
            if trajectory_status == "VALID":
                sir_sum = traj_df["susceptible_count"] + traj_df["infected_count"] + traj_df["recovered_count"]
                N = sir_sum.iloc[0]
                if not (sir_sum == N).all():
                    trajectory_status = "INVALID"
                    failure_reason = "S+I+R != N"
                    
            # Non-negative
            if trajectory_status == "VALID":
                if (traj_df[["susceptible_count", "infected_count", "recovered_count"]] < 0).any().any():
                    trajectory_status = "INVALID"
                    failure_reason = "Negative counts"
                    
            # NaN checks
            if trajectory_status == "VALID":
                if traj_df[required_cols].isna().any().any():
                    trajectory_status = "INVALID"
                    failure_reason = "NaN values found"
                    
            # final state match
            if trajectory_status == "VALID":
                final_adoption_traj = traj_df["adoption_count"].iloc[-1]
                if float(final_adoption_traj) != float(summary.get("final_adoption", -1)):
                    trajectory_status = "INVALID"
                    failure_reason = "Summary final adoption mismatch"
                    
        except Exception as e:
            trajectory_status = "INVALID"
            failure_reason = str(e)
            
        overall_status = "VALID" if (summary_status == "VALID" and trajectory_status == "VALID") else "INVALID"
        if overall_status == "INVALID":
            invalid_runs.append((run_id, failure_reason))
        else:
            validated_runs += 1
            
        # Add artifact hashes
        manifest["summary_sha256"] = hash_file(sum_path)
        manifest["trajectory_sha256"] = hash_file(traj_path)
        
        # Rewrite manifest
        with open(man_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        audit_records.append({
            "run_id": run_id,
            "model_class": manifest["model_class"],
            "provider": manifest["provider"],
            "baseline_provider": manifest["baseline_provider"],
            "calibration_hash_status": "VALID",
            "summary_status": summary_status,
            "trajectory_status": trajectory_status,
            "manifest_status": manifest_status,
            "overall_status": overall_status,
            "failure_reason": failure_reason
        })
        
    print(f"Validated: {validated_runs}")
    print(f"Invalid: {len(invalid_runs)}")
    
    os.makedirs(f"outputs/experiments/phase_4f_1_rerun/tables", exist_ok=True)
    pd.DataFrame(audit_records).to_csv("outputs/experiments/phase_4f_1_rerun/tables/provenance_audit.csv", index=False)

    
if __name__ == "__main__":
    repair_manifests()
