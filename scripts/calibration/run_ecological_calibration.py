import os
import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.models.statistical.empirical_baseline import EmpiricalEcologicalBaseline
from schemas.data.calibration import TargetSpec, PreprocessingSpec, SerializedModelArtifact, CalibrationConfig

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))

def calculate_state_rates(X, w, beta, intercept, state_indices, num_states):
    """Calculate the predicted adoption rate for each state."""
    linear = np.dot(X, beta) + intercept
    p = sigmoid(linear)
    
    # Weighted sum of probabilities per state
    pred_counts = np.bincount(state_indices, weights=p * w, minlength=num_states)
    total_weights = np.bincount(state_indices, weights=w, minlength=num_states)
    
    # Avoid division by zero
    total_weights = np.where(total_weights == 0, 1e-9, total_weights)
    return pred_counts / total_weights

def rate_mse_loss(params, X, w, state_indices, num_states, true_rates):
    """Mean Squared Error between predicted state rates and true state rates."""
    beta = params[:-1]
    intercept = params[-1]
    
    pred_rates = calculate_state_rates(X, w, beta, intercept, state_indices, num_states)
    
    # Only compare states that we have true rates for (where true_rate >= 0)
    valid = true_rates >= 0
    return mean_squared_error(true_rates[valid], pred_rates[valid])

