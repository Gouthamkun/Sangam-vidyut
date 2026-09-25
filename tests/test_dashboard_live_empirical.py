import pytest
import math
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from src.simulation.live_runner import LiveSimulationRunner
from src.simulation.agents.consumer import ConsumerAgent

def test_live_empirical_deterministic_regression():
    runner = LiveSimulationRunner(
        subsidy=1000,
        beta=0.15,
        population=500,
        horizon=1,  # execute at least one timestep
        topology="watts_strogatz",
        household_mode="empirical",
        policy_mode="fixed",
        initial_adoption=5,
        recovery=2,
        cognitive_mode="deterministic",
        seed=42
    )
    
    res = runner.run()
    
    # Assert execution completed and we got a dataframe
    assert len(res["df"]) == 2 # step 0 + 1 step
    
    model = runner._model
    consumer_count = 0
    for agent in model.agents:
        if isinstance(agent, ConsumerAgent):
            assert hasattr(agent, "derived_mpce"), "ConsumerAgent missing derived_mpce!"
            assert agent.derived_mpce is not None
            assert not math.isnan(agent.derived_mpce)
            assert agent.derived_mpce >= 0
            consumer_count += 1
            
    assert consumer_count == 500, "Did not find expected number of ConsumerAgents!"

def test_live_empirical_ollama_regression():
    runner = LiveSimulationRunner(
        subsidy=1000,
        beta=0.15,
        population=500,
        horizon=1,
        topology="watts_strogatz",
        household_mode="empirical",
        policy_mode="fixed",
        initial_adoption=5,
        recovery=2,
        cognitive_mode="ollama", # Trigger the LLM usage
        seed=42
    )
    
    res = runner.run()
    assert len(res["df"]) == 2
    
def test_live_constant_regression():
    runner = LiveSimulationRunner(
        subsidy=1000,
        beta=0.15,
        population=500,
        horizon=1,
        topology="watts_strogatz",
        household_mode="constant",
        policy_mode="fixed",
        initial_adoption=5,
        recovery=2,
        cognitive_mode="deterministic",
        seed=42
    )
    
    res = runner.run()
    assert len(res["df"]) == 2
    model = runner._model
    consumer_count = sum(1 for a in model.agents if isinstance(a, ConsumerAgent))
    assert consumer_count == 500
