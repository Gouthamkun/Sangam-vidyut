import os
import json
import pandas as pd
import numpy as np

OUT_DIR = "outputs/experiments/phase_4f_1_rerun"

def ensure_dirs():
    for d in ["raw", "aggregated", "plots", "manifests", "tables", "logs", "checkpoints"]:
        os.makedirs(os.path.join(OUT_DIR, d), exist_ok=True)

def analyze_results():
    ensure_dirs()
    
    # Read all summary JSONs
    records = []
    raw_dir = f"{OUT_DIR}/raw"
    if not os.path.exists(raw_dir):
        return {}
        
    for fn in os.listdir(raw_dir):
        if fn.endswith("_summary.json"):
            with open(os.path.join(raw_dir, fn), "r") as f:
                records.append(json.load(f))
    df = pd.DataFrame(records)
    if df.empty:
        return {}

    # Read all trajectories
    traj_dfs = []
    for fn in os.listdir(raw_dir):
        if fn.endswith("_trajectory.csv"):
            try:
                tdf = pd.read_csv(os.path.join(raw_dir, fn))
                traj_dfs.append(tdf)
            except Exception as e:
                print(f"Failed to read {fn}: {e}")
    if traj_dfs:
        tdf_all = pd.concat(traj_dfs, ignore_index=True)
        tdf_all.to_csv(f"{OUT_DIR}/aggregated/trajectory_results.csv", index=False)

    df.to_csv(f"{OUT_DIR}/aggregated/experiment_results.csv", index=False)

    # Heterogeneity
    het_df = df[(df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0)]
    het_df.to_csv(f"{OUT_DIR}/tables/heterogeneity_ablation.csv", index=False)

    # Policy
    pol_df = df[(df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["p_base_mode"] == "empirical")]
    pol_df.to_csv(f"{OUT_DIR}/tables/policy_results.csv", index=False)

    # Cognitive
    cog_df = df[df["model_class"] == "HYBRID_COGNITIVE_ABM"]
    cog_df.to_csv(f"{OUT_DIR}/tables/cognitive_results.csv", index=False)
    
    # Static vs ABM
    static = df[(df["model_class"] == "STATIC_BASELINE") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    abm = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz")]
    
    m_static = static["final_adoption"].mean()
    m_abm = abm["final_adoption"].mean()
    sd_abm = abm["final_adoption"].std()
    sd_static = static["final_adoption"].std()
    
    # Cohen's d roughly
    if pd.notnull(sd_abm) and pd.notnull(sd_static) and sd_abm > 0:
        d_static_abm = (m_abm - m_static) / np.sqrt((sd_abm**2 + sd_static**2)/2)
    else:
        d_static_abm = 0.0

    # Topology BA vs WS
    ba = df[(df["topology"] == "barabasi_albert") & (df["beta"] == 0.15) & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    ws = df[(df["topology"] == "watts_strogatz") & (df["beta"] == 0.15) & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    
    tip_ba = ba["tipping_quarter"].mean()
    tip_ws = ws["tipping_quarter"].mean()
    
    # Beta
    b05 = df[(df["beta"] == 0.05) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    b15 = ws
    b30 = df[(df["beta"] == 0.30) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    
    # Heterogeneity
    emp = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    con = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0) & (df["p_base_mode"] == "constant")]
    
    # Policy
    sub_0 = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 0) & (df["p_base_mode"] == "empirical")]
    sub_1000 = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 1000) & (df["p_base_mode"] == "empirical")]
    sub_5000 = df[(df["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM") & (df["beta"] == 0.15) & (df["topology"] == "watts_strogatz") & (df["subsidy"] == 5000) & (df["p_base_mode"] == "empirical")]
    
    # Cognitive
    cog = df[df["model_class"] == "HYBRID_COGNITIVE_ABM"]

    return {
        "n_total": len(df),
        "static_mean": m_static,
        "abm_mean": m_abm,
        "d_static_abm": d_static_abm,
        "tip_ba": tip_ba,
        "tip_ws": tip_ws,
        "tip_diff_ba_ws": tip_ws - tip_ba if tip_ws is not None and tip_ba is not None else None,
        "b05_mean": b05["final_adoption"].mean() if not b05.empty else None,
        "b15_mean": b15["final_adoption"].mean() if not b15.empty else None,
        "b30_mean": b30["final_adoption"].mean() if not b30.empty else None,
        "tip_b05": b05["tipping_quarter"].mean() if not b05.empty else None,
        "tip_b15": b15["tipping_quarter"].mean() if not b15.empty else None,
        "tip_b30": b30["tipping_quarter"].mean() if not b30.empty else None,
        "tip_diff_b15_b30": b15["tipping_quarter"].mean() - b30["tipping_quarter"].mean() if not b15.empty and not b30.empty else None,
        "emp_mean": emp["final_adoption"].mean() if not emp.empty else None,
        "con_mean": con["final_adoption"].mean() if not con.empty else None,
        "sub_0_mean": sub_0["final_adoption"].mean() if not sub_0.empty else None,
        "sub_1000_mean": sub_1000["final_adoption"].mean() if not sub_1000.empty else None,
        "sub_5000_mean": sub_5000["final_adoption"].mean() if not sub_5000.empty else None,
        "cog_calls": cog["total_llm_calls"].sum() if not cog.empty else None,
        "cog_mean": cog["final_adoption"].mean() if not cog.empty else None
    }

if __name__ == "__main__":
    res = analyze_results()
    for k, v in res.items():
        print(f"{k}: {v}")
