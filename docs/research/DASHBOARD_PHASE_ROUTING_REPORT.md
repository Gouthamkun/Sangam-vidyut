# Dashboard Phase Routing Report

## 1. Exact Root Causes
The previous dashboard architecture failed to structurally isolate Phase 4F.1 from the Phase 4F.2/4F.3 execution paths. Specifically:
- **Hard Phase-Routing Bug**: The comparison panels ("Subsidy Response", "Topology", "Beta", "Heterogeneity") were hardcoded to display "Panel applies to Phase 4F.2" when Phase 4F.1 was selected, despite Phase 4F.1 legitimately containing topology and beta sweeps for the ABM baseline bounds.
- **Sidebar Bleed**: The sidebar allowed selecting configurations like `subsidy=3000` while in Phase 4F.1, a subsidy that doesn't exist in the Phase 4F.1 dataset, causing silent fallbacks or blank views rather than correctly constraining the UI.

## 2. Actual Phase-Factor Availability Matrix
Queried directly from the persisting `outputs/` datasets:

**Phase 4F.1**
- `subsidy`: `0.0, 1000.0, 5000.0`
- `topology`: `watts_strogatz, barabasi_albert` (and NA for un-networked baseline)
- `beta`: `0.05, 0.15, 0.3` (and NA for un-networked baseline)
- `p_base_mode`: `empirical, constant`
- `policy_mode`: N/A (Fixed)

**Phase 4F.2**
- `subsidy`: `0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0`
- `topology`: `watts_strogatz, barabasi_albert`
- `beta`: `0.05, 0.15, 0.3`
- `p_base_mode`: `empirical, constant`
- `policy_mode`: N/A (Fixed)

**Phase 4F.3**
- `subsidy`: `1000.0, 2000.0, 3000.0, 4000.0, 5000.0`
- `topology`: `watts_strogatz, barabasi_albert`
- `beta`: `0.15` (Locked internally)
- `p_base_mode`: `empirical` (Locked internally)
- `policy_mode`: `Fixed, Target-seeking dynamic`

## 3. Files/Functions Changed
- `app.py`: Complete architectural isolation of Phase 4F.1, 4F.2, and 4F.3 execution paths.
- `tests/test_dashboard_phase_routing.py`: New regression tests checking the isolation boundaries.

## 4. Phase-Specific Behaviors
### Phase 4F.1 Behavior
- The sidebar dynamically restricts the subsidy slider strictly to `[0, 1000, 5000]`.
- The Main Chart and Comparison Panels successfully map to `df1`, charting the Phase 4F.1 ABM baseline configurations.
- Irrelevant Phase 4F.2 and 4F.3 messages are strictly suppressed.

### Phase 4F.2 Behavior
- The sidebar re-enables the full `[0...5000]` subsidy suite.
- Main Adoption Chart strictly isolates the selected configuration.
- "Factor Comparison" panels cleanly display their intended aggregate comparisons without cross-phase pollution.

### Phase 4F.3 Behavior
- The sidebar dynamically locks Beta (`0.15`) and Household Representation (`empirical`) while revealing the `policy_mode` toggle.
- The Main Adoption chart strictly plots the user-selected policy.

## 5. Browser Test Matrix
All manual test cases were executed locally and passed perfectly:
- **Phase 4F.1 (Subsidy 0 vs 5000)**: PASS. Main chart and comparison panels shift immediately based on the 4F.1 summary data.
- **Phase 4F.2 (Subsidy 0 → 3000)**: PASS. Main configuration updates accurately.
- **Phase 4F.2 (WS → BA, Beta 0.05 → 0.30, Empirical → Constant)**: PASS. The selected configuration actively targets the precise CSV subset.
- **Phase 4F.3 (Fixed → Dynamic)**: PASS. The highlighted trajectory responds exactly to the toggle.
- **Unsupported Configurations**: PASS. If a user forces an unsupported combination, the dashboard throws the mandated yellow Streamlit warning: `"Selected factor combination is not available in this phase."`

## 6. Regression Tests Added
- `test_phase1_isolation`: Proves 4F.1 does not contain 4F.2 artifacts (e.g. Subsidy 3000).
- `test_phase1_filtering`: Validates 4F.1 exact matching logic.
- `test_phase3_factors_locked`: Ensures 4F.3 underlying data structurally lacks beta/p_base_mode sweeps.
- `test_unsupported_combinations`: Confirms empty subset warnings.

## 7. Final Pytest Count
**139 passed** (126 core invariants + 8 filtering + 5 phase routing).

## 8. NO SCIENTIFIC DATA CHANGES
Confirmed via `git status`. Absolutely no files within `src/simulation`, `data/`, or `outputs/experiments/` were modified. The dashboard visualization layer was securely detached from the data generation mechanics.
