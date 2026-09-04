# Residential PV System-Size Source Audit (Phase 4D.7)

## 1. Context & Motivation
To mathematically compare binary household adoption rates against historical/modern MW targets (P0-B), the ABM requires a `system_size_distribution_kw`. The objective of this audit was to locate an authoritative dataset representing `P(system_size_kw | residential installation)`.

## 2. Search Strategy & Findings

### PM Surya Ghar (Modern Era)
- **Capacity Bands:** The subsidy is tiered based on system capacity (0–2 kW, 2–3 kW, >3 kW). However, a granular dataset showing the exact frequency/count of households adopting within each specific band is not published as a standalone official PDF on `sansad.in` or OGD.
- **Paired Data (P2 Level):** Press releases and dashboard snapshots (e.g., August 2026 metrics citing 5.04M households and 14,894 MW) provide paired national and state totals. This yields a single mathematical average (e.g., ~2.95 kW national mean) but does not supply the variance, distribution shape, or discrete probabilities required for an empirical distribution.

### Rooftop Solar Programme Phase-II (Historical)
- **Capacity Bands:** Phase-II similarly tiered subsidies (up to 3 kW, 3–10 kW). However, historical data reporting lacks granular household frequency by tier.
- **Paired Data:** Because no pre-2024 historical household count could be verified (as established in Phase 4D.6), paired (installations + capacity) data for the historical period does not exist.

## 3. Semantic Limitations
Without a discrete count of installations per kW band, relying on divided totals (Total MW / Total Installations) creates an identical point-estimate across all synthetic households. This violates the directive to avoid arbitrary numerical averages (e.g., "assume 3 kW") and strips the variance necessary for accurate economic simulations of household affordability.

## 4. Conclusion
An exact, verifiable P0/P1 official dataset providing a true residential system-size probability distribution could not be located in accessible archives. 

**NO VERIFIED DIRECT RESIDENTIAL SYSTEM-SIZE DISTRIBUTION FOUND**
