# Phase 4F.1 Execution Persistence Diagnostic

## 1. Discrepancy
The previous experiment status incorrectly reported that 180 runs had been completed and successfully evaluated. However, an audit revealed that 0 files were actually written to `outputs/experiments/phase_4f_1/raw/`. The previously stated execution count was based on submitting jobs to the execution pool and erroneously trusting in-memory completion, completely bypassing physical disk persistence validation.

## 2. Filesystem Findings
A comprehensive recursive search of the workspace for expected experiment artifacts (`experiment_results`, `trajectory_results`, manifests) returned zero results. No raw scientific artifacts were serialized to disk.

## 3. Runner Architecture & 4. Failure Point
The root cause was located in `scripts/experiments/phase_4f_1_campaign.py`. The runner utilized `joblib`'s `Parallel` execution, gathering all results in memory, and attempting a monolithic `to_csv` dump *only after all 180 runs had completed*. Because the parent process was terminated (server restart/crash) prior to the execution of `to_csv`, the entirely memory-bound result buffer was permanently lost.

## 5. Diagnostic Experiment
A single diagnostic run (2 agents, 2 timesteps) was executed in isolation via `scripts/experiments/phase_4f_1_diagnostic.py`. It confirmed that Python's file operations can successfully serialize and validate the required schema in real-time, verifying that the issue was purely architecturally bounded by the monolithic loop.

## 6. Persistence Fix
The campaign runner was structurally overhauled to enforce **Atomic Execution**:
*   Worker functions now write their own artifacts immediately upon completion.
*   Results are written to `.tmp` files and atomically renamed.
*   The parent process aggregates artifacts that have already been validated on disk, rather than relying on holding all states in memory.

## 7. Completion-State Contract
A strict contract is now enforced via `tests/integration/test_persistence_contract.py`. A run is only counted as `COMPLETED` when:
1.  The simulation finishes successfully.
2.  The JSON summary is written atomically.
3.  The CSV trajectory is written atomically.
4.  The artifact is reopened and validated successfully.
5.  Trajectory lengths mathematically correspond to the simulated timesteps.
6.  The manifest points correctly to the persisted artifact.

The runner now strictly separates `submitted`, `executed`, `persisted`, and `validated` counts, refusing to announce campaign completion unless `submitted == validated`.

## 8. Tests
Six new test cases were integrated:
- `test_single_run_persistence`
- `test_corrupted_result_detection`
- `test_missing_result_detection`
- `test_atomic_file_writing`
- `test_completion_counter_correctness`
- `test_manifest_result_mismatch`

## 9. Remaining Requirements Before Scientific Rerun
The persistence pipeline is validated. The 180-run campaign matrix is ready to be securely re-executed.
