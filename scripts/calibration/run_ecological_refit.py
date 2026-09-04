import json
import os
import hashlib
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from src.models.statistical.empirical_baseline import EmpiricalEcologicalBaseline

def get_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def validate_inputs(target_path):
    print("Validating inputs...")
    assert os.path.basename(target_path) == "pm_surya_ghar_state_penetration_corrected.json", "Invalid target file name"
    
    with open(target_path, 'r') as f:
        target_data = json.load(f)
        
    df = pd.DataFrame(target_data)
    
    # 36 states check
    assert len(df) == 36, f"Expected 36 states, got {len(df)}"
    
    # Numerator provenance
    assert all(df['numerator_reference_date'] == "27.07.2026"), "Numerator date must be 27.07.2026"
    assert all(df['denominator_reference_date'] == "31.03.2024"), "Denominator date must be 31.03.2024"
    
    # No HCES fallback (we ensure this by checking if contributing_utilities exists)
    assert 'contributing_utilities' in df.columns, "Missing CEA utility counts"
    assert df['domestic_consumers'].notna().all(), "Missing domestic consumers"
    
    # Bounds check
    assert (df['observed_rate'] >= 0).all() and (df['observed_rate'] <= 1).all(), "Rates out of bounds"
    
    print("Input validation passed.")
    return df

def rate_mse_loss(beta, X_mat, weights, state_indices, true_rates, n_states):
    # Vectorized computation
    logits = X_mat.dot(beta)
    probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
    
    weighted_probs = probs * weights
    
    # Aggregate by state
    state_predicted_sums = np.bincount(state_indices, weights=weighted_probs, minlength=n_states)
    state_weight_sums = np.bincount(state_indices, weights=weights, minlength=n_states)
    
    # Avoid div zero
    state_pred_rates = state_predicted_sums / np.maximum(state_weight_sums, 1e-9)
    
    # Ignore states where true_rate is -1 (held out)
    mask = true_rates >= 0
    diff = state_pred_rates[mask] - true_rates[mask]
    return np.mean(diff ** 2)

