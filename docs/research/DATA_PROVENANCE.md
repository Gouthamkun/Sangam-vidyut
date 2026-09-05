# Data Provenance

The Sangam Vidyut model relies on public empirical datasets mapped via ecological calibration. **No private credentials or sensitive local paths are exposed.**

## 1. Household Consumption Expenditure Survey (HCES 2023-24)
- **Purpose**: Empirical distribution of wealth proxy (MPCE) for synthetic household generation.
- **Local Representation**: Survey-weighted probability distributions.
- **Limitations**: Aggregate statistics only; does not provide direct household-level solar adoption labels.

## 2. MNRE Benchmark Costs
- **Purpose**: Establishes base panel prices and capital thresholds.
- **Local Representation**: `IndustryAgent` base constraints and scaling boundaries.

## 3. PM Surya Ghar Targets
- **Purpose**: Calibrates the government budget cap and 50% target milestones.
- **Local Representation**: Configures `GovernmentAgent` fiscal allocations.

## 4. CEA Domestic Consumer Data
- **Purpose**: Establishes the macro-denominator for household scale conversion.
- **Local Representation**: Bound-checking targets for the ecological scaling.
