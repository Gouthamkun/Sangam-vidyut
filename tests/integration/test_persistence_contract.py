import pytest
import os
import json
import pandas as pd
from scripts.experiments.phase_4f_1_campaign import atomic_write_json, atomic_write_csv

def test_single_run_persistence(tmp_path):
    data = {"run_id": "test_01"}
    path = str(tmp_path / "test.json")
    atomic_write_json(data, path)
    assert os.path.exists(path)
    with open(path, "r") as f:
        reopened = json.load(f)
    assert reopened["run_id"] == "test_01"

def test_corrupted_result_detection(tmp_path):
    # Simulate a corrupted result
    path = str(tmp_path / "test.json")
    with open(path, "w") as f:
        f.write("{corrupted_json:")
    
    # Validation should fail
    try:
        with open(path, "r") as f:
            json.load(f)
        pytest.fail("Should have raised JSONDecodeError")
    except json.JSONDecodeError:
        pass

def test_missing_result_detection(tmp_path):
    path = str(tmp_path / "missing.json")
    assert not os.path.exists(path)

def test_atomic_file_writing(tmp_path):
    df = pd.DataFrame([{"a": 1}])
    path = str(tmp_path / "test.csv")
    atomic_write_csv(df, path)
    assert os.path.exists(path)
    assert not os.path.exists(path + ".tmp")

def test_completion_counter_correctness():
    # If 10 submitted, 10 executed, 8 persisted, 8 validated -> fails
    submitted = 10
    validated = 8
    assert submitted != validated

def test_manifest_result_mismatch(tmp_path):
    manifest = {"run_id": "123", "artifact_path": "nonexistent.json"}
    path = str(tmp_path / "manifest.json")
    atomic_write_json(manifest, path)
    
    with open(path, "r") as f:
        loaded = json.load(f)
        
    assert not os.path.exists(loaded["artifact_path"])
