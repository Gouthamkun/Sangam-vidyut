import pandas as pd
import sys

def test_case(phase, subsidy, topology, beta, p_base_mode, policy_mode=None):
    print(f"--- CASE: Phase={phase}, Subsidy={subsidy}, Topology={topology}, Beta={beta}, Household={p_base_mode}, Policy={policy_mode} ---")
    
    if phase == "Phase 4F.2":
        df2 = pd.read_csv("outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv")
        subset = df2[(df2["subsidy"] == subsidy) & 
                     (df2["topology"] == topology) & 
                     (df2["beta"] == beta) & 
                     (df2["p_base_mode"] == p_base_mode) &
                     (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
        print(f"Rows returned: len={len(subset)}")
        if not subset.empty:
            print(f"Mean Final Adoption: {subset['mean_adoption_pct'].iloc[0]*100}%")
            print(f"Min Adoption: {subset['min_adoption_pct'].iloc[0]*100}%")
            print(f"Max Adoption: {subset['max_adoption_pct'].iloc[0]*100}%")
        else:
            print("No data.")
    elif phase == "Phase 4F.3":
        # Load trajectory
        is_dynamic = (policy_mode == "dynamic")
        dyn_str = "True" if is_dynamic else "False"
        path = f"outputs/experiments/phase_4f_3/raw/R3_DET_{float(subsidy)}_{dyn_str}_{topology}_42_trajectory.csv"
        try:
            traj = pd.read_csv(path)
            print(f"Rows returned: len={len(traj)}")
            final_row = traj.iloc[-1]
            print(f"Final Adoption Count: {final_row['adoption_count']}")
            print(f"Total Expenditure: {1000000 - final_row['budget_remaining']}")
        except FileNotFoundError:
            print(f"No data. File not found: {path}")

# CASE A
test_case("Phase 4F.2", 0, "watts_strogatz", 0.05, "empirical")
# CASE B
test_case("Phase 4F.2", 3000, "watts_strogatz", 0.05, "empirical")
# CASE C
test_case("Phase 4F.2", 3000, "barabasi_albert", 0.05, "empirical")
# CASE D
test_case("Phase 4F.2", 3000, "watts_strogatz", 0.30, "empirical")
# CASE E
test_case("Phase 4F.2", 3000, "watts_strogatz", 0.15, "constant")
# CASE F
test_case("Phase 4F.3", 3000, "watts_strogatz", None, None, "fixed")
# CASE G
test_case("Phase 4F.3", 3000, "watts_strogatz", None, None, "dynamic")

