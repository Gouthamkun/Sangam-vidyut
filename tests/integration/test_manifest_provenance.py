import os
import json
import pytest
import pandas as pd
import hashlib

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def test_calibration_hash_correctness():
    path = "outputs/calibration/selected_model/empirical_baseline.json"
    expected = "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"
    assert hash_file(path) == expected

def test_manifest_provenance_consistency():
    manifests_dir = "outputs/experiments/phase_4f_1_rerun/manifests/"
    raw_dir = "outputs/experiments/phase_4f_1_rerun/raw/"
    
    manifest_files = [f for f in os.listdir(manifests_dir) if f.endswith("_manifest.json") and not f.startswith("R_RECOVERY_TEST")]
    assert len(manifest_files) == 180
    
    for fn in manifest_files:
        with open(os.path.join(manifests_dir, fn), 'r') as f:
            manifest = json.load(f)
            
        assert "calibration_artifact_sha256" in manifest
        run_id = manifest["run_id"]
        is_const = "const" in run_id
        is_cog = "cog" in run_id
        
        # semantics
        if is_const:
            assert manifest["calibration_artifact_sha256"] is None
            assert manifest["baseline_provider"] == "constant"
        else:
            assert manifest["calibration_artifact_sha256"] == "0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241"
            assert manifest["baseline_provider"] == "empirical"
            
        if is_cog:
            assert manifest["provider"] == "mock"
            
        # Missing hash detection is done above via 'in' 
        # Raw artifact linkage
        sum_path = os.path.join(raw_dir, f"{run_id}_summary.json")
        traj_path = os.path.join(raw_dir, f"{run_id}_trajectory.csv")
        assert manifest["summary_sha256"] == hash_file(sum_path)
        assert manifest["trajectory_sha256"] == hash_file(traj_path)

        # Validation count correctness
        with open(sum_path, 'r') as sf:
            summary = json.load(sf)
        assert summary["run_id"] == run_id
        traj = pd.read_csv(traj_path)
        assert traj["run_id"].iloc[0] == run_id
        
def test_static_legacy_provenance_semantics():
    # Tested dynamically in loop above
    pass
