import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

OUT_DIR = "docs/figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Common styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'

# Helpers for drawing boxes
def draw_box(ax, x, y, width, height, text, color="lightblue"):
    box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1", 
                         ec="black", fc=color, mutation_scale=0.5)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha="center", va="center", fontsize=9, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, text=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    if text:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y, text, ha="center", va="bottom", fontsize=8)


def fig1_architecture():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('off')
    
    draw_box(ax, 0.1, 0.8, 0.3, 0.15, "Indian Empirical Data\n(HCES 2023-24)", "lightgreen")
    draw_box(ax, 0.1, 0.5, 0.3, 0.15, "Synthetic Households\n(ConsumerAgents)", "skyblue")
    draw_box(ax, 0.6, 0.5, 0.3, 0.15, "Social Network\n(SIR Diffusion)", "skyblue")
    draw_box(ax, 0.35, 0.2, 0.3, 0.15, "Macro Feedback\n(Gov / Industry / Env)", "lightcoral")
    draw_box(ax, 0.1, 0.2, 0.2, 0.1, "LLM Cognitive\nLayer (Optional)", "plum")
    
    draw_arrow(ax, 0.25, 0.8, 0.25, 0.65, "Calibration")
    draw_arrow(ax, 0.4, 0.575, 0.6, 0.575, "Adoption State")
    draw_arrow(ax, 0.6, 0.5, 0.4, 0.5, "Network Exposure")
    
    draw_arrow(ax, 0.25, 0.5, 0.4, 0.35, "Aggregate Demand")
    draw_arrow(ax, 0.5, 0.35, 0.65, 0.5, "Price & Subsidy Updates")
    
    draw_arrow(ax, 0.25, 0.5, 0.2, 0.3, "Ambiguity")
    draw_arrow(ax, 0.2, 0.3, 0.25, 0.5, "Decision")
    
    plt.title("Figure 1: Sangam Vidyut System Architecture", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_01_architecture.png", dpi=300)
    plt.close()

def fig2_calibration():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    
    draw_box(ax, 0.05, 0.6, 0.2, 0.15, "HCES 2023-24\nHousehold Records", "lightgray")
    draw_box(ax, 0.35, 0.6, 0.25, 0.15, "Synthetic Population\n(Weighted Generation)", "lightblue")
    draw_box(ax, 0.7, 0.6, 0.25, 0.15, "Empirical Baseline\nPropensity (p_base)", "lightgreen")
    
    draw_box(ax, 0.05, 0.2, 0.2, 0.15, "PM Surya Ghar /\nMNRE Data", "lightgray")
    draw_box(ax, 0.35, 0.2, 0.25, 0.15, "CEA Denominator\nConstraints", "lightblue")
    draw_box(ax, 0.7, 0.2, 0.25, 0.15, "Ecological\nCalibration Target", "lightcoral")
    
    draw_arrow(ax, 0.25, 0.675, 0.35, 0.675)
    draw_arrow(ax, 0.6, 0.675, 0.7, 0.675)
    
    draw_arrow(ax, 0.25, 0.275, 0.35, 0.275)
    draw_arrow(ax, 0.6, 0.275, 0.7, 0.275)
    
    draw_arrow(ax, 0.825, 0.35, 0.825, 0.6, "Fitted to Matches")
    
    plt.title("Figure 2: Aggregate-Consistent Ecological Calibration Pipeline", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_02_calibration.png", dpi=300)
    plt.close()

def fig3_decision():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('off')
    
    draw_box(ax, 0.35, 0.8, 0.3, 0.1, "score = 0.4*p_base + 0.4*SIR + 0.2*aff", "lightyellow")
    
    draw_box(ax, 0.1, 0.5, 0.2, 0.1, "score >= 0.20\n(Deterministic Adopt)", "lightgreen")
    draw_box(ax, 0.4, 0.5, 0.2, 0.1, "Ambiguity Zone\n(0.05 - 0.20)", "peachpuff")
    draw_box(ax, 0.7, 0.5, 0.2, 0.1, "score <= 0.05\n(Deterministic Wait)", "lightcoral")
    
    draw_box(ax, 0.4, 0.2, 0.2, 0.1, "LLM Cognitive\nRouting", "plum")
    
    draw_arrow(ax, 0.5, 0.8, 0.2, 0.6)
    draw_arrow(ax, 0.5, 0.8, 0.5, 0.6)
    draw_arrow(ax, 0.5, 0.8, 0.8, 0.6)
    
    draw_arrow(ax, 0.5, 0.5, 0.5, 0.3)
    
    plt.title("Figure 3: Household Decision Mechanism", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_03_household_decision.png", dpi=300)
    plt.close()

def fig4_subsidy_response():
    try:
        df = pd.read_csv("outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv")
        df_det = df[df['model_class'] == "DETERMINISTIC_EMPIRICAL_ABM"]
        df_det = df_det.copy()
        
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df_det, x="subsidy", y="mean_adoption_pct", marker="o", color="blue")
        plt.axvspan(0, 2000, color='red', alpha=0.1, label='Blocked Regime')
        plt.axvspan(2000, 3000, color='orange', alpha=0.1, label='Diffusion-Active')
        plt.axvspan(3000, 5000, color='green', alpha=0.1, label='Saturated')
        plt.xlabel("Government Subsidy")
        plt.ylabel("Mean Adoption (%)")
        plt.title("Figure 4: Subsidy Response Curve (N=500)", fontweight="bold")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_04_subsidy_response.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 4:", e)

def fig5_activation():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    
    draw_box(ax, 0.05, 0.4, 0.25, 0.2, "AFFORDABILITY-BLOCKED\n(Subsidy < 2000)\nNo adoption possible", "lightcoral")
    draw_box(ax, 0.375, 0.4, 0.25, 0.2, "DIFFUSION-ACTIVE\n(Subsidy 2000-3000)\nNetwork effects dominate", "gold")
    draw_box(ax, 0.7, 0.4, 0.25, 0.2, "SATURATED\n(Subsidy > 4000)\nUniversally affordable", "lightgreen")
    
    draw_arrow(ax, 0.3, 0.5, 0.375, 0.5)
    draw_arrow(ax, 0.625, 0.5, 0.7, 0.5)
    
    plt.title("Figure 5: Observed Mechanism Activation Regimes", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_05_mechanism_activation.png", dpi=300)
    plt.close()

def fig6_topology():
    try:
        df = pd.read_csv("outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv")
        df_det = df[df['model_class'] == "DETERMINISTIC_EMPIRICAL_ABM"]
        df_det = df_det.copy()
        
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df_det, x="subsidy", y="mean_adoption_pct", hue="topology", capsize=0.1)
        plt.xlabel("Government Subsidy")
        plt.ylabel("Mean Adoption (%)")
        plt.title("Figure 6: Conditional Topology Effect (BA vs WS)", fontweight="bold")
        plt.legend(title="Topology")
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_06_topology.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 6:", e)

def fig7_beta():
    try:
        df = pd.read_csv("outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv")
        df_det = df[df['model_class'] == "DETERMINISTIC_EMPIRICAL_ABM"]
        df_det = df_det.copy()
        
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df_det, x="subsidy", y="mean_adoption_pct", hue="beta", palette="flare", marker="o")
        plt.xlabel("Government Subsidy")
        plt.ylabel("Mean Adoption (%)")
        plt.title("Figure 7: Contagion Rate (Beta) Sensitivity", fontweight="bold")
        plt.legend(title="Beta")
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_07_beta.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 7:", e)

def fig8_heterogeneity():
    try:
        df = pd.read_csv("outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv")
        df_ws = df[(df['topology'] == 'watts_strogatz') & (df['beta'] == 0.15)]
        df_ws = df_ws.copy()
        
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df_ws, x="subsidy", y="mean_adoption_pct", hue="p_base_mode", marker="o")
        plt.xlabel("Government Subsidy")
        plt.ylabel("Mean Adoption (%)")
        plt.title("Figure 8: Household Heterogeneity Impact", fontweight="bold")
        plt.legend(title="p_base Distribution")
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_08_heterogeneity.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 8:", e)

