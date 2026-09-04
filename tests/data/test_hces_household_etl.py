import os
import pandas as pd
import pytest

def test_hces_household_core_exists():
    path = "data/processed/households/hces_2023_24/hces_household_core.parquet"
    assert os.path.exists(path), "Parquet file should be generated"

def test_hces_household_core_records():
    path = "data/processed/households/hces_2023_24/hces_household_core.parquet"
    df = pd.read_parquet(path, engine='fastparquet')
    
    assert len(df) == 261953, f"Expected 261,953 records, got {len(df)}"
    
    # Check keys
    keys = ['FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No']
    assert len(df.drop_duplicates(subset=keys)) == len(df), "Household keys must be completely unique"
    
def test_hces_household_mpce():
    path = "data/processed/households/hces_2023_24/hces_household_core.parquet"
    df = pd.read_parquet(path, engine='fastparquet')
    
    assert 'derived_mpce' in df.columns
    assert 'processed_survey_weight' in df.columns
    assert 'raw_multiplier' in df.columns
    
    assert df['derived_mpce'].isna().sum() == 0, "There should be no missing MPCE values after average aggregation"
    assert (df['derived_mpce'] > 0).all(), "All derived MPCE should be positive"
