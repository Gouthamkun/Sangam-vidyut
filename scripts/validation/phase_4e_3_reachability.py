import pandas as pd
import numpy as np

w_base = 0.4
w_sir = 0.4
w_aff = 0.2

lower = 0.3
upper = 0.7

p_percentiles = {
    "p50": 0.000330,
    "p75": 0.000755,
    "p90": 0.001815,
    "p99": 0.01, # approx based on distribution tail
    "p_max": 0.111450
}

affordabilities = [0.2, 1.0] # default and max

results = []

for p_label, p_val in p_percentiles.items():
    for aff in affordabilities:
        # We need sir_score such that:
        # w_base * p_val + w_sir * sir + w_aff * aff = target
        # sir = (target - w_base * p_val - w_aff * aff) / w_sir
        
        req_sir_llm = (lower - w_base * p_val - w_aff * aff) / w_sir
        req_sir_llm = max(0.0, req_sir_llm) # if negative, 0 is enough
        
        req_sir_auto = (upper - w_base * p_val - w_aff * aff) / w_sir
        req_sir_auto = max(0.0, req_sir_auto)
        
        results.append({
            "p_base_level": p_label,
            "p_base_val": p_val,
            "affordability": aff,
            "req_sir_for_llm": min(req_sir_llm, float('inf')) if req_sir_llm <= 1.0 else "UNREACHABLE",
            "req_sir_for_auto": min(req_sir_auto, float('inf')) if req_sir_auto <= 1.0 else "UNREACHABLE"
        })

df = pd.DataFrame(results)
df.to_csv("outputs/validation/phase_4e_3/score_reachability.csv", index=False)
print("Score reachability computed.")
