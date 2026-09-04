# Solar Adoption ETL & Validation Report (Phase 4D.5)

## 1. Source Verification
Two PDFs were manually placed in `data/raw/solar/adoption/` and their checksums (SHA-256) were stored in `data/metadata`. 
- **Historical:** Lok Sabha UQ 1936 (Answer Date: 14.12.2023, Ref Date: 31.10.2023). Contains total installed solar capacity (MW).
- **PM Surya Ghar:** Lok Sabha UQ 1698 (Answer Date: 29.07.2026, Ref Date: 27.07.2026). Contains PM-SGMBY residential installations and subsidy released.

## 2. Extraction Results
Automated `pypdf` extraction was used with custom Python logic to parse line-wraps and page breaks.
- **UQ 1936:** Extracted exactly 37 state/UT rows (including "Others"). Extracted from Pages 2 and 3.
- **UQ 1698:** Extracted exactly 36 state/UT rows. Extracted from Page 3. 
- *Anomaly Correction:* Dadra & Nagar Haveli and Andaman & Nicobar spanned multiple lines in the raw text dump. This was caught and corrected dynamically in the script by buffering incomplete numerical row matches.

## 3. State Coverage & Normalization
- **Number of States/UTs:** 36 (UQ 1698) and 37 (UQ 1936).
- **Normalization:** A deterministic mapping `data/processed/solar/adoption/state_name_mapping.csv` resolves variations (e.g., "JAMMU And KASHMIR" -> "Jammu & Kashmir"). No states were silently dropped.

## 4. Metric Definitions & Semantics
- UQ 1936 extracts `Capacity till 31-10-2023 (MW)`. This is a cumulative capacity metric for *all* solar sectors. It does *not* provide the number of residential consumers.
- UQ 1698 extracts `installations`, `households`, and `CFA released`. This is a cumulative residential count since Feb 2024. `applications` was missing from the annexure and set to empty.

## 5. Official Total Reconciliation
- **UQ 1936 Total:** Extracted rows sum to `72018.04 MW`. Official total reported is `72018.02 MW`. The difference of 0.02 is due to document rounding artifacts.
- **UQ 1698 Total:** Extracted `installations` sum to exactly `4,045,298`. Extracted `households` sum to exactly `4,880,796`. Extracted `CFA` sums to `27343.88` (vs official `27343.90`). The extraction accurately captures the table totals.

## 6. Data Limitations
The critical limitation is that UQ 1936 does *not* contain residential consumer counts. It provides overall solar MW. Therefore, these two sources cannot currently be merged into a single cumulative historical time series without expert assumptions (which are forbidden at this stage).

## 7. Test Results
`python -m pytest tests/data/test_solar_adoption_etl.py` executed successfully, passing 6/6 tests covering schema validity, non-negative numerics, state uniqueness, and official total reconciliation.

## FINAL STATUS
**PHASE 4D.5 = SOLAR DATA EXTRACTION COMPLETE / AWAITING REVIEW**
