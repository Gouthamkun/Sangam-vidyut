# Historical / PM Surya Ghar Bridge Analysis

## Overview
This document evaluates the feasibility of bridging historical and modern residential solar adoption datasets to form a continuous validation target.

## Critical Finding on Historical Count Availability
**NO VERIFIED CONTINUOUS PRE-2024 STATE-WISE RESIDENTIAL HOUSEHOLD INSTALLATION COUNT SERIES HAS BEEN IDENTIFIED.** 

## Critical Finding on Lok Sabha UQ 1936
Lok Sabha UQ 1936 (14.12.2023) provides `Capacity till 31-10-2023 (MW)`. It represents *Total Solar Capacity* (Ground-Mounted + C&I Rooftop + Off-grid). 
- **Scientific Impact:** UQ 1936 is classified as a **P1 Target** (Total Capacity Context). It must NOT be used directly as a residential household calibration target.
- **Prohibition:** Any attempt to mathematically add UQ 1936 capacity (MW) to UQ 1698 installations (Household counts) is strictly invalid. 

## Bridging Architecture (Revised)
Because continuous homogeneous historical counts are unavailable, we cannot form a single mathematically appended target. Instead, the validation architecture spans multiple parallel targets:
1. **Modern Calibration (P0-A):** PM Surya Ghar Household Counts (Feb 2024+).
2. **Historical Validation (P0-B / P1):** Historical Phase-II Residential Capacity (MW) and Total Solar Capacity (MW).

Bridging ABM outputs across these metrics strictly requires the implementation of an empirical **Capacity Model (kW/household)** derived from official data, without which MW and Household counts remain fundamentally isolated.
