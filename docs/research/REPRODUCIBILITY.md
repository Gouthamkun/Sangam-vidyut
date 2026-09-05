# Sangam Vidyut Reproducibility Guide

This document outlines the strict technical constraints and infrastructure used to ensure bitwise reproducibility across the Sangam Vidyut Phase 4F experiments.

## IMPORTANT DISTINCTION
- **Reproducing Existing Results**: Validating identical artifacts using the locked `config_sha256` and exact 10-matched-seed arrays.
- **Running New Experiments**: Will overwrite artifacts and invalidate Phase 4F locked boundaries. **Do not run new experiments in the locked release state.**

## Environment Lock
- **Python Version**: 3.12.4
- **Dependency Installation**: Run `pip install -r requirements-lock.txt` to instantiate the exact validated environment.

## Repository Structure
```text
src/          # Core Mesa simulation engine, agents, and LLM interfaces
experiments/  # Phase-specific execution definitions and runner logic
scripts/      # Orchestration, data generation, plotting, and execution scripts
tests/        # Pytest suite validating caching and model physics
schemas/      # Pydantic schemas enforcing output structure
docs/         # Master Research Reports, design specs, and figures
outputs/      # Persisted results (manifests, logs, aggregated CSVs)
data/         # Un-tracked raw empirical data (HCES / surveys)
```

## Reproducibility Mechanics
- **Random Seed Strategy**: All experiments utilize deterministic 10-matched-seed arrays (`[42, 43, 44, 45, 46, 47, 48, 49, 50, 51]`).
- **Configuration Hashing**: Every experiment generates a `config_sha256` mapping exactly to its invariant parameters.
- **Calibration Artifact**: The population proxy is locked to `SHA-256: 0d5acf7...`.
- **Atomic Persistence**: Experiment manifests and CSV trajectories are written atomically to prevent mid-run state corruption.
- **Invariant Checks**: Mathematical constraints (e.g. `S + I + R == N`) are explicitly validated per-timestep.
- **Test Suite**: A `pytest` suite consisting of 126 assertions continuously monitors physics and cognitive cache isolation.
- **Dashboard Launch**: `python -m streamlit run app.py` (Loads precomputed outputs. Does NOT mutate data).
