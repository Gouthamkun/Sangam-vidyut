import time
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from src.simulation.live_runner import LiveSimulationRunner

# Exact configuration from bug report
runner = LiveSimulationRunner(
    subsidy=2500,
    beta=0.15,
    population=500,
    horizon=24,
    topology="watts_strogatz",
    household_mode="empirical",
    cognitive_mode="deterministic",
    policy="fixed",
    initial_adoption=5,
    recovery=2,
    seed=42
)

print("Running LiveSimulationRunner with bug report config...")
start = time.time()
res = runner.run()
elapsed = time.time() - start

print(f"\nRuntime: {elapsed:.1f} seconds")
print(f"Run ID: {res['run_id']}")
print(f"Final adoption: {res['final_adoption']}")

df = res['df']
print(f"\nTrajectory:")
for _, row in df.iterrows():
    print(f"  t={int(row['timestep'])}: adopters={int(row['adoption_count'])}, new={int(row['new_adoptions'])}, subsidy={row['subsidy']:.0f}, price={row['panel_price']:.0f}")

print(f"\nTotal expenditure: {df['cumulative_expenditure'].iloc[-1]:.0f}")
print(f"Budget remaining: {df['budget_remaining'].iloc[-1]:.0f}")
print(f"LLM calls: {res['metrics']['call_count']}")
print(f"Rule decisions: {res['metrics']['rule_decisions']}")