import pytest
import pandas as pd
import time
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.config.schema import ExperimentConfig
from src.simulation.live_runner import LiveSimulationRunner

def test_propagation_subsidy():
    runner = LiveSimulationRunner(subsidy=2750.5)
    assert runner.config.government.base_subsidy == 2750.5

def test_propagation_beta():
    runner = LiveSimulationRunner(beta=0.173)
    assert runner.config.sir.beta == 0.173

def test_propagation_population():
    runner = LiveSimulationRunner(population=750)
    assert runner.config.simulation.n_agents == 750

def test_deterministic_mode():
    runner = LiveSimulationRunner(
        population=100, 
        horizon=2, 
        cognitive_mode="deterministic"
    )
    res = runner.run()
    assert res["metrics"]["call_count"] == 0
    assert len(res["df"]) == 3 # step 0 + 2 steps

def test_trajectory_lengths():
    runner = LiveSimulationRunner(horizon=5)
    res = runner.run()
    assert len(res["df"]) == 6 # Includes step 0

def test_population_conservation():
    runner = LiveSimulationRunner(population=50, horizon=2)
    res = runner.run()
    df = res["df"]
    
    # Check SIR states sum to N
    total_sir = df["susceptible_count"] + df["infected_count"] + df["recovered_count"]
    assert all(total_sir == 50)

def test_temporal_consistency():
    runner = LiveSimulationRunner(
        subsidy=5000,
        beta=0.30,
        population=100,
        horizon=12,
        topology="barabasi_albert",
        household_mode="constant",
        policy_mode="dynamic",
        cognitive_mode="deterministic",
        seed=42
    )
    res = runner.run()
    df = res["df"]
    
    # adoption_count[t] - adoption_count[t-1] == new_adoptions[t]
    for t in range(1, len(df)):
        diff = df["adoption_count"].iloc[t] - df["adoption_count"].iloc[t-1]
        assert diff == df["new_adoptions"].iloc[t]
        
    # cumulative expenditure changes exactly with new_adoptions * subsidy
    for t in range(1, len(df)):
        exp_diff = df["cumulative_expenditure"].iloc[t] - df["cumulative_expenditure"].iloc[t-1]
        expected = df["new_adoptions"].iloc[t] * df["subsidy"].iloc[t]
        assert abs(exp_diff - expected) < 1e-5
