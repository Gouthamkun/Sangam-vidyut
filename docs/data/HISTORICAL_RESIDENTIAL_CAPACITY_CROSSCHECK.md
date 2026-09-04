# Historical Residential Capacity Cross-Check (Phase 4D.6)

## 1. Cross-Source Comparison (RS 210 vs LS 3579)
*   **Geographic Coverage:** Both documents comprehensively cover 36 States/UTs with identical mapping topologies.
*   **Reference Dates:** 
    *   Rajya Sabha Q210 → 30 June 2023
    *   Lok Sabha UQ3579 → 31 July 2023
*   **Metric Compatibility:** The `Capacity installed under CFA under Phase-II (MW)` metric is present in both sources and is directly comparable. Between June 30 and July 31, the national CFA-installed capacity grew from 2045.72 MW to 2117.06 MW.
*   **Overlap Risk & Independence:** Because they have different reference dates, they serve as two distinct temporal observations. They should NOT be averaged or interpolated. Lok Sabha UQ3579 (July 2023) is the slightly more recent observation prior to PM Surya Ghar.

## 2. Relationship to UQ 1936 (Contextual Macro Target P1)
*   Lok Sabha UQ 1936 provides *Total Solar Capacity (72,018 MW)*. 
*   **Rule:** The historically extracted Residential Phase-II MW (~2,117 MW) is explicitly a subset/contextual component of the broader UQ 1936 Total Solar MW. We must NEVER computationally combine or conflate the residential MW with total MW as equivalents.

## 3. Relationship to PM Surya Ghar UQ 1698 (Primary Calibration Target P0-A)
*   **Historical P0-B:** Residential rooftop capacity (MW).
*   **Modern P0-A:** Residential installation/household counts.
*   **Rule:** These are distinct empirical targets measuring fundamentally different dimensions of adoption (Capacity vs. Distinct Households). They must NEVER be appended into a single mathematical array.

## 4. Unresolved Capacity Model Gap
Currently, we hold MW data for pre-2024 and Household Counts for 2024+. To compare ABM household adoption directly against the P0-B MW targets, the model inherently requires an explicit `system_size_distribution_kw`. 
**Requirement:** We cannot arbitrarily assume an average system size (e.g., 3 kW). The distribution must eventually be empirically estimated from:
*   Official PM-SGMBY capacity vs. install counts.
*   Official state-level DISCOM residential system statistics.
*   Detailed Phase-II operational records.

Until this capacity model is mathematically resolved, historical MW calibration remains strictly separated from modern Household count calibration.
