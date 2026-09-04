import pytest
import os
import json
import pandas as pd
from src.models.statistical.empirical_baseline import EmpiricalEcologicalBaseline
from schemas.data.calibration import SerializedModelArtifact

def test_corrected_target_ingestion():
    target_path = 'outputs/calibration/target/pm_surya_ghar_state_penetration_corrected.json'
    assert os.path.exists(target_path)
    
    with open(target_path, 'r') as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # 36 states coverage
    assert len(df) == 36
    
    # PM Surya Ghar date provenance
    assert (df['numerator_reference_date'] == "27.07.2026").all()
    assert (df['denominator_reference_date'] == "31.03.2024").all()
    
    # No HCES fallback
    assert df['domestic_consumers'].notna().all()
    assert (df['domestic_consumers'] > 0).all()
    
    # Target bounds
    assert (df['observed_rate'] >= 0).all()
    assert (df['observed_rate'] <= 1).all()

def test_no_contaminated_target():
    # Verify the contaminated target is correctly labeled
    contam_path = 'outputs/calibration/target/pm_surya_ghar_state_penetration_contaminated.json'
    if os.path.exists(contam_path):
        with open(contam_path, 'r') as f:
            data = json.load(f)
        assert any("INVALID" in str(v) for v in data[0].values())

def test_artifact_schema_validity():
    model_path = 'outputs/calibration/selected_model/empirical_baseline.json'
    if os.path.exists(model_path):
        model = EmpiricalEcologicalBaseline()
        model.load(model_path)
        assert model.is_fitted
        
        # Check deterministic feature ordering
        assert 'log_mpce' in model.feature_order
        assert 'household_size' in model.feature_order
        assert 'home_owner' not in model.feature_order
        assert 'system_size_kw' not in model.feature_order
        assert 'survey_weight' not in model.feature_order