def run_calibration():
    # 0. Target Audit and Data Loading
    print("Loading datasets...")
    hces_path = 'data/processed/households/hces_2023_24/hces_household_core.parquet'
    pm_path = 'data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv'
    cea_path = 'data/processed/energy/cea_domestic_consumers.csv' # Extract from 4D.11A
    
    hces_df = pd.read_parquet(hces_path)
    pm_df = pd.read_csv(pm_path)
    
    # If CEA path exists, load it, otherwise we fall back (with a warning)
    if os.path.exists(cea_path):
        cea_df = pd.read_csv(cea_path)
    else:
        # Fallback to HCES Expansion
        print("WARNING: CEA domestic consumers CSV not found. Utilizing HCES Multiplier sum as denominator fallback.")
        cea_df = hces_df.groupby('state')['survey_weight'].sum().reset_index()
        cea_df.columns = ['state', 'domestic_consumers_mar2024']

    # Merge Targets
    # PM Surya Ghar Installations
    target_df = pm_df[['state', 'installations']].copy()
    target_df['installations'] = target_df['installations'].astype(float)
    
    # Merge Denominator
    target_df = target_df.merge(cea_df, on='state', how='inner')
    target_df['observed_rate'] = target_df['installations'] / target_df['domestic_consumers_mar2024']
    
    # Map HCES columns
    # Standard Census 2011 State Codes mapping (used by HCES)
    state_code_map = {
        '01': 'Jammu & Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab', '04': 'Chandigarh',
        '05': 'Uttarakhand', '06': 'Haryana', '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
        '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh', '13': 'Nagaland', '14': 'Manipur',
        '15': 'Mizoram', '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam', '19': 'West Bengal',
        '20': 'Jharkhand', '21': 'Odisha', '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
        '25': 'Dadra & Nagar Haveli and Daman & Diu', '26': 'Dadra & Nagar Haveli and Daman & Diu',
        '27': 'Maharashtra', '28': 'Andhra Pradesh', '29': 'Karnataka', '30': 'Goa',
        '31': 'Lakshadweep', '32': 'Kerala', '33': 'Tamil Nadu', '34': 'Puducherry',
        '35': 'Andaman & Nicobar Islands', '36': 'Telangana', '37': 'Ladakh'
    }
    # Convert numerical code (which might be int or string) to padded 2-digit string
    hces_df['state'] = hces_df['State'].astype(str).str.zfill(2).map(state_code_map)
    hces_df['sector'] = hces_df['Sector']
    hces_df['household_size'] = hces_df['HH_Size_FDQ']
    hces_df['dwelling_type'] = hces_df['Type_of_Dwelling_Unit']
    hces_df['electricity_access'] = hces_df['Energy_Source_Lighting']
    hces_df['free_electricity'] = hces_df['Free_electricity']
    hces_df['derived_mpce'] = hces_df['MONTHLY_CONSUMPTION_EXP'] / hces_df['HH_Size_FDQ']
    hces_df['survey_weight'] = hces_df['Multiplier']
    
    # Create canonical target mapping
    # Clean state strings for perfect matching
    hces_df['state_clean'] = hces_df['state'].str.strip().str.lower()
    target_df['state_clean'] = target_df['state'].str.strip().str.lower()
    
    # Filter HCES to states we have targets for
    valid_states = set(target_df['state_clean'])
    hces_train = hces_df[hces_df['state_clean'].isin(valid_states)].copy()
    
    # Prepare Features
    config = CalibrationConfig()
    
    X_raw = hces_train[config.features].copy()
    model = EmpiricalEcologicalBaseline()
    X_proc = model._preprocess(X_raw)
    
    # State mapping to integer indices for fast bincount
    state_names = sorted(list(valid_states))
    state_to_idx = {s: i for i, s in enumerate(state_names)}
    hces_train['state_idx'] = hces_train['state_clean'].map(state_to_idx)
    
    true_rates = np.zeros(len(state_names))
    for i, s in enumerate(state_names):
        true_rates[i] = target_df[target_df['state_clean'] == s]['observed_rate'].values[0]
        
    X_vals = X_proc.values
    w_vals = hces_train[config.weight_column].values
    state_idx_vals = hces_train['state_idx'].values
    
    print("Fitting Ecological Propensity Model (Pooled)...")
    np.random.seed(config.seed)
    # Initialize near zero
    init_params = np.random.randn(X_proc.shape[1] + 1) * 0.01
    # Bias the intercept heavily negative since adoption rates are very low (e.g., 0.01)
    init_params[-1] = -5.0 
    
    res = minimize(
        rate_mse_loss, 
        init_params, 
        args=(X_vals, w_vals, state_idx_vals, len(state_names), true_rates),
        method='L-BFGS-B',
        options={'maxiter': 100, 'disp': False}
    )
    
    print(f"Optimization Success: {res.success}")
    
    # Assign back to model
    model.coefficients = {col: res.x[i] for i, col in enumerate(X_proc.columns)}
    model.intercept = res.x[-1]
    model.feature_order = list(X_proc.columns)
    model.is_fitted = True
    
    # Model A: State Penetration Baseline (Mean Rate)
    mean_rate = true_rates.mean()
    model_a_pred = np.full(len(state_names), mean_rate)
    mae_a = mean_absolute_error(true_rates, model_a_pred)
    
    # Model B: Pooled Household Propensity
    model_b_pred = calculate_state_rates(X_vals, w_vals, res.x[:-1], res.x[-1], state_idx_vals, len(state_names))
    mae_b = mean_absolute_error(true_rates, model_b_pred)
    
    print(f"Model A (Mean) MAE: {mae_a:.6f}")
    print(f"Model B (Propensity) MAE: {mae_b:.6f}")
    
    # Geographic Holdout (Leave One State Out)
    print("Running Geographic Holdout (LOSO)...")
    loso_preds = np.zeros(len(state_names))
    
    for holdout_idx in range(min(3, len(state_names))):
        # Mask out true rate
        masked_true_rates = true_rates.copy()
        masked_true_rates[holdout_idx] = -1.0 # Will be ignored in loss
        
        res_loso = minimize(
            rate_mse_loss, 
            init_params, 
            args=(X_vals, w_vals, state_idx_vals, len(state_names), masked_true_rates),
            method='L-BFGS-B',
            options={'maxiter': 50} # Fast for LOSO
        )
        
        # Predict for holdout
        pred = calculate_state_rates(X_vals, w_vals, res_loso.x[:-1], res_loso.x[-1], state_idx_vals, len(state_names))
        loso_preds[holdout_idx] = pred[holdout_idx]
        
    mae_loso = mean_absolute_error(true_rates, loso_preds)
    print(f"Geographic Holdout MAE: {mae_loso:.6f}")
    
    # Save Model
    target_spec = TargetSpec(
        numerator_metric="installations",
        numerator_reference_date="27.07.2024",
        denominator_metric="domestic_consumers_mar2024",
        denominator_reference_date="31.03.2024"
    )
    prep_spec = PreprocessingSpec(log_transform_mpce=True)
    
    artifact = SerializedModelArtifact(
        target=target_spec,
        preprocessing=prep_spec,
        coefficients=model.coefficients,
        intercept=model.intercept,
        feature_order=model.feature_order,
        calibration_seed=config.seed,
        training_states=state_names
    )
    
    out_dir = 'outputs/calibration/selected_model'
    model.save(f'{out_dir}/empirical_baseline.json', artifact)
    print(f"Model saved to {out_dir}/empirical_baseline.json")
    
if __name__ == "__main__":
    run_calibration()
