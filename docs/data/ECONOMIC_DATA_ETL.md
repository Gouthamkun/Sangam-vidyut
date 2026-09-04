# ECONOMIC DATA ETL (Phase 4D.1)

## 1. Objective
Establish the empirical economic baseline for Sangam Vidyut using official, primary Indian data sources (MNRE). The extraction normalizes official raw subsidy and cost artifacts into a versioned, machine-readable format to guide future ABM calibration.

**Critical Constraint:** No ABM parameters, weights, or decision thresholds were modified during this phase.

## 2. Official Sources
### 2.1 MNRE Benchmark Costs
- **Source:** Ministry of New and Renewable Energy (MNRE)
- **Document Title:** Benchmark costs for Grid-connected Rooftop Solar Photo-voltaic systems
- **Effective Year:** 2021-22
- **Acquisition Date:** 2026-09-02
- **Raw File:** `data/raw/economic/mnre_benchmark_costs/benchmark_costs_2021_22.json`
- **Fields Extracted:** Geography, capacity range, cost per kW (INR)

### 2.2 PM Surya Ghar Subsidy
- **Source:** MNRE / PM Surya Ghar National Portal
- **Document Title:** PM Surya Ghar: Muft Bijli Yojana Official Guidelines
- **Launch Date:** 2024-02-15
- **Acquisition Date:** 2026-09-02
- **Raw File:** `data/raw/economic/pm_surya_ghar/official_guidelines_2024.json`
- **Fields Extracted:** Capacity bands, subsidy per kW, max subsidy per band, total max subsidy.

## 3. Transformations & Normalization
The ETL scripts (`ingest_mnre_costs.py`, `ingest_pm_surya_ghar.py`) perform the following:
1. Parse the raw JSON artifacts.
2. Ensure data types align with the strict Pydantic schemas in `schemas/data/economic.py`.
3. Normalize the output structure into lists of `BenchmarkCostRecord` and `SubsidyRecord` objects.
4. Export the clean data to `data/processed/economic/`.
5. Generate `ProvenanceMetadata` including SHA-256 checksums of the raw files, saving to `data/metadata/economic/`.

## 4. Validation Rules
The Pydantic schemas enforce deterministic validation:
- `currency` must be strictly `"INR"`.
- Costs and subsidies must be non-negative (`ge=0`).
- Duplicate entry logic is caught during the ETL execution.
- Missing required fields (e.g., date, slab capacity) explicitly fail processing.

## 5. Artifacts Generated
- **Raw Artifacts:**
  - `data/raw/economic/mnre_benchmark_costs/benchmark_costs_2021_22.json`
  - `data/raw/economic/pm_surya_ghar/official_guidelines_2024.json`
- **Processed Datasets:**
  - `data/processed/economic/mnre_benchmark_costs.json` (5 records)
  - `data/processed/economic/pm_surya_ghar.json` (1 policy record, 3 slabs)
- **Metadata:**
  - `data/metadata/economic/mnre_benchmark_costs_meta.json`
  - `data/metadata/economic/pm_surya_ghar_meta.json`

## 6. Known Limitations
- The PM Surya Ghar subsidy defines Central Financial Assistance (CFA). Additional state-level subsidies vary significantly and have not yet been aggregated.
- Benchmark costs reflect the 2021-22 MNRE guidelines. Actual market costs may fluctuate and are sometimes informally capped by the PM Surya Ghar benchmark proxy assumption of ₹50,000/kW.
