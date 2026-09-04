import os
import pandas as pd
import pytest

def test_rs_capacity_schema():
    df = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_rs210.csv')
    required_cols = ['source_document', 'question_number', 'answer_date', 'reference_date', 'state', 'metric_raw', 'value_raw', 'unit_raw', 'sector', 'programme', 'cumulative']
    for col in required_cols:
        assert col in df.columns, f"Missing {col} in RS data"

def test_ls_capacity_schema():
    df = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_ls3579.csv')
    required_cols = ['source_document', 'question_number', 'answer_date', 'reference_date', 'state', 'metric_raw', 'value_raw', 'unit_raw', 'sector', 'programme', 'cumulative']
    for col in required_cols:
        assert col in df.columns, f"Missing {col} in LS data"

def test_numeric_parsing():
    df1 = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_rs210.csv')
    df2 = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_ls3579.csv')
    assert pd.api.types.is_numeric_dtype(df1['value_raw']), "RS Capacity should be numeric"
    assert (df1['value_raw'] >= 0).all(), "RS Capacity cannot be negative"
    assert pd.api.types.is_numeric_dtype(df2['value_raw']), "LS Capacity should be numeric"
    assert (df2['value_raw'] >= 0).all(), "LS Capacity cannot be negative"

def test_official_total_reconciliation():
    df1 = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_rs210.csv')
    cfa_total = df1[df1['metric_raw'] == 'Capacity installed under CFA under Phase-II (MW)']['value_raw'].sum()
    assert abs(cfa_total - 2045.72) < 0.1, f"Computed RS total {cfa_total} does not match official 2045.72"
    
    df2 = pd.read_csv('data/processed/solar/adoption/residential_capacity_phase2_ls3579.csv')
    alloc_total = df2[df2['metric_raw'] == 'Total Net Allocation in Ph-II so far']['value_raw'].sum()
    assert abs(alloc_total - 3370.82) < 0.1, f"Computed LS total {alloc_total} does not match official 3370.82"

def test_metadata_provenance():
    assert os.path.exists('data/metadata/solar/adoption/rs_sq210_metadata.json')
    assert os.path.exists('data/metadata/solar/adoption/ls_uq3579_metadata.json')