def run_refit():
    target_path = 'outputs/calibration/target/pm_surya_ghar_state_penetration_corrected.json'
    target_df = validate_inputs(target_path)
    
    # Load HCES
    hces_path = 'data/processed/households/hces_2023_24/hces_household_core.parquet'
    hces_df = pd.read_parquet(hces_path)
    
    # Map target strings to state codes if necessary, or just lowercase matching
    target_df['state_lower'] = target_df['state'].str.lower()
    
    # HCES states are numeric (Census codes). We need a mapping to strings to match `target_df`.
    # Borrow mapping from previous Phase 4D.12
    state_code_map = {
        28: 'andhra pradesh', 12: 'arunachal pradesh', 18: 'assam', 10: 'bihar', 22: 'chhattisgarh',
        30: 'goa', 24: 'gujarat', 6: 'haryana', 2: 'himachal pradesh', 20: 'jharkhand',
        29: 'karnataka', 32: 'kerala', 23: 'madhya pradesh', 27: 'maharashtra', 14: 'manipur',
        17: 'meghalaya', 15: 'mizoram', 13: 'nagaland', 21: 'odisha', 3: 'punjab',
        8: 'rajasthan', 11: 'sikkim', 33: 'tamil nadu', 36: 'telangana', 16: 'tripura',
        9: 'uttar pradesh', 5: 'uttarakhand', 19: 'west bengal', 35: 'andaman & nicobar islands',
        4: 'chandigarh', 26: 'dadra & nagar haveli and daman & diu', 7: 'delhi',
        1: 'jammu & kashmir', 37: 'ladakh', 31: 'lakshadweep', 34: 'puducherry'
    }
    
    hces_df['state_lower'] = hces_df['State'].map(state_code_map)
    # Filter HCES to states in target_df
    hces_df = hces_df[hces_df['state_lower'].isin(target_df['state_lower'])].copy()
    
    hces_df.rename(columns={
        'Sector': 'sector',
        'Type_of_Dwelling_Unit': 'dwelling_type',
        'Energy_Source_Lighting': 'electricity_access',
        'Free_electricity': 'free_electricity',
        'HH_Size_FDQ': 'household_size'
    }, inplace=True)
    
    # Set up baseline model for preprocessing
    model = EmpiricalEcologicalBaseline()
    
    features = ['derived_mpce', 'household_size', 'sector', 'dwelling_type', 'electricity_access', 'free_electricity']
    X_raw = hces_df[features].copy()
    
    # Enforce exclusion
    for col in ['home_owner', 'system_size_kw', 'survey_weight']:
        if col in X_raw.columns:
            X_raw.drop(columns=[col], inplace=True)
            
    X_proc = model._preprocess(X_raw)
    feature_order = list(X_proc.columns)
    
    X_mat = X_proc.values
    weights = hces_df['Multiplier'].values
    
    # Create integer state indices
    unique_states = sorted(hces_df['state_lower'].unique())
    state_to_idx = {s: i for i, s in enumerate(unique_states)}
    state_indices = hces_df['state_lower'].map(state_to_idx).values
    n_states = len(unique_states)
    
    # Align true rates
    target_dict = target_df.set_index('state_lower')['observed_rate'].to_dict()
    true_rates = np.array([target_dict[s] for s in unique_states])
    
    # Model A: National Mean (In-sample)
    national_mean = target_df['installations'].sum() / target_df['domestic_consumers'].sum()
    pred_a = np.full(n_states, national_mean)
    mae_a = np.mean(np.abs(pred_a - true_rates))
    rmse_a = np.sqrt(np.mean((pred_a - true_rates)**2))
    
    print(f"Model A (Mean) MAE: {mae_a:.6f}, RMSE: {rmse_a:.6f}")
    
    # Model A: LOSO
    pred_a_loso = np.zeros(n_states)
    for i, s in enumerate(unique_states):
        # Hold out state s
        mask = target_df['state_lower'] != s
        subset = target_df[mask]
        loso_mean = subset['installations'].sum() / subset['domestic_consumers'].sum()
        pred_a_loso[i] = loso_mean
        
    mae_a_loso = np.mean(np.abs(pred_a_loso - true_rates))
    rmse_a_loso = np.sqrt(np.mean((pred_a_loso - true_rates)**2))
    print(f"Model A (LOSO) MAE: {mae_a_loso:.6f}, RMSE: {rmse_a_loso:.6f}")
    
    # Model B: Pooled Fit (In-sample)
    init_beta = np.zeros(X_mat.shape[1])
    init_beta[0] = -5.0 # Intercept-like shift if needed, actually we don't have an explicit intercept unless added.
    # EmpiricalEcologicalBaseline does not add an intercept implicitly in _preprocess, let's check
    if 'intercept' not in X_proc.columns:
        X_mat = np.hstack([np.ones((X_mat.shape[0], 1)), X_mat])
        feature_order = ['intercept'] + feature_order
        init_beta = np.zeros(X_mat.shape[1])
        init_beta[0] = -4.0
    
    res = minimize(
        rate_mse_loss,
        init_beta,
        args=(X_mat, weights, state_indices, true_rates, n_states),
        method='L-BFGS-B',
        bounds=[(-10, 10)] * X_mat.shape[1]
    )
    
    beta_opt = res.x
    
    # Predict in-sample
    logits = X_mat.dot(beta_opt)
    probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
    state_predicted_sums = np.bincount(state_indices, weights=probs * weights, minlength=n_states)
    state_weight_sums = np.bincount(state_indices, weights=weights, minlength=n_states)
    pred_b_insample = state_predicted_sums / np.maximum(state_weight_sums, 1e-9)
    
    mae_b_in = np.mean(np.abs(pred_b_insample - true_rates))
    rmse_b_in = np.sqrt(np.mean((pred_b_insample - true_rates)**2))
    
    print(f"Model B (In-sample) MAE: {mae_b_in:.6f}, RMSE: {rmse_b_in:.6f}")
    
    # LOSO CV
    print("Running LOSO CV...")
    loso_preds = np.zeros(n_states)
    
    for holdout_idx in range(n_states):
        masked_rates = true_rates.copy()
        masked_rates[holdout_idx] = -1.0 # exclude from loss
        
        loso_res = minimize(
            rate_mse_loss,
            init_beta,
            args=(X_mat, weights, state_indices, masked_rates, n_states),
            method='L-BFGS-B',
            bounds=[(-10, 10)] * X_mat.shape[1]
        )
        
        # Predict holdout
        loso_beta = loso_res.x
        logits_loso = X_mat.dot(loso_beta)
        probs_loso = 1.0 / (1.0 + np.exp(-np.clip(logits_loso, -20, 20)))
        
        # Only compute for the holdout state
        mask_h = (state_indices == holdout_idx)
        w_h = weights[mask_h]
        p_h = probs_loso[mask_h]
        
        if np.sum(w_h) > 0:
            loso_preds[holdout_idx] = np.sum(p_h * w_h) / np.sum(w_h)
        else:
            loso_preds[holdout_idx] = 0.0

    mae_b_loso = np.mean(np.abs(loso_preds - true_rates))
    rmse_b_loso = np.sqrt(np.mean((loso_preds - true_rates)**2))
    
    print(f"Model B (LOSO) MAE: {mae_b_loso:.6f}, RMSE: {rmse_b_loso:.6f}")
    
    # Save Refit Candidate
    out_dir = 'outputs/calibration/refit_candidate'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. empirical_baseline_refit.json
    coef_dict = {feat: float(val) for feat, val in zip(feature_order, beta_opt)}
    intercept = coef_dict.pop('intercept', 0.0)
    
    model.is_fitted = True
    model.coefficients = coef_dict
    model.intercept = intercept
    model.feature_order = [f for f in feature_order if f != 'intercept']
    
    from schemas.data.calibration import SerializedModelArtifact, TargetSpec, PreprocessingSpec
    target_spec = TargetSpec(
        target_name="PM_Surya_Ghar_State_Penetration",
        numerator_metric="installations",
        numerator_reference_date="27.07.2026",
        denominator_metric="cea_domestic_consumers_mar2024",
        denominator_reference_date="31.03.2024",
        geography="State/UT",
        programme_scope="PM Surya Ghar"
    )
    prep_spec = PreprocessingSpec(
        version="1.1",
        log_transform_mpce=True,
        mpce_clip_lower=1.0,
        categorical_encoding="one-hot-drop-first"
    )
    
    artifact = SerializedModelArtifact(
        target=target_spec,
        preprocessing=prep_spec,
        coefficients=model.coefficients,
        intercept=model.intercept,
        feature_order=model.feature_order,
        calibration_seed=42,
        training_states=unique_states
    )
    
    candidate_model_path = os.path.join(out_dir, 'empirical_baseline_refit.json')
    model.save(candidate_model_path, artifact)
    
    # 2. model_comparison.json
    comp = {
        "model_A": {"in_sample_mae": mae_a, "in_sample_rmse": rmse_a, "loso_mae": mae_a_loso, "loso_rmse": rmse_a_loso},
        "model_B": {"in_sample_mae": mae_b_in, "in_sample_rmse": rmse_b_in, "loso_mae": mae_b_loso, "loso_rmse": rmse_b_loso}
    }
    with open(os.path.join(out_dir, 'model_comparison.json'), 'w') as f:
        json.dump(comp, f, indent=2)
        
    # 3. loso_predictions.csv
    loso_df = pd.DataFrame({
        'state': unique_states,
        'observed_rate': true_rates,
        'pred_rate_in_sample': pred_b_insample,
        'pred_rate_loso': loso_preds
    })
    loso_df.to_csv(os.path.join(out_dir, 'loso_predictions.csv'), index=False)
    
    # Promote to selected model
    final_path = 'outputs/calibration/selected_model/empirical_baseline.json'
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    model.save(final_path, artifact)
    
    # Manifest
    manifest = {
        "refit_timestamp": pd.Timestamp.now().isoformat(),
        "final_artifact_sha256": get_sha256(final_path),
        "target_file": target_path
    }
    with open(os.path.join(out_dir, 'refit_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print("Refit complete and promoted.")

if __name__ == '__main__':
    run_refit()
