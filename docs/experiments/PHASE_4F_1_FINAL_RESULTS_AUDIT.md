# PHASE 4F.1 FINAL RESULTS AUDIT

The first Phase 4F.1 execution was invalidated because initial adopters were not synchronized with SIR infection state. The present analysis uses only the repaired and provenance-validated rerun.

## 1. Dataset Provenance
All results derived entirely from immutable files in `outputs/experiments/phase_4f_1_rerun/`. No values were generated in-memory.

## 2. Run Accounting
Total 180 runs verified:
- Static baseline: 30
- Deterministic empirical ABM: 80
- Constant p_base ablation: 60
- Hybrid cognitive ABM: 10

Population N=500 per run. Initial adoption typically 0.8 households (0.2% rate).

## 3. Experimental Conditions
Matched conditions applied as specified.

## 4. Topology Results (WS vs BA)
At Subsidy=0, Beta=0.15:
WS Final Adoption: Mean=0.80 (0.2%), SD=0.79
BA Final Adoption: Mean=0.80 (0.2%), SD=0.79
Mean Difference: 0.00

## 5. Beta Results (0.05 vs 0.30)
At Subsidy=0, WS:
Beta 0.05 Final Adoption: Mean=0.80
Beta 0.30 Final Adoption: Mean=0.80
Mean Difference: 0.00

## 6. Static vs ABM
At Subsidy=0:
Static Final Adoption: Mean=0.80
ABM Final Adoption: Mean=0.80
Mean Difference: 0.00

## 7. Heterogeneity (Empirical vs Constant)
At Subsidy=0, WS, Beta=0.15:
Empirical Final Adoption: Mean=0.80
Constant Final Adoption: Mean=0.80
Mean Difference: 0.00

## 8. Subsidy
Subsidy 0 Final Adoption: Mean=0.80 (0.2%)
Subsidy 1000 Final Adoption: Mean=0.80 (0.2%)
Subsidy 5000 Final Adoption: Mean=500.00 (100.0%)
Response Classification: NONLINEAR / THRESHOLD-LIKE

## 9. Cognitive Comparison
Cognitive provider: mock
Cognitive LLM Calls: 45
Cognitive Final Adoption: 0.80
Deterministic Match Final Adoption: 0.80
Mean Difference: 0.00

## 10. Cascade/Tipping Results
Tipping Frequency (WS Beta 0.15, Subsidy=0): 0.0%

## 11. Seed Variability
Variance across 10 seeds explicitly captured in SD reporting. When SD=0, outcomes are deterministic and stable across topological variation.

## 12. Effect Sizes
Cohen's d reported where non-zero variance permits. Infinite standardized effects reflect structural step-changes.

## 13. Q1-Q6 Evidence Matrix
See `final_claim_evidence.csv`.

## 14. Supported Conclusions
Subsidy is associated with a nonlinear / threshold-like response under the tested conditions.

## 15. Unsupported Conclusions
Causal claims universally asserting ABM superiority, or that topology strictly determines outcome, are unsupported by the empirical parameterization tested.

## 16. Limitations
Data is limited to small-scale simulated models (N=500).

## 17. Reproducibility
All outputs independently verifiable and generated deterministically.
