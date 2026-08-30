# Data Strategy

## Data Provenance
To ensure research integrity, data categories are strictly separated:
- **Real Empirical Data**: Ground-truth datasets such as Census demographics, MNRE historical adoption records, and IRENA price data. These are read-only and immutable.
- **Derived Data**: Data generated through statistical aggregation of empirical data (e.g., state-wise averages).
- **Synthetic Data**: Artificially generated structures (e.g., generated network graphs, LLM-generated personas) used to simulate environments where empirical data is missing. Must be explicitly tagged as synthetic.
- **Simulated Data**: Outputs produced dynamically during the Mesa simulation runs.

Synthetic data will never be presented as empirical evidence. All experiments will explicitly state the provenance of their inputs.

## Social Network Data Strategy

The diffusion of solar technology relies heavily on social topology. Because exhaustive empirical mappings of household relationships are rarely available, the system supports both empirical and synthetic network structures.

### A. Empirical Networks
If provided, real graph data (e.g., survey-based community connections) will be ingested via NetworkX to map exact household nodes and edges.

### B. Synthetic Networks
When empirical data is unavailable, the framework will utilize synthetic topologies. The choice of topology drastically affects diffusion dynamics and experimental validity.

1. **Random Networks (Erdős–Rényi)**
   - **Characteristics**: Edges are formed randomly.
   - **Validity Impact**: Unrealistic for human social networks. Diffusion spreads too uniformly, ignoring community clustering. Included only as a null-hypothesis baseline.
2. **Small-World Networks (Watts-Strogatz)**
   - **Characteristics**: High local clustering but short average path lengths ("six degrees of separation").
   - **Validity Impact**: Highly realistic for geographic household communities. Captures local neighborhood influence while allowing cross-town viral spread. Recommended default.
3. **Scale-Free Networks (Barabási–Albert)**
   - **Characteristics**: Driven by preferential attachment; highly connected "hubs" dominate.
   - **Validity Impact**: Realistic for digital social networks (e.g., Twitter influencers), but less accurate for physical solar panel adoption, which is geographically constrained. Useful for testing the impact of highly influential community leaders.

**Strategy**: The system will support all three synthetic generators, allowing researchers to parameterize the graph type and document how the network choice affects the tipping point of solar adoption.
