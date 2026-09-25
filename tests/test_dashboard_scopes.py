import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from app import load_phase1_data, load_phase2_data

def test_phase_4f1_subsidy_scope_collapse():
    # Verify that in Phase 4F.1, selecting beta=0.05 correctly yields only one subsidy (subsidy=0),
    # meaning the distribution chart should rightly collapse to a single point.
    df1 = load_phase1_data()
    df_abm = df1[(df1["topology"] == "watts_strogatz") & 
                 (df1["beta"] == "0.05") & 
                 (df1["p_base_mode"] == "empirical") &
                 (df1["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert df_abm["subsidy"].nunique() == 1
    assert df_abm["subsidy"].iloc[0] == 0.0
    
def test_phase_4f1_subsidy_scope_full():
    # Verify that in Phase 4F.1, selecting beta=0.15 yields the full subsidy sweep (0, 1000, 5000).
    df1 = load_phase1_data()
    df_abm = df1[(df1["topology"] == "watts_strogatz") & 
                 (df1["beta"] == "0.15") & 
                 (df1["p_base_mode"] == "empirical") &
                 (df1["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    assert df_abm["subsidy"].nunique() == 3
    assert set(df_abm["subsidy"]) == {0.0, 1000.0, 5000.0}

def test_heterogeneity_filtering_scope():
    # Verify that heterogeneity data for 4F.2 extracts exactly empirical vs constant for the same beta and topology
    df2 = load_phase2_data()
    df_comp = df2[df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
    
    # scope: topology=watts_strogatz, beta=0.30
    df_het = df_comp[(df_comp["topology"] == "watts_strogatz") & (df_comp["beta"] == 0.30)]
    assert not df_het.empty
    assert set(df_het["p_base_mode"]) == {"empirical", "constant"}
    assert set(df_het["subsidy"]) == {0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0}

def test_aggregation_semantics():
    # Verify that the factor panels correctly aggregate across the hidden dimensions.
    # For Subsidy Response, we expect all topologies and betas to be collapsed into means per subsidy.
    df2 = load_phase2_data()
    df_comp = df2[df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
    
    # Grouping by subsidy should yield exactly one row per valid subsidy in Phase 2
    agg_df = df_comp.groupby("subsidy")["mean_adoption_pct"].mean().reset_index()
    assert len(agg_df) == 6
    assert set(agg_df["subsidy"]) == {0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0}
    
    # Grouping by topology AND subsidy should yield two rows per subsidy (WS and BA)
    agg_top = df_comp.groupby(["subsidy", "topology"])["mean_adoption_pct"].mean().reset_index()
    assert len(agg_top) == 12
