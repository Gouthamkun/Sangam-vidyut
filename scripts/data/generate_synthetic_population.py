import os
import uuid
import json
import numpy as np
import pandas as pd
from datetime import datetime
import argparse

def compute_weighted_deciles(df, value_col='derived_mpce', weight_col='Multiplier'):
    """
    Computes weighted deciles for the entire dataset based on the survey weights.
    Returns a pandas Series of integer deciles (1-10).
    """
    # Sort data
    df_sorted = df.sort_values(value_col)
    
    # Compute cumulative weights
    cum_weights = df_sorted[weight_col].cumsum()
    total_weight = df_sorted[weight_col].sum()
    
    # Calculate cumulative percentage
    cum_pct = cum_weights / total_weight
    
    # Assign deciles (1 to 10)
    # 0 to 0.1 -> 1, ..., 0.9 to 1.0 -> 10
    deciles = np.ceil(cum_pct * 10).astype(int)
    # Clip to ensure valid range just in case of float precision issues
    deciles = deciles.clip(1, 10)
    
    # Map back to original index
    df_sorted['mpce_decile'] = deciles
    return df_sorted.loc[df.index, 'mpce_decile']

def generate_synthetic_population(hces_df, n_agents, seed):
    """
    Performs survey-weighted empirical resampling.
    """
    # Sample with replacement using explicit seed
    sample_df = hces_df.sample(n=n_agents, replace=True, weights='Multiplier', random_state=seed).copy()
    
    # Generate unique synthetic agent IDs (deterministic or UUID, UUID used for guaranteed global uniqueness)
    # To make it deterministic for tests based on seed/index, we can use a seeded generator or standard uuid4
    # We will use uuid4 to guarantee uniqueness across distributed runs, but reproducibility is guaranteed 
    # by the exact same sample rows being chosen.
    np.random.seed(seed)
    # Deterministic pseudo-uuids to make exact reproducibility tests easy (same seed -> same uuids)
    def seeded_uuid(i):
        return str(uuid.UUID(bytes=np.random.bytes(16)))
    
    sample_df['synthetic_agent_id'] = [seeded_uuid(i) for i in range(n_agents)]
    
    # Define required output columns
    output_cols = [
        'synthetic_agent_id',
        'source_hces_household_key',
        'state',
        'district',
        'sector',
        'household_size',
        'dwelling_type',
        'electricity_access',
        'free_electricity',
        'monthly_consumption_expenditure',
        'derived_mpce',
        'mpce_decile',
        'survey_weight'
    ]
    
    return sample_df[output_cols].reset_index(drop=True)

def compare_distributions(source_df, synthetic_df, col, weight_col='Multiplier'):
    """
    Compares the source weighted distribution with the synthetic unweighted distribution.
    Returns a dataframe with differences.
    """
    # Source weighted
    source_dist = (source_df.groupby(col)[weight_col].sum() / source_df[weight_col].sum()).rename('source_pct')
    
    # Synthetic unweighted (since it's a representative sample now)
    synth_dist = (synthetic_df.groupby(col).size() / len(synthetic_df)).rename('synthetic_pct')
    
    comp = pd.concat([source_dist, synth_dist], axis=1).fillna(0)
    comp['abs_diff'] = (comp['source_pct'] - comp['synthetic_pct']).abs()
    return comp

def run_diagnostics(source_df, synthetic_df):
    diagnostics = {}
    
    # 1. Duplicates
    vc = synthetic_df['source_hces_household_key'].value_counts()
    duplicates = vc[vc > 1]
    
    diagnostics['duplication'] = {
        'total_synthetic_agents': len(synthetic_df),
        'unique_source_households': len(vc),
        'duplicated_source_households': len(duplicates),
        'max_multiplicity': int(vc.max()) if len(vc) > 0 else 0,
        'pct_agents_from_duplicated': float(duplicates.sum() / len(synthetic_df)) if len(duplicates) > 0 else 0.0
    }
    
    # 2. Distributions
    cols_to_check = ['state', 'sector', 'household_size', 'dwelling_type', 'electricity_access', 'mpce_decile']
    dist_results = {}
    
    for col in cols_to_check:
        comp = compare_distributions(source_df, synthetic_df, col)
        max_diff = comp['abs_diff'].max()
        dist_results[col] = {
            'max_abs_diff': float(max_diff),
            'comparison_df': comp
        }
    
    diagnostics['distributions'] = dist_results
    return diagnostics

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[500])
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 100, 200, 300, 400])
    args = parser.parse_args()
    
    input_path = 'data/processed/households/hces_2023_24/hces_household_core.parquet'
    out_dir = 'data/processed/households/synthetic/'
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Loading {input_path}...")
    df = pd.read_parquet(input_path)
    
    # Construct source_hces_household_key
    df['source_hces_household_key'] = df['FSU_Serial_No'].astype(str) + '_' + \
                                      df['Second_Stage_Stratum_No'].astype(str) + '_' + \
                                      df['Sample_Household_No'].astype(str)
    
    # Map standard columns
    df['state'] = df['State']
    df['district'] = df['District']
    df['sector'] = df['Sector']
    df['household_size'] = df['HH_Size_FDQ']
    df['dwelling_type'] = df['Type_of_Dwelling_Unit']
    df['electricity_access'] = df['Energy_Source_Lighting']
    df['free_electricity'] = df['Free_electricity']
    df['monthly_consumption_expenditure'] = df['MONTHLY_CONSUMPTION_EXP']
    df['survey_weight'] = df['Multiplier']
    
    # Compute Deciles
    df['mpce_decile'] = compute_weighted_deciles(df)
    
    all_diagnostics = {}
    
    for size in args.sizes:
        for seed in args.seeds:
            print(f"Generating N={size} with seed={seed}...")
            synth = generate_synthetic_population(df, size, seed)
            
            # Run diagnostics
            diag = run_diagnostics(df, synth)
            
            # Save artifacts
            out_file = os.path.join(out_dir, f'population_{size}_seed_{seed}.parquet')
            meta_file = os.path.join(out_dir, f'population_{size}_seed_{seed}_metadata.json')
            
            synth.to_parquet(out_file, index=False)
            
            metadata = {
                'dataset_id': f'synthetic_{size}_{seed}',
                'dataset_version': '1.0',
                'source_hces_version': '2023_24_core',
                'sampling_method': 'survey-weighted empirical resampling',
                'sampling_weight_field': 'Multiplier',
                'population_size': size,
                'seed': seed,
                'generator_version': '1.0',
                'generation_timestamp': datetime.utcnow().isoformat(),
                'duplication_diagnostics': diag['duplication'],
                'max_distribution_diffs': {k: v['max_abs_diff'] for k,v in diag['distributions'].items()}
            }
            
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            all_diagnostics[f'{size}_{seed}'] = diag

    print("Generation complete.")
