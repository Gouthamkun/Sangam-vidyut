import os
import pandas as pd
import numpy as np
from scripts.data.hces_household_etl import run_etl

def audit():
    path = "data/processed/households/hces_2023_24/hces_household_core.parquet"
    df = pd.read_parquet(path, engine='fastparquet')
    
    print("--- 1. RAW TO PROCESSED RECONCILIATION ---")
    print(f"Total rows: {len(df)}")
    keys = ['FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No']
    unique_keys = len(df.drop_duplicates(subset=keys))
    print(f"Unique household keys: {unique_keys}")
    print(f"Duplicate keys: {len(df) - unique_keys}")
    
    print("\n--- 3 & 4. EXPENDITURE & MPCE AUDIT ---")
    # Check denominator validity
    zero_hh = (df['HH_Size_FDQ'] == 0).sum()
    neg_hh = (df['HH_Size_FDQ'] < 0).sum()
    nan_hh = df['HH_Size_FDQ'].isna().sum()
    print(f"HH_Size_FDQ - Zeros: {zero_hh}, Negatives: {neg_hh}, NaNs: {nan_hh}")
    print(f"derived_mpce - Zeros: {(df['derived_mpce'] == 0).sum()}, Negatives: {(df['derived_mpce'] < 0).sum()}, NaNs: {df['derived_mpce'].isna().sum()}")
    print(f"derived_mpce - Min: {df['derived_mpce'].min()}, Max: {df['derived_mpce'].max()}")
    
    print("\n--- 5. SURVEY WEIGHT AUDIT ---")
    w = df['raw_multiplier']
    print(f"Raw Multiplier - Min: {w.min()}, Median: {w.median()}, Mean: {w.mean()}, Max: {w.max()}")
    print(f"Unique multiplier values: {w.nunique()}")
    
    print("\n--- 6. DISTRIBUTION CHECK ---")
    # Unweighted stats
    print(f"Unweighted MPCE mean: {df['derived_mpce'].mean()}")
    print(f"Unweighted HH Size mean: {df['HH_Size_FDQ'].mean()}")
    
    # Weighted stats (using raw multiplier without division)
    weighted_mpce_mean = np.average(df['derived_mpce'], weights=df['processed_survey_weight'])
    weighted_hh_mean = np.average(df['HH_Size_FDQ'], weights=df['processed_survey_weight'])
    print(f"Weighted MPCE mean (using raw multiplier): {weighted_mpce_mean}")
    print(f"Weighted HH Size mean (using raw multiplier): {weighted_hh_mean}")
    
    print("\n--- 7. MISSING-DATA AUDIT ---")
    for col in df.columns:
        nans = df[col].isna().sum()
        zeros = (df[col] == 0).sum() if pd.api.types.is_numeric_dtype(df[col]) else 0
        min_v = df[col].min()
        max_v = df[col].max()
        print(f"{col}: NaNs={nans}, Zeros={zeros}, Min={min_v}, Max={max_v}")
        
    print("\n--- 11. REPRODUCIBILITY ---")
    # Backup the original
    import shutil
    shutil.copyfile(path, path + ".bak")
    
    # Run ETL again
    run_etl()
    df_new = pd.read_parquet(path, engine='fastparquet')
    
    try:
        pd.testing.assert_frame_equal(df, df_new)
        print("Reproducibility: SUCCESS. Deterministic equality verified.")
    except AssertionError as e:
        print(f"Reproducibility: FAILED. {e}")
        
    # Restore backup
    shutil.move(path + ".bak", path)

if __name__ == "__main__":
    audit()