def fig9_policy():
    try:
        # We will plot from one matched set of trajectories
        import glob
        traj_dir = "outputs/experiments/phase_4f_3/raw/"
        # Find one fixed and one dynamic at subsidy 3000
        fx = pd.read_csv(f"{traj_dir}R3_DET_3000.0_False_watts_strogatz_42_trajectory.csv")
        dy = pd.read_csv(f"{traj_dir}R3_DET_3000.0_True_watts_strogatz_42_trajectory.csv")
        
        fx['Policy'] = "Fixed Subsidy"
        dy['Policy'] = "Dynamic Target-Seeking"
        
        comb = pd.concat([fx, dy])
        
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=comb, x="quarter", y="adoption_count", hue="Policy")
        plt.axhline(250, color='red', linestyle='--', label='50% Target')
        plt.xlabel("Quarter")
        plt.ylabel("Adoption Count")
        plt.title("Figure 9: Fixed vs Target-Seeking Dynamic Policy (Subsidy 3000)", fontweight="bold")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_09_policy.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 9:", e)

def fig10_efficiency():
    try:
        df = pd.read_csv("outputs/experiments/phase_4f_3/tables/fixed_vs_dynamic.csv")
        
        plt.figure(figsize=(8, 5))
        # Plot mean policy efficiency
        sns.barplot(data=df, x="subsidy", y="eff_diff_mean", hue="topology")
        plt.xlabel("Government Subsidy Level")
        plt.ylabel("Difference in Efficiency (Dynamic - Fixed)")
        plt.title("Figure 10: Dynamic Policy Efficiency Gains vs Fixed Base", fontweight="bold")
        plt.legend(title="Topology")
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/figure_10_efficiency.png", dpi=300)
        plt.close()
    except Exception as e:
        print("Skipping fig 10:", e)

