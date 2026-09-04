# Phase 4F.1D Provenance Validation

## 1. Discovery
During the final manifest validation check of the 180 runs from the Phase 4F.1 rerun, 180 out of 180 manifests were flagged as INVALID because they lacked the `calibration_artifact_sha256` field. This breached the strict provenance contract linking scientific output files dynamically back to the exact empirical model state deployed.

## 2. Root Cause
The initial `atomic_write_json` manifest generator failed to embed the `calibration_artifact_sha256` field natively because the JSON generator schema defined in the pre-flight check had not been strictly injected into the 4F.1 campaign loop script. The script was appending `calibration_hash`, rather than the mandated `calibration_artifact_sha256`, and failed to discriminate usage semantics between `EMPIRICAL` and `CONSTANT` evaluations.

## 3. Manifest Schema
The schema was updated in-place via a localized repair script. It now includes:
- `calibration_artifact_sha256`
- `calibration_artifact_note`
- `provider`
- `baseline_provider`
- `summary_sha256`
- `trajectory_sha256`
alongside `run_id`, `experiment_id`, `model_class`, `topology`, `beta`, `subsidy`, `seed`, `population_size`, `horizon`, and `config_hash`.

## 4. Calibration Provenance
The static empirical calibration artifact (`outputs/calibration/selected_model/empirical_baseline.json`) was independently hashed via SHA-256 and confirmed exactly as `0d5acf7ef798ebd814d6a6431f9b9f1da36789c0225120f4468d78c2e9f1d241`.

## 5. Repair Method
A standalone script (`scripts/experiments/phase_4f_1d_repair.py`) was executed to:
1. Identify the baseline provider mechanism from the experiment setup (constant vs empirical).
2. Insert `calibration_artifact_sha256` into each manifest.
3. Assert a `null` value with explanatory note for `CONSTANT` baseline runs where the artifact mean was technically utilized before the simulation rather than evaluated independently during the run.
4. Add `provider` and `baseline_provider` tracking.
5. Create raw SHA-256 fingerprint linkage to summary/trajectory artifacts.

## 6. Raw Artifact Validation
Every single raw artifact was hashed and appended into the manifest JSON to form a complete atomic contract.

## 7. Summary/Trajectory Validation
Trajectory output arrays were checked against:
- `susceptible_count` + `infected_count` + `recovered_count` == N (invariant)
- Monotonic/bounds constraints
- No Negative/NaN/Inf counts
- Consistency checking against identical final adoption in `_summary.json`
- 100% of the 180 runs passed trajectory validation.

## 8. Run Accounting
- **Planned runs:** 180
- **Manifest count:** 180
- **Summary count:** 180
- **Trajectory count:** 180
- **Fully validated runs:** 180
- **Invalid runs:** 0

## 9. Provider Provenance
- Standard empirical and static runs are logged with `N/A` LLM provider.
- Cognitive runs (`HYBRID_COGNITIVE_ABM`) are correctly logged as `MockLLM` with `empirical` baseline.

## 10. Scientific-output Immutability
Absolutely zero scientific records, counts, results, trajectories, or model configurations were altered. Only the uncoupled manifest files and metadata logic strings were repaired.

## 11. Tests
`tests/integration/test_manifest_provenance.py` successfully added, asserting the exact frozen calibration SHA-256 and structural semantic integrity of all 180 parsed manifests.

## 12. Final Validation Status
The 180-run Phase 4F.1 experimental campaign successfully adheres to the full provenance and validation schema.
