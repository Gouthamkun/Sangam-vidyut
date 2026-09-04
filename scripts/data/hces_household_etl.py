import os
import json
import pandas as pd
import numpy as np

def load_level(filepath, columns):
    df = pd.read_json(filepath)
    # Cast keys to string to ensure safe joins
    for k in ['FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No']:
        if k in df.columns:
            df[k] = df[k].astype(str)
    return df[columns]

def run_etl():
    print("Starting HCES 2023-24 Core ETL...")
    
    # 1. Load Level 01
    level_01_path = "data/raw/households/hces_2023_24/data/LEVEL - 01(Section 1 and 1_1).json"
    print(f"Loading Level 01 from {level_01_path}")
    cols_01 = [
        'FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No',
        'State', 'Sector', 'District', 'Multiplier'
    ]
    df_01 = load_level(level_01_path, cols_01)
    
    # 2. Load Level 03
    level_03_path = "data/raw/households/hces_2023_24/data/LEVEL - 03.json"
    print(f"Loading Level 03 from {level_03_path}")
    cols_03 = [
        'FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No',
        'HH_Size_FDQ', 'Type_of_Dwelling_Unit', 'Energy_Source_Lighting'
    ]
    df_03 = load_level(level_03_path, cols_03)
    
    # 3. Load Level 07
    level_07_path = "data/raw/households/hces_2023_24/data/LEVEL - 07 (Section 4_2).json"
    print(f"Loading Level 07 from {level_07_path}")
    cols_07 = [
        'FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No',
        'Free_electricity'
    ]
    df_07 = load_level(level_07_path, cols_07)
    
    # 4. Load Level 15 (Aggregate across visits)
    level_15_path = "data/raw/households/hces_2023_24/data/LEVEL - 15 (Section 1_1, A2,B2  C2).json"
    print(f"Loading Level 15 from {level_15_path}")
    cols_15 = [
        'FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No',
        'MONTHLY_CONSUMPTION_EXP'
    ]
    df_15 = load_level(level_15_path, cols_15)
    
    # Group Level 15 by household keys to get mean monthly consumption
    join_keys = ['FSU_Serial_No', 'Second_Stage_Stratum_No', 'Sample_Household_No']
    
    df_15['MONTHLY_CONSUMPTION_EXP'] = pd.to_numeric(df_15['MONTHLY_CONSUMPTION_EXP'], errors='coerce')
    df_15_agg = df_15.groupby(join_keys, as_index=False)['MONTHLY_CONSUMPTION_EXP'].mean()
    
    # Validate uniqueness
    assert len(df_01) == len(df_01.drop_duplicates(subset=join_keys)), "Duplicate keys in Level 01"
    
    print("Merging levels...")
    df_core = df_01.merge(df_03, on=join_keys, how='outer', indicator='_merge_03')
    unmatched_03 = len(df_core[df_core['_merge_03'] != 'both'])
    df_core = df_core.drop(columns=['_merge_03'])
    
    df_core = df_core.merge(df_07, on=join_keys, how='outer', indicator='_merge_07')
    unmatched_07 = len(df_core[df_core['_merge_07'] != 'both'])
    df_core = df_core.drop(columns=['_merge_07'])
    
    df_core = df_core.merge(df_15_agg, on=join_keys, how='outer', indicator='_merge_15')
    unmatched_15 = len(df_core[df_core['_merge_15'] != 'both'])
    df_core = df_core.drop(columns=['_merge_15'])
    
    print(f"Unmatched Level 03: {unmatched_03}")
    print(f"Unmatched Level 07: {unmatched_07}")
    print(f"Unmatched Level 15: {unmatched_15}")
    
    # 6. Variables & Transformations
    # Weight: since no /100 verified, use raw.
    df_core['processed_survey_weight'] = df_core['Multiplier'].astype(float)
    df_core['raw_multiplier'] = df_core['Multiplier']
    
    df_core['HH_Size_FDQ'] = pd.to_numeric(df_core['HH_Size_FDQ'], errors='coerce')
    
    missing_mpce = df_core['MONTHLY_CONSUMPTION_EXP'].isna().sum()
    print(f"Missing MONTHLY_CONSUMPTION_EXP values: {missing_mpce}")
    
    df_core['derived_mpce'] = np.where(
        (df_core['HH_Size_FDQ'].isna()) | (df_core['HH_Size_FDQ'] <= 0) | (df_core['MONTHLY_CONSUMPTION_EXP'].isna()),
        np.nan,
        df_core['MONTHLY_CONSUMPTION_EXP'] / df_core['HH_Size_FDQ']
    )
    
    # 7. Electricity Level 06
    print("Level 06 Electricity extraction skipped: Item Code unverified in official layout.")
    
    # 8. Save Parquet
    os.makedirs("data/processed/households/hces_2023_24", exist_ok=True)
    out_path = "data/processed/households/hces_2023_24/hces_household_core.parquet"
    df_core.to_parquet(out_path, engine='fastparquet')
    print(f"Saved {len(df_core)} records to {out_path}")

    # Write metadata
    meta = {
        "dataset": "HCES 2023-24 Core",
        "records": len(df_core),
        "unmatched_03": unmatched_03,
        "unmatched_15": unmatched_15,
        "missing_mpce": int(missing_mpce),
        "levels_used": ["01", "03", "07", "15"],
        "electricity_item_code": "UNVERIFIED_SKIPPED"
    }
    
    os.makedirs("data/metadata/households/hces_2023_24", exist_ok=True)
    with open("data/metadata/households/hces_2023_24/hces_household_core_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    run_etl()
