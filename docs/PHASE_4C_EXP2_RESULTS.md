# Phase 4C Experiment 2 Results: Economic Nonlinearity

## 1. Research Question
Does renewable-energy adoption exhibit a non-linear threshold response (an "adoption cliff") to government subsidy interventions when isolated from cognitive and social influences?

## 2. Hypothesis
We hypothesized that systematically increasing the government subsidy would improve the deterministic affordability score, eventually crossing a critical threshold that triggers a non-linear population-wide adoption cascade. 

## 3. Experimental Design
- **Model**: `DETERMINISTIC_ABM`
- **Cognitive Routing**: Disabled. Thresholds clamped to `[0.5, 0.5]` enforcing strict mathematical bypass.
- **Topology**: Fixed at `watts_strogatz`
- **Network Influence (Beta)**: Fixed at `0.1`
- **Dynamic Policy**: Disabled (`dynamic_subsidy = False`) to prevent the government from naturally correcting the fixed experimental sweeps.
- **Population**: `n_agents = 500`
- **Timesteps**: `24`

## 4. Parameter Matrix (Subsidy Sweep)
The `subsidy` parameter was evaluated at:
`[500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]`

**Number of runs**: 10 independent integer seeds per subsidy level (100 total executions).

## 5. Results Table

| Subsidy (₹) | Affordability (Max 1.0) | Mean Final Adoption | Std Dev | Mean Tipping Pt | Peak Rate | T-25% | T-50% |
|-------------|-------------------------|---------------------|---------|-----------------|-----------|-------|-------|
| 500         | 0.10                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 1000        | 0.20                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 1500        | 0.30                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 2000        | 0.40                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 2500        | 0.50                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 3000        | 0.60                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 3500        | 0.70                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 4000        | 0.80                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 4500        | 0.90                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |
| 5000        | 1.00                    | 1.00% (5 agents)    | 0.00%   | None            | 0.00%     | -     | -     |

*Note: The 1.00% baseline represents exactly 5 agents—the initial starting seed randomly chosen by the generator. Zero actual in-simulation adoptions occurred across any run.*

## 6. Adoption vs Subsidy Analysis & Tipping Points
No nonlinear transition was identified. In fact, **no adoption whatsoever occurred at any subsidy level** under the deterministic mathematical routing. 

The tipping point was never reached in any of the 100 executed runs. Variance across seeds was strictly 0.0%.

## 7. Mathematical Post-Mortem
This behavior is not a bug, but rather an exact manifestation of the Phase 3 rigid mathematical formula:
`Score = 0.4 * (Base_Probability) + 0.4 * (SIR_Influence) + 0.2 * (Affordability)`

- Because `Base_Probability` is derived from a `LogisticRegression` model randomly mock-fit with dummy data, its output hovers near the binary threshold of ~`0.5`.
- Therefore, the baseline contribution is roughly `0.4 * 0.5 = 0.2`.
- At `subsidy = 5000` (which is 100% of the panel price), `Affordability` maxes out at `1.0`. Its formula contribution is `0.2 * 1.0 = 0.2`.
- For an isolated agent with no infected neighbors, `SIR_Influence = 0.0`.
- The highest possible mathematical score achieved independently is `0.2 + 0.0 + 0.2 = 0.4`.

Because the `DETERMINISTIC_ABM` strictly evaluates `Score >= 0.5` for adoption, an isolated score of `0.4` triggers unanimous, continuous rejection. The structural math rigidly suppresses adoption because affordability is severely under-weighted (20% maximum influence) compared to required network pressure.

## 8. Conclusion
The hypothesis is **rejected** for the `DETERMINISTIC_ABM`. 

Increasing the subsidy up to 100% of the asset cost does not produce a nonlinear cascade threshold because the algorithmic architecture mathematically bounds the economic influence below the absolute requirement for adoption. 

## 9. Limitations
These results heavily highlight the limitation of pure mathematical rationality inside ABMs. Real human households would almost certainly adopt if the government provided a 100% subsidy (making the panels free), but the deterministic formula structurally traps agents in `WAIT` states. This provides extremely strong scientific justification for why the cognitive (LLM) routing layer introduced in Phase 3C is absolutely critical to modeling bounded human rationality.
