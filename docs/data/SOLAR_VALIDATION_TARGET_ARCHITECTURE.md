# Solar Validation Target Architecture (Phase 4D.5B / 4D.7)

## 1. Target Hierarchy
To prevent metric pollution and explicitly handle data limitations, the validation architecture is stratified as follows:

*   **P0-A: Residential Household Installation Counts**
    *   *Definition:* Discrete count of households with commissioned grid-connected systems.
    *   *Use Case:* Primary calibration target for ABM binary adoption decisions.
*   **P0-B: Residential Rooftop Installed Capacity (MW)**
    *   *Definition:* Total MW capacity explicitly bounded to the residential sector.
    *   *Use Case:* Validation target; requires an intermediate system-size conversion model.
*   **P1: Total Rooftop/Solar Capacity (MW)**
    *   *Definition:* Macro capacity including Ground-Mounted, C&I, and Off-grid.
    *   *Use Case:* Contextual upper-bound validation. ABM residential outputs must strictly be less than or equal to this value.
*   **P2: Programme Applications / CFA Released**
    *   *Definition:* Intent-to-adopt registrations and financial subsidy flows.
    *   *Use Case:* Policy-process indicators and adoption funnel metrics. NOT an adoption outcome target.

## 2. Model Output Mapping
| ABM Variable | Conversion/Derivation | Empirical Target |
| :--- | :--- | :--- |
| `agent.adopted == True` (Sum) | None (Direct Count) | **P0-A:** Residential Installation Counts |
| `agent.system_size_kw` (Sum) | Requires empirical distribution mapping | **P0-B:** Residential Rooftop Capacity (MW) |
| `ABM Residential Capacity` | Do NOT compare directly. Can only act as a subset of total. | **P1:** Total Solar Capacity (MW) (Upper-bound only) |

## 3. Capacity Model Requirement
To mathematically compare binary household adoption (P0-A) against residential installed MW (P0-B), the simulation requires a **System Size Representation (kW/Household)**.
*   **Rule:** We will NOT use a fabricated point-estimate average (e.g., "assume 3 kW").
*   **Model Mapping Strategy:** The eventual model could represent `system_size_kw` as either an empirical categorical distribution, a weighted discrete distribution, or a continuous distribution fitted to observed data. (No final representation is chosen yet).
*   **Phase 4D.7 Status:** NO VERIFIED DIRECT RESIDENTIAL SYSTEM-SIZE DISTRIBUTION FOUND. P2-level paired totals (e.g., PM Surya Ghar state-wise installations and capacity) exist but provide only a single average without the variance required for a distribution.

## 4. Calibration vs Validation Design
*   **Constraint:** *NO VERIFIED CONTINUOUS PRE-2024 RESIDENTIAL INSTALLATION COUNT SERIES EXISTS.* 
*   **Recommended Calibration Target:** **PM Surya Ghar Snapshot (Feb 2024 – July 2026)**. Use the highly verified, state-wise household installation counts (UQ 1698) to calibrate the core decision logic and social contagion under the modern subsidy regime.
*   **Recommended Validation Target:** **Historical Phase-II Residential Capacity Snapshots (Pre-2024)**. Run the calibrated model backward/historically and validate the resulting `ABM installed capacity` against available P0-B (Residential MW) snapshots. Validate that total ABM residential outputs do not exceed the P1 (Total MW) upper-bound context established by UQ 1936.

## 5. Historical Data Gaps
*   Continuous time-series for residential counts prior to 2024 are missing.
*   Total Solar Capacity (UQ 1936) cannot be utilized directly to count households without violating methodological constraints.
*   Direct `P(system_size_kw | residential installation)` capacity-band distribution data is missing.