def fig11_budget_feedback():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Pathway A: ABM (Network Clustering)
    draw_box(ax, 0.05, 0.7, 0.25, 0.1, "Rapid Early Adoption\n(Network Clustering)", "lightcoral")
    draw_box(ax, 0.35, 0.7, 0.25, 0.1, "Fast Subsidy Burn\n(Budget Exhausts Early)", "lightcoral")
    draw_box(ax, 0.65, 0.7, 0.3, 0.1, "Subsidy Drops to Zero\n(Affordability Destroyed / Cascade Stalls)", "lightcoral")
    
    draw_arrow(ax, 0.3, 0.75, 0.35, 0.75)
    draw_arrow(ax, 0.6, 0.75, 0.65, 0.75)
    
    # Pathway B: Static (Budget Preservation)
    draw_box(ax, 0.05, 0.3, 0.25, 0.1, "Slow Early Adoption\n(No Network Physics)", "lightblue")
    draw_box(ax, 0.35, 0.3, 0.25, 0.1, "Budget Preserved\n(Industry Prices Fall)", "lightblue")
    draw_box(ax, 0.65, 0.3, 0.3, 0.1, "Delayed Mass Adoption\n(Universally Affordable Later)", "lightblue")
    
    draw_arrow(ax, 0.3, 0.35, 0.35, 0.35)
    draw_arrow(ax, 0.6, 0.35, 0.65, 0.35)
    
    plt.title("Figure 11: Budget Exhaustion Paradox (Observed Simulation Mechanism)", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_11_budget_feedback.png", dpi=300)
    plt.close()

def fig12_complete_feedback():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    draw_box(ax, 0.4, 0.8, 0.2, 0.1, "Government\nSubsidy Budget", "lightgreen")
    draw_box(ax, 0.1, 0.5, 0.2, 0.1, "Affordability", "lightblue")
    draw_box(ax, 0.4, 0.5, 0.2, 0.1, "Household Adoption", "orange")
    draw_box(ax, 0.7, 0.5, 0.2, 0.1, "Network Diffusion\n(SIR)", "plum")
    draw_box(ax, 0.4, 0.2, 0.2, 0.1, "Industry Price", "lightgray")
    draw_box(ax, 0.7, 0.2, 0.2, 0.1, "CO2 Emissions\nAverted", "lightgreen")
    
    draw_arrow(ax, 0.4, 0.85, 0.2, 0.6, "Depletes Budget")
    draw_arrow(ax, 0.5, 0.8, 0.5, 0.6, "Funds")
    draw_arrow(ax, 0.2, 0.5, 0.4, 0.55, "Enables")
    draw_arrow(ax, 0.6, 0.55, 0.7, 0.55, "Triggers")
    draw_arrow(ax, 0.7, 0.5, 0.6, 0.5, "Pressures")
    draw_arrow(ax, 0.5, 0.5, 0.5, 0.3, "Increases Demand")
    draw_arrow(ax, 0.4, 0.25, 0.2, 0.5, "Determines")
    draw_arrow(ax, 0.6, 0.5, 0.7, 0.3, "Calculates")
    
    plt.title("Figure 12: Complete System Feedback (Causal Loop Diagram)", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/figure_12_complete_feedback.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    fig1_architecture()
    fig2_calibration()
    fig3_decision()
    fig4_subsidy_response()
    fig5_activation()
    fig6_topology()
    fig7_beta()
    fig8_heterogeneity()
    fig9_policy()
    fig10_efficiency()
    fig11_budget_feedback()
    fig12_complete_feedback()
    print("Figures generated.")
