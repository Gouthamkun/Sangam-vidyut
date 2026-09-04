import os
import pandas as pd
import pytest

def test_historical_adoption_schema():
    df = pd.read_csv('data/processed/solar/adoption/residential_adoption_historical.csv')
    required_cols = ['source_document', 'question_number', 'answer_date', 'reference_date', 'state', 'metric_raw', 'value_raw', 'unit', 'cumulative']
    for col in required_cols:
        assert col in df.columns, f"Missing {col} in historical data"

def test_pmsuryaghar_adoption_schema():
    df = pd.read_csv('data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv')
    required_cols = ['source_document', 'question_number', 'answer_date', 'reference_date', 'state', 'installations', 'households_raw', 'cfa_raw', 'unit', 'cumulative']
    for col in required_cols:
        assert col in df.columns, f"Missing {col} in pmsuryaghar data"

def test_no_duplicate_states():
    df = pd.read_csv('data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv')
    # State should be unique per reference date
    duplicates = df.duplicated(subset=['state', 'reference_date']).sum()
    assert duplicates == 0, "Duplicate states found for the same reference date"

def test_numeric_parsing():
    df = pd.read_csv('data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv')
    assert pd.api.types.is_numeric_dtype(df['installations']), "Installations should be numeric"
    assert (df['installations'] >= 0).all(), "Installations cannot be negative"

def test_official_total_reconciliation():
    df = pd.read_csv('data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv')
    computed_installations = df['installations'].sum()
    # Official total as per Lok Sabha UQ 1698
    assert computed_installations == 4045298, f"Computed total {computed_installations} does not match official 4045298"

def test_metadata_provenance():
    assert os.path.exists('data/metadata/solar/adoption/uq_1698_metadata.json')
    assert os.path.exists('data/metadata/solar/adoption/uq_1936_metadata.json')
