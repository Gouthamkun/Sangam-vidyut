# Historical Residential Solar Source Audit (Phase 4D.5A)

## 1. Context & Motivation
Phase 4D.5 confirmed that Lok Sabha UQ 1936 provides *total solar capacity (MW)* (blending Ground-Mounted, RTS, and Off-grid) and does *not* provide historical residential consumer counts. To calibrate Sangam Vidyut's household adoption model, we strictly require a dataset containing **historical residential rooftop solar installation counts** prior to the launch of PM Surya Ghar in Feb 2024.

## 2. Target Variable Definition
- **Preferred Metric:** Number of residential consumers / Number of households benefited / Residential installations.
- **Unit:** Discrete count (households).
- **Semantics:** Physically installed and grid-connected residential rooftop solar systems. This directly corresponds to the discrete ABM state `agent.adopted = True`.

## 3. Search Period & Availability
- **Target Period:** 2015–2023.
- **Data Gap:** The live MNRE SPIN portal is currently inaccessible/timed-out. Continuous month-by-month time series for residential installations are notoriously difficult to acquire publicly.
- **Snapshot Availability:** State-wise snapshot aggregates (e.g., "Installations up to Dec 2023") are periodically released via Parliament (Lok Sabha/Rajya Sabha Q&A) and MNRE Annual Reports.

## 4. Official Source Hierarchy
1. **P0 (Direct Historical Residential Installation Count):** Lok Sabha Unstarred Questions regarding "State-wise physical progress under Rooftop Solar Programme Phase-II (Residential)". (e.g., Questions explicitly listing "Number of systems installed in residential sector").
2. **P0 (Modern PM Surya Ghar Count):** Lok Sabha UQ 1698 (Extracted in Phase 4D.5, successfully provides 4.04M exact installations).
3. **P1 (Residential Capacity Cross-Check):** OGD datasets or parliamentary replies detailing *allocated vs installed Residential Capacity (MW)* under Phase II.
4. **P2 (Total Solar Capacity Context):** Lok Sabha UQ 1936 (Extracted in Phase 4D.5, provides total solar macro-baseline).

## 5. Recommended Target Architecture
To accurately validate the simulation without mixing metrics, the data architecture should be:
**[Historical Residential Consumer Count (Pre-Feb 2024)]**
*plus*
**[PM Surya Ghar Installations (Feb 2024 – Present)]**
*cross-checked by*
**[Historical Residential Capacity (MW) & Total Macro Capacity (MW)]**

## 6. Bridge Analysis (Updated)
Bridging a historical residential count to PM Surya Ghar is feasible *only if* the historical metric is structurally identical (i.e., household counts).
- **Metric Compatibility:** Valid if both are household counts. 
- **Programme Scope:** RTS Phase II strictly targeted residential (like PM Surya Ghar).
- **Overlap Risk:** Low, provided the historical snapshot date is firmly bounded at Jan/Feb 2024, as PM Surya Ghar requires fresh portal registrations.

## 7. Manual Acquisition Directives
Since the SPIN portal is down, the most authoritative historical backup is the Lok Sabha Q&A archive. The user must manually locate the exact parliamentary snapshot that lists residential consumers under Phase II prior to the PM Surya Ghar transition.
