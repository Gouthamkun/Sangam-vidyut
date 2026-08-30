# Data Dictionary

This document outlines the input datasets utilized by Sangam Vidyut.

### 1. Census / NSSO Household Demographic Data
- **Source**: National Sample Survey Office (NSSO) / Census.
- **Contents**: Household size, income bracket, geographical location, housing type, electricity consumption baseline.
- **Usage**: Feeds into LLM Persona Generation to create diverse Consumer Agents.

### 2. MNRE State-wise Solar Adoption Records
- **Source**: Ministry of New and Renewable Energy (MNRE).
- **Contents**: Historical counts of solar installations partitioned by state, capacity, and year.
- **Usage**: Used to train the Logistic Regression module to establish baseline adoption probabilities.

### 3. IRENA Panel Pricing & Technology Cost Data
- **Source**: International Renewable Energy Agency (IRENA).
- **Contents**: Historical costs of PV modules, installation costs, efficiency metrics over time.
- **Usage**: Trains the LSTM model to forecast future solar technology costs for the Industry Agent.

### 4. Household Social Network Graph Data
- **Source**: Empirical survey data or synthetically generated (e.g., Watts-Strogatz small-world graphs).
- **Contents**: Nodes (Households) and Edges (Relationships/Influence connections).
- **Usage**: Parsed by NetworkX to structure the simulation grid and govern the SIR diffusion model.

### 5. Government Subsidy & Policy Parameters
- **Source**: Official policy documents (e.g., PM Surya Ghar Muft Bijli Yojana).
- **Contents**: Subsidy tiers, eligibility criteria, tax rebates, grid feed-in tariffs.
- **Usage**: Parsed by the Rule-Based Encoding module to dictate the behavior of the Government Agent.
