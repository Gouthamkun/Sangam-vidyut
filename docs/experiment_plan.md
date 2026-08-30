# Experiment Plan

Sangam Vidyut is designed to support rigorous, reproducible experiments.

## 1. Baseline vs. Agent-Based Model Comparison
- **Objective**: Demonstrate the added value of the ABM approach over static statistical forecasting.
- **Methodology**: 
  - Run the Static Baseline Regression (using historical MNRE data and Logistic Regression) to project future adoption over $T$ years.
  - Run the full LangGraph/Mesa ABM simulation over the same time period $T$.
  - Compare the resulting adoption curves.
- **Expected Output**: A quantitative assessment of how social diffusion (SIR) and dynamic policy feedback alter adoption rates compared to linear/logistic trends.

## 2. Policy Scenario Analysis
- **Objective**: Evaluate the impact of different subsidy structures.
- **Methodology**:
  - **Scenario A**: Business-as-usual (current subsidies).
  - **Scenario B**: Aggressive upfront capital subsidy.
  - **Scenario C**: High feed-in tariffs (rewarding generation over installation).
- **Expected Output**: Policy Scenario Comparison Dashboard detailing which policy yields the fastest adoption and lowest carbon emissions.

## 3. Cascade & Tipping-Point Detection
- **Objective**: Identify the critical threshold of adoption required to trigger self-sustaining viral growth in a community.
- **Methodology**:
  - Vary the initial "seed" adopters in the NetworkX graph.
  - Measure the time-to-saturation for different network topologies (e.g., dense urban vs. sparse rural).
- **Expected Output**: Cascade analysis report identifying the "tipping point" percentage for target demographics.

## 4. Emissions Impact Estimation
- **Objective**: Quantify the environmental benefit of the simulated adoption.
- **Methodology**:
  - The Environment Agent calculates carbon displacement based on simulation adoption rates multiplied by the regional Carbon Factor.
- **Expected Output**: Total CO2 equivalent mitigated under various policy scenarios.
