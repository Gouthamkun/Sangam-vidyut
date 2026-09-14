import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from app import load_phase1_data, load_phase2_data, load_phase3_data

def test_phase1_isolation():
    # Phase 4F.1 dataset should contain EXACTLY subsidies 0, 1000, 5000
    df1 = load_phase1_data()
    subsidies = df1["subsidy"].unique().tolist()
    assert 0.0 in subsidies
    assert 1000.0 in subsidies
    assert 5000.0 in subsidies
    assert 3000.0 not in subsidies

def test_phase1_filtering():
    # Test valid combination
    df1 = load_phase1_data()
    subset = df1[(df1["subsidy"] == 0.0) & 
                 (df1["topology"] == "watts_strogatz") & 
                 (df1["beta"] == "0.15") & 
                 (df1["p_base_mode"] == "empirical") &
                 (df1["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert not subset.empty
    
def test_phase2_filtering_valid():
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 3000.0) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.15) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert not subset.empty
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.933) < 0.001

def test_phase3_factors_locked():
    df3 = load_phase3_data()
    # fixed_vs_dynamic shouldn't sweep beta/p_base_mode
    assert "beta" not in df3.columns
    assert "p_base_mode" not in df3.columns

def test_unsupported_combinations():
    df1 = load_phase1_data()
    subset = df1[(df1["subsidy"] == 3000.0)]
    assert subset.empty # 3000 was not run in 4F.1
