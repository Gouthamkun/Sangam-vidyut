import pytest
import pandas as pd
import json

def test_utility_to_state_mapping():
    df = pd.read_parquet('data/interim/energy/cea/cea_domestic_consumers_by_utility.parquet')
    
    # 21 is JBVNL
    jbvnl = df[df['utility_id'] == 21].iloc[0]
    assert jbvnl['state'] == 'Jharkhand'
    
    # Check Delhi utilities (77-80)
    delhi_utils = df[df['utility_id'].isin([77, 78, 79, 80])]
    assert all(delhi_utils['state'] == 'Delhi')

def test_multi_utility_aggregation():
    df = pd.read_parquet('data/interim/energy/cea/cea_domestic_consumers_by_utility.parquet')
    state_df = pd.read_csv('data/processed/energy/cea/cea_domestic_consumers_by_state.csv')
    
    jharkhand_utils = df[df['state'] == 'Jharkhand']
    assert len(jharkhand_utils) == 3
    
    jh_sum = jharkhand_utils['total_domestic'].sum()
    jh_state_total = state_df[state_df['state'] == 'Jharkhand']['domestic_consumers'].iloc[0]
    
    assert jh_sum == jh_state_total

def test_national_reconciliation_and_double_counting():
    df = pd.read_parquet('data/interim/energy/cea/cea_domestic_consumers_by_utility.parquet')
    national_sum = df['total_domestic'].sum()
    
    with open('data/metadata/energy/cea/cea_domestic_consumers_metadata.json', 'r') as f:
        meta = json.load(f)
        
    assert national_sum == meta['national_domestic_consumers']
    # The true national total for domestic consumers is around 272.7M
    assert national_sum > 270000000 and national_sum < 280000000

def test_state_coverage():
    state_df = pd.read_csv('data/processed/energy/cea/cea_domestic_consumers_by_state.csv')
    assert len(state_df) >= 35 # 36 total states/UTs

def test_no_hces_fallback():
    with open('outputs/calibration/target/pm_surya_ghar_state_penetration_corrected.json', 'r') as f:
        target = json.load(f)
        
    for row in target:
        if row['domestic_consumers'] is not None:
            # Fallbacks would have very different origins, we just check no 'hces' in keys
            assert 'hces' not in str(row).lower()

def test_domestic_category_selection():
    df = pd.read_parquet('data/interim/energy/cea/cea_domestic_consumers_by_utility.parquet')
    # If commercial got included, sums would be massive (e.g. 5M for JBVNL instead of 1M if swapped)
    jbvnl = df[df['utility_id'] == 21].iloc[0]
    assert jbvnl['total_domestic'] == 5508992 # Exactly the parsed domestic total, not commercial
