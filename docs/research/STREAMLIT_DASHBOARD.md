# Streamlit Research Dashboard

## How to Launch
To launch the Sangam Vidyut interactive research dashboard locally, ensure your environment has `streamlit` and `plotly` installed.
Run the following command from the repository root:
```bash
streamlit run app.py
```

## Architecture
The dashboard is a visualization and exploration interface, explicitly separated from the heavy numerical simulation engine (`Mesa`). 
It relies on Streamlit's `@st.cache_data` to load precomputed CSV aggregations securely and efficiently without mutating the underlying scientific source artifacts. Raw trajectory files are lazy-loaded only when a user selects them from the sidebar.

## Data Sources
- `outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv`
- `outputs/experiments/phase_4f_3/tables/fixed_vs_dynamic.csv`
- `outputs/experiments/phase_4f_3/raw/R3_DET_*_trajectory.csv`

## Available Controls
The sidebar exposes isolated dimensions from the locked experimental factorial:
- **Research Phase**: 4F.1, 4F.2, 4F.3
- **Subsidy Level**: 0, 1000, 2000, 3000, 4000, 5000
- **Topology**: Watts-Strogatz vs Barabási-Albert
- **Beta (Transmission)**: 0.05, 0.15, 0.30
- **Household Representation**: Empirical vs Constant
- **Policy Mode**: Fixed vs Target-seeking dynamic

## Limitations
- The dashboard visualizes results from a bounded computational experiment (N=500).
- It is **not** a validated national forecast.
- Calibration is strictly aggregate-consistent/ecological.

## Reproducibility
The dashboard itself performs no math or data generation. It simply reflects the mathematically locked results stored in `outputs/`. The raw data was generated across 1,060 runs using strict configuration hashing and seed isolation, guarded by 126 `pytest` invariants.
