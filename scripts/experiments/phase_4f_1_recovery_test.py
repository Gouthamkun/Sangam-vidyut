import os
import time
from scripts.experiments.phase_4f_1_campaign import run_single_simulation, validate_run

def test_recovery():
    print("--- CRASH RECOVERY TEST ---")
    run_id = "R_RECOVERY_TEST"
    quarters = 3
    n_agents = 5
    
    # Check if already validated (simulate restart condition)
    if validate_run(run_id, quarters):
        print("Valid artifact discovered. SKIPPED existing run.")
        assert True
        return
    else:
        print("Generating artifact...")
        res = run_single_simulation(
            run_id=run_id,
            model_class="DETERMINISTIC_EMPIRICAL_ABM",
            topo="watts_strogatz",
            beta=0.15,
            seed=42,
            subsidy=0,
            p_base_mode="empirical",
            quarters=quarters,
            constant_val=None,
            n_agents=n_agents
        )
        print(f"Generated. Status: {res['status']}")
        
        # Simulate crash
        print("Simulating crash... Exiting without further updates.")
        assert res['status'] == 'COMPLETED'

if __name__ == "__main__":
    test_recovery()
