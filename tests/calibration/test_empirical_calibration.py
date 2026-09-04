import pytest
import numpy as np
import pandas as pd
import json
import os
from src.models.statistical.empirical_baseline import EmpiricalEcologicalBaseline
from schemas.data.calibration import SerializedModelArtifact, TargetSpec, PreprocessingSpec

def test_probability_bounds():
    model = EmpiricalEcologicalBaseline()
    model.is_fitted = True
    model.feature_order = ['log_mpce', 'sector_2']
    model.coefficients = {'log_mpce': 0.5, 'sector_2': -0.1}
    model.intercept = -2.0
    
    df = pd.DataFrame({'derived_mpce': [1000, 50000], 'sector': [1, 2], 'dwelling_type': [1, 1], 'electricity_access': [1, 1], 'free_electricity': [1, 1]})
    preds = model.predict_proba(df)
    
    assert (preds >= 0.0).all()
    assert (preds <= 1.0).all()

def test_deterministic_preprocessing():
    model = EmpiricalEcologicalBaseline()
    model.is_fitted = False
    
    df = pd.DataFrame({
        'derived_mpce': [10.0, 100.0], 
        'sector': [1, 2],
        'dwelling_type': [1, 2],
        'electricity_access': [1, 2],
        'free_electricity': [1, 2]
    })
    
    X_proc = model._preprocess(df)
    assert 'log_mpce' in X_proc.columns
    assert 'derived_mpce' not in X_proc.columns
    assert np.allclose(X_proc['log_mpce'], np.log1p([10.0, 100.0]))
    assert 'sector_2' in X_proc.columns
    
def test_feature_exclusion():
    model = EmpiricalEcologicalBaseline()
    df = pd.DataFrame({'derived_mpce': [100], 'sector': [1], 'survey_weight': [100], 'home_owner': [1], 'system_size_kw': [3.0]})
    
    # Feature exclusion happens via CalibrationConfig before preprocess in the script,
    # but the model also enforces it after fitting.
    model.is_fitted = True
    model.feature_order = ['log_mpce', 'sector_1']
    X_proc = model._preprocess(df)
    
    assert 'survey_weight' not in X_proc.columns
    assert 'home_owner' not in X_proc.columns
    assert 'system_size_kw' not in X_proc.columns

def test_serialization():
    model = EmpiricalEcologicalBaseline()
    model.is_fitted = True
    model.coefficients = {'a': 1.0}
    model.intercept = 0.0
    model.feature_order = ['a']
    
    target = TargetSpec()
    prep = PreprocessingSpec()
    
    artifact = SerializedModelArtifact(
        target=target, preprocessing=prep,
        coefficients=model.coefficients, intercept=model.intercept,
        feature_order=model.feature_order, calibration_seed=42, training_states=["state1"]
    )
    
    path = "tests/temp_model.json"
    model.save(path, artifact)
    
    loaded_model = EmpiricalEcologicalBaseline()
    loaded_model.load(path)
    
    assert loaded_model.is_fitted
    assert loaded_model.coefficients == {'a': 1.0}
    assert loaded_model.intercept == 0.0
    
    os.remove(path)
