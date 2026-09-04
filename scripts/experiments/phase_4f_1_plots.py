import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

OUT_DIR = "outputs/experiments/phase_4f_1"

def generate_plots():
    df_sum = pd.read_csv(f"{OUT_DIR}/raw/experiment_results.csv")
    df_traj = pd.read_csv(f"{OUT_DIR}/raw/trajectory_results.csv")
    
    # Filter only baseline mode empirical unless stated
    df_emp = df_sum[df_sum['p_base_mode'] == 'empirical']
    df_traj_emp = df_traj[df_traj['p_base_mode'] == 'empirical']
    
    sns.set_theme(style="whitegrid")
    
    # 1. Adoption curves: WS vs BA (holding beta=0.15, subsidy=0, empirical)
    plt.figure(figsize=(10, 6))
    data = df_traj_emp[(df_traj_emp['beta'] == 0.15) & (df_traj_emp['subsidy'] == 0.0) & (df_traj_emp['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM')]
    sns.lineplot(data=data, x='quarter', y='adoption_rate', hue='topology', errorbar=('ci', 95))
    plt.title("Adoption Curves: Watts-Strogatz vs Barabási-Albert (Beta=0.15)")
    plt.savefig(f"{OUT_DIR}/plots/1_topology_comparison.png")
    plt.close()
    
    # 2. Adoption curves: beta = 0.05 vs 0.15 vs 0.30 (WS, subsidy=0, empirical)
    plt.figure(figsize=(10, 6))
    data = df_traj_emp[(df_traj_emp['topology'] == 'watts_strogatz') & (df_traj_emp['subsidy'] == 0.0) & (df_traj_emp['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM')]
    sns.lineplot(data=data, x='quarter', y='adoption_rate', hue='beta', palette='viridis', errorbar=('ci', 95))
    plt.title("Adoption Curves: Varying Social Diffusion (Beta)")
    plt.savefig(f"{OUT_DIR}/plots/2_beta_comparison.png")
    plt.close()
    
    # 3. Static vs deterministic ABM (WS, beta=0.15, subsidy=0)
    plt.figure(figsize=(10, 6))
    data_abm = df_traj_emp[(df_traj_emp['topology'] == 'watts_strogatz') & (df_traj_emp['beta'] == 0.15) & (df_traj_emp['subsidy'] == 0.0) & (df_traj_emp['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM')]
    data_static = df_traj_emp[(df_traj_emp['model_class'] == 'STATIC_BASELINE') & (df_traj_emp['subsidy'] == 0.0)]
    data = pd.concat([data_abm, data_static])
    sns.lineplot(data=data, x='quarter', y='adoption_rate', hue='model_class', errorbar=('ci', 95))
    plt.title("Static Baseline vs Networked Deterministic ABM")
    plt.savefig(f"{OUT_DIR}/plots/3_static_vs_abm.png")
    plt.close()
    
    # 4. Heterogeneous vs constant p_base (WS, beta=0.15, subsidy=0)
    plt.figure(figsize=(10, 6))
    data = df_traj[(df_traj['topology'] == 'watts_strogatz') & (df_traj['beta'] == 0.15) & (df_traj['subsidy'] == 0.0) & (df_traj['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM')]
    sns.lineplot(data=data, x='quarter', y='adoption_rate', hue='p_base_mode', errorbar=('ci', 95))
    plt.title("Heterogeneity Ablation: Empirical vs Constant p_base")
    plt.savefig(f"{OUT_DIR}/plots/4_heterogeneity_ablation.png")
    plt.close()
    
    # 5. Subsidy-response curve (WS, beta=0.15, deterministic vs static)
    plt.figure(figsize=(10, 6))
    data = df_sum[
        ((df_sum['topology'] == 'watts_strogatz') & (df_sum['beta'] == 0.15) & (df_sum['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM')) |
        (df_sum['model_class'] == 'STATIC_BASELINE')
    ]
    sns.barplot(data=data, x='subsidy', y='final_adoption', hue='model_class', errorbar=('ci', 95))
    plt.title("Final Adoption by Subsidy Level")
    plt.savefig(f"{OUT_DIR}/plots/5_subsidy_response.png")
    plt.close()
    
    # 6. Tipping/cascade frequency (ABM, Empirical, sub=0)
    plt.figure(figsize=(10, 6))
    data = df_sum[(df_sum['model_class'] == 'DETERMINISTIC_EMPIRICAL_ABM') & (df_sum['subsidy'] == 0.0) & (df_sum['p_base_mode'] == 'empirical')]
    cascade_freq = data.groupby(['topology', 'beta'])['tipping_occurred'].mean().reset_index()
    sns.barplot(data=cascade_freq, x='beta', y='tipping_occurred', hue='topology')
    plt.title("Tipping Point Frequency (Proportion of Runs)")
    plt.savefig(f"{OUT_DIR}/plots/6_tipping_frequency.png")
    plt.close()
    
    # 7. Deterministic vs cognitive ABM (WS, beta=0.15, subsidy=0)
    plt.figure(figsize=(10, 6))
    data = df_traj_emp[(df_traj_emp['topology'] == 'watts_strogatz') & (df_traj_emp['beta'] == 0.15) & (df_traj_emp['subsidy'] == 0.0)]
    data = data[data['model_class'].isin(['DETERMINISTIC_EMPIRICAL_ABM', 'HYBRID_COGNITIVE_ABM'])]
    sns.lineplot(data=data, x='quarter', y='adoption_rate', hue='model_class', errorbar=('ci', 95))
    plt.title("Deterministic vs Hybrid Cognitive ABM")
    plt.savefig(f"{OUT_DIR}/plots/7_deterministic_vs_cognitive.png")
    plt.close()

if __name__ == "__main__":
    generate_plots()
