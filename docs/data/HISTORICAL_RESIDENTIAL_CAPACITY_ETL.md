# Historical Residential Capacity ETL (Phase 4D.6)

## 1. Source Verification
Two manual PDFs were physically retrieved from `data/raw/solar/adoption/`:
1. **Rajya Sabha Starred Question No. 210** (08.08.2023). Table explicitly outlines `Capacity installed under CFA under Phase-II (MW)`. Reference Date: 30.06.2023.
2. **Lok Sabha Unstarred Question No. 3579** (10.08.2023). Table explicitly outlines `Capacity installed under CFA under Phase-II (MW)` and `Capacity installed under New Simplified Procedure in National Portal`. Reference Date: 31.07.2023.

## 2. Extraction & Row Counts
Automated pypdf extraction correctly identified the tables and metrics:
*   **RS SQ 210:** Extracted exactly 36 states/UTs, 2 capacity columns -> 72 structural rows.
*   **LS UQ 3579:** Extracted exactly 36 states/UTs, 3 capacity columns -> 108 structural rows (long format).

## 3. Metric Semantics
- **Capacity installed under CFA under Phase-II (MW):** Specifically maps to **Residential Rooftop Solar Capacity (MW)** (P0-B) since Phase-II Central Financial Assistance is structurally restricted to the residential sector.
- **Capacity installed under New Simplified Procedure in National Portal:** Also Residential MW (National Portal launch).
- **Total Net Allocation:** Represents administrative sanctions, NOT physical installed capacity.
- **Cumulative capacity installed... with or without CFA (MW):** Maps to **All Rooftop** capacity (including C&I).

## 4. Source Totals & Reconciliation
*   **RS 210 CFA:** Computed sum is 2045.72 MW vs Official total 2045.72 MW. Perfect match.
*   **RS 210 Cumulative:** Computed sum is 9109.21 MW vs Official total 9109.21 MW. Perfect match.
*   **LS 3579 Allocation:** Computed sum is 3370.81 MW vs Official total 3370.82 MW. (-0.01 MW rounding).
*   **LS 3579 CFA:** Computed sum is 2117.06 MW vs Official total 2117.06 MW. Perfect match.
*   **LS 3579 Portal:** Computed sum is 90.54 MW vs Official total 90.53 MW. (+0.01 MW rounding).

## 5. Provenance & Integrity
- SHA-256 checksums successfully calculated for both PDFs and written to `data/metadata/solar/adoption/rs_sq210_metadata.json` and `ls_uq3579_metadata.json`.
- State normalization mapped raw abbreviations (e.g., `DNH&DD` to `Dadra & Nagar Haveli and Daman & Diu`) preserving full geographic integrity without dropping rows.
- 5/5 PyTest validations successfully executed for schema validity and mathematical reconciliation.
