import sys
import os
sys.path.insert(0, os.path.abspath("."))

from src.config.schema import ExperimentConfig, BehaviorPolicyConfig, CognitiveConfig
from src.simulation.llm.providers import MockLLMProvider
import numpy as np

# Test MockLLM at t=9 conditions
config = ExperimentConfig()
config.cognitive.policy.name = "cognitive_accessible_candidate_v1"
config.cognitive.sync_policy_thresholds()
config.simulation.seed = 42
config.llm.provider = "mock"

mock_llm = MockLLMProvider(config)

# At t=9: panel_price ~ 3151, subsidy = 2500, affordability = 0.793
# Max p_base = 0.11145
# Max score = 0.4*0.11145 + 0.2*0.793 = 0.04458 + 0.1586 = 0.20318
# With noise up to 0.15: max = 0.35318 < 0.5

print("Testing MockLLM at t=9 conditions (max possible score):")
test_context = {
    "combined_score": 0.20318,
    "income": 19333,  # max derived_mpce
    "home_owner": -1,
    "sir_score": 0.0,
    "affordability": 0.793,
    "panel_price": 3151,
    "subsidy": 2500,
    "adopting_neighbors": 0,
    "total_neighbors": 4,
    "prompt_version": "v1",
    "model_identifier": "mock",
    "provider": "mock",
    "temperature": 0.1
}

for i in range(20):
    decision = mock_llm.generate_decision(test_context)
    print(f"  Call {i+1}: decision={decision}")

# What if there ARE infected neighbors?
# With 1 infected neighbor: sir_score = 0.15
# Score = 0.4*0.11145 + 0.4*0.15 + 0.2*0.793 = 0.04458 + 0.06 + 0.1586 = 0.26318
# With 2 infected neighbors: sir_score = 0.2775
# Score = 0.4*0.11145 + 0.4*0.2775 + 0.2*0.793 = 0.04458 + 0.111 + 0.1586 = 0.31418
# With 3 infected neighbors: sir_score = 0.3859
# Score = 0.4*0.11145 + 0.4*0.3859 + 0.2*0.793 = 0.04458 + 0.15436 + 0.1586 = 0.35754
# With 4 infected neighbors: sir_score = 0.478
# Score = 0.4*0.11145 + 0.4*0.478 + 0.2*0.793 = 0.04458 + 0.1912 + 0.1586 = 0.39438

print("\nTesting with 3 infected neighbors (score=0.35754):")
test_context["combined_score"] = 0.35754
test_context["sir_score"] = 0.3859
test_context["adopting_neighbors"] = 3
for i in range(20):
    decision = mock_llm.generate_decision(test_context)
    print(f"  Call {i+1}: decision={decision}")

print("\nTesting with 4 infected neighbors (score=0.39438):")
test_context["combined_score"] = 0.39438
test_context["sir_score"] = 0.478
test_context["adopting_neighbors"] = 4
for i in range(20):
    decision = mock_llm.generate_decision(test_context)
    print(f"  Call {i+1}: decision={decision}")

# But at t=9, there are 0 infected agents (initial 5 recovered by t=2)
# So how did adoption happen?
# Unless... the initial adopters didn't recover? Or new adopters were created somehow?

# Let me check if maybe the recovery logic is different
print("\nChecking recovery logic:")
print(f"recovery_duration_quarters: {config.sir.recovery_duration_quarters}")
# In consumer step:
# if self.sir_state == 1:
#     self.time_infected += 1
#     if self.time_infected >= self.model.config.sir.recovery_duration_quarters:
#         self.sir_state = 2
# So at t=0: time_infected=0, sir_state=1
# t=1 step: time_infected=1, sir_state=1
# t=2 step: time_infected=2, sir_state=2 (recovered)
# So from t=2 onwards, initial adopters are recovered.

# But wait - the model step order:
# 1. Government/Industry step
# 2. Consumer step (where recovery check happens)
# 3. Environment/Analysis step
# Data collection happens AFTER all steps

# At t=0 (initial): 5 infected, time_infected=0
# t=1 step: consumers step -> time_infected=1, still infected
# t=2 step: consumers step -> time_infected=2 >= 2, sir_state=2 (recovered)
# So after t=2 step, 0 infected.

# At t=9 step (the 9th step), there should be 0 infected.

# Unless... the MockLLM cache is causing issues? Let me check the cache key generation.
# The cache key includes: income_decile, home_owner, sir_score, affordability, panel_price, subsidy, adopting_neighbors, total_neighbors, prompt_version, model_identifier, provider, temperature
# At t=9, panel_price=3151, subsidy=2500, affordability=0.79, adopting_neighbors=0 for all
# Many agents would have the same cache key (same income_decile rounded to 0.1, etc.)
# But the first call for each unique context would be a cache miss and generate a decision.

# With 495 agents, many unique contexts... but all decisions should be False.

# I'm very confused. Let me check if maybe the adoption in the trajectory is from a DIFFERENT run or there's a bug in my trajectory reading.

# Actually, let me re-run the full simulation but stop at t=9 and check the decisions.