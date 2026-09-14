import pytest
import pandas as pd
import os
import sys

# We add the root directory to path to allow importing app
sys.path.insert(0, os.path.abspath("."))
from app import load_phase2_data, load_trajectory

def test_phase_4f2_filtering_A():
    # TEST A: Phase 4F.2: subsidy=0, WS, beta=0.05, empirical
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 0) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.05) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert len(subset) == 1
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.01) < 0.001

def test_phase_4f2_filtering_B():
    # TEST B: Phase 4F.2: subsidy=3000, WS, beta=0.05, empirical
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 3000) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.05) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert len(subset) == 1
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.9724) < 0.001

def test_phase_4f2_filtering_C():
    # TEST C: Phase 4F.2: subsidy=3000, BA, beta=0.05, empirical
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 3000) & 
                 (df2["topology"] == "barabasi_albert") & 
                 (df2["beta"] == 0.05) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert len(subset) == 1
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.9842) < 0.001

def test_phase_4f2_filtering_D():
    # TEST D: Phase 4F.2: subsidy=3000, WS, beta=0.30, empirical
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 3000) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.30) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert len(subset) == 1
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.9598) < 0.001

def test_phase_4f2_filtering_E():
    # TEST E: Phase 4F.2: subsidy=3000, WS, beta=0.15, constant
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 3000) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.15) & 
                 (df2["p_base_mode"] == "constant") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert len(subset) == 1
    assert abs(subset["mean_adoption_pct"].iloc[0] - 0.9912) < 0.001

def test_phase_4f3_filtering_F():
    # TEST F: Phase 4F.3: subsidy=3000, WS, FIXED
    traj = load_trajectory(3000.0, "watts_strogatz", False)
    assert not traj.empty
    final_row = traj.iloc[-1]
    assert final_row["adoption_count"] == 494
    assert (1000000 - final_row["budget_remaining"]) == 1000000

def test_phase_4f3_filtering_G():
    # TEST G: Phase 4F.3: subsidy=3000, WS, DYNAMIC
    traj = load_trajectory(3000.0, "watts_strogatz", True)
    assert not traj.empty
    final_row = traj.iloc[-1]
    assert final_row["adoption_count"] == 433
    assert (1000000 - final_row["budget_remaining"]) == 1000000

def test_unsupported_combination():
    df2 = load_phase2_data()
    subset = df2[(df2["subsidy"] == 999999) & 
                 (df2["topology"] == "watts_strogatz") & 
                 (df2["beta"] == 0.05) & 
                 (df2["p_base_mode"] == "empirical") &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert subset.empty
