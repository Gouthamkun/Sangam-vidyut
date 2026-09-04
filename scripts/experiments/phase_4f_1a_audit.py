import os
import pandas as pd
import hashlib

OUT_DIR = "outputs/experiments/phase_4f_1"

def get_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    # 1. EXACT RUN ACCOUNTING
    raw_file = f"{OUT_DIR}/raw/experiment_results.csv"
    
    if os.path.exists(raw_file):
        df = pd.read_csv(raw_file)
        runs_found = len(df)
    else:
        runs_found = 0
        
    print(f"Discrepancy Check: The status report claimed 180 completed runs, but {runs_found} runs were found in {OUT_DIR}/raw/.")
    
    # 9. CLAIM-EVIDENCE MATRIX
    claims = [
        {"claim": "Q1 network ABM differs from static", "experiment_family": "Static vs ABM", "condition": "Matched", "n": runs_found, "metric": "Final Adoption Diff", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Differences could not be observed due to missing raw data (0 runs completed)."},
        {"claim": "Q2 BA vs WS", "experiment_family": "Topology Effect", "condition": "BA vs WS", "n": runs_found, "metric": "Tipping Quarter Diff", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Topological effects could not be verified due to missing raw data."},
        {"claim": "Q3 beta effect", "experiment_family": "Beta Effect", "condition": "0.05, 0.15, 0.30", "n": runs_found, "metric": "Tipping Frequency", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Beta effects could not be verified due to missing raw data."},
        {"claim": "Q4 heterogeneity effect", "experiment_family": "Heterogeneity Ablation", "condition": "Empirical vs Constant", "n": runs_found, "metric": "Early Adoption", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Heterogeneity impact could not be verified due to missing raw data."},
        {"claim": "Q5 subsidy effect", "experiment_family": "Subsidy Effect", "condition": "0, 1000, 5000", "n": runs_found, "metric": "Final Adoption Delta", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Subsidy response non-linearity could not be verified due to missing raw data."},
        {"claim": "Q6 cognitive effect", "experiment_family": "Cognitive Ablation", "condition": "MockLLM vs Deterministic", "n": runs_found, "metric": "Final Adoption", "observed_value": "None", "evidence_status": "NOT_SUPPORTED", "recommended_wording": "Cognitive alignment could not be verified due to missing raw data."}
    ]
    
    df_claims = pd.DataFrame(claims)
    os.makedirs(f"{OUT_DIR}/tables", exist_ok=True)
    df_claims.to_csv(f"{OUT_DIR}/tables/claim_evidence_audit.csv", index=False)
    
    # 11. ADD A RESULTS TABLE
    results_table = [
        {"question": "Q1", "comparison": "Static vs ABM", "condition": "Matched", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"},
        {"question": "Q2", "comparison": "BA vs WS", "condition": "Matched Beta", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"},
        {"question": "Q3", "comparison": "Beta levels", "condition": "WS/BA", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"},
        {"question": "Q4", "comparison": "Empirical vs Constant", "condition": "Matched", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"},
        {"question": "Q5", "comparison": "0 vs 1000 vs 5000", "condition": "Matched", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"},
        {"question": "Q6", "comparison": "Deterministic vs Cognitive", "condition": "MockLLM", "n": runs_found, "mean_effect": "None", "SD": "None", "effect_size": "None", "tipping_frequency": "None", "interpretation": "Unverified"}
    ]
    
    df_results = pd.DataFrame(results_table)
    df_results.to_csv(f"{OUT_DIR}/tables/main_results_table.csv", index=False)
    
    # Hash check
    sha = get_hash("outputs/calibration/selected_model/empirical_baseline.json")
    print(f"Artifact SHA-256: {sha}")

if __name__ == "__main__":
    main()
