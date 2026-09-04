# Phase 4C - Experiment 3B: Real LLM Validation Results

## 1. Experimental Protocol
This document summarizes the execution and quantitative results of **Experiment 3B**, which aimed to validate the structural pipeline and behavioral fidelity of the `FULL_COGNITIVE_ABM` model using a live, locally hosted LLM provider (`llama3.2:3b` via Ollama) compared to the standard `DETERMINISTIC_ABM` model.

**Execution Command:**
`python run_exp3b.py`

**Configuration:**
- **Provider:** `LangGraphLLMProvider` (Local Ollama via LangChain JSON format)
- **Model Identifier:** `llama3.2:3b`
- **Population:** `100` agents
- **Timesteps:** `12` quarters
- **Seeds:** `[42, 100, 200, 300, 400]`

## 2. Historical Global-Cache Result
*Note: This data represents the previous iteration which used a `_global_cache` across all seeds. It is scientifically invalid for independent-seed variance estimation.*

| Metric | Historical / Old Global-Cache Result |
| :--- | :--- |
| **Mean Final Adoption Rate** | 5.2% |
| **Max Final Adoption Rate** | 6.0% |
| **Fraction Tipping Point Reached**| 0.0 |
| **Old Total Invocations**| 240 |
| **Old Mean Invocations per Seed** | 48 |
| **Cache Hits** | 964 |
| **Cross-Seed Reuse Events** | Hundreds |

## 3. Independence Failure
The previous `_global_cache` fundamentally violated cross-seed statistical independence. Random stochastic responses generated during Seed 42 were deterministically reused in subsequent seeds (100, 200, 300, 400) if their structural contexts matched. 

### Evaluation-Count Semantics Breakdown (Old Caching)
- **Total household decision opportunities:** 6000 (5 seeds × 100 agents × 12 timesteps)
- **Mathematical/rule-based decisions:** ~4796
- **Total cognitive evaluations (Routed to LLM Path):** 1204
- **Consistency Equation:** Total cognitive evaluations (1204) = Cache Hits (964) + Cache Misses / Real LLM Invocations (240).
Because 964 hits occurred across all 5 seeds mapped globally, the stochastic variance between seeds was completely collapsed.

## 4. Corrected Seed-Scoped Cache
The cache was corrected by removing the class-level dictionary and restoring it to an instance-scoped variable (`self._cache`) initialized uniquely for each simulation model (seed-scoped).
6 rigorous validation tests (`test_cache_audit.py`) were created to enforce this. The total test suite (46/46) confirms:
- **Within-seed reuse:** Intact. Repeated evaluations within a seed yield cache hits.
- **Cross-seed reuse:** ELIMINATED (0 occurrences). Identity includes provider, model, prompt, config, and seed boundaries.
- **Cache Scope Provenance:** `cache_scope="seed"` is now explicitly written into all JSON artifacts.

## 5. Confidence Normalization Audit
A global `NORMALIZATION_EVENTS` logging tracker was implemented for scaling artifacts in Pydantic. 
For Experiment 3B, no unrecoverable/malformed failures occurred due to the robust JSON structural prompt modification.

## 6. Per-Seed Corrected Results
| Seed | Final Adoption | LLM Invocations (Misses) | Cache Hits | Hit Rate | Tipping Count |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | 5% | 220 | 240 | 52.1% | 0 |
| **100**| 5% | 80 | 86 | 51.8% | 0 |
| **200**| 5% | 110 | 139 | 55.8% | 0 |
| **300**| 5% | 170 | 193 | 53.1% | 0 |
| **400**| 6% | 20 | 12 | 37.5% | 0 |

*(Total corrected cognitive evaluations = 1270. Total corrected cache hits = 670. Total corrected Ollama invocations = 600.)*
*(Overall pooled cache hit rate = 52.76%. Mean per-seed cache hit rate = 50.1%.)*
*(Total cognitive evaluations = cache hits + cache misses is verified for all seeds.)*

## 7. Old vs Corrected Comparison

| Metric | OLD GLOBAL-CACHE 3B | CORRECTED SEED-SCOPED 3B |
| :--- | :--- | :--- |
| **Final adoption mean** | 5.2% | 5.2% |
| **Final adoption std** | ~0.44% | ~0.44% |
| **Minimum final adoption** | 5.0% | 5.0% |
| **Maximum final adoption** | 6.0% | 6.0% |
| **Tipping count** | 0 | 0 |
| **Total provider invocations** | 240 | 600 |
| **Mean provider invocations per seed** | 48 | 120.0 |
| **Overall pooled cache hit rate** | ~80.0% | 52.76% |
| **Mean per-seed cache hit rate** | N/A | 50.1% |
| **Cross-seed cache reuse** | Hundreds | 0 |
| **LLM Failures** | 0 | 0 |
| **Mathematical Fallbacks**| 0 | 0 |

## 8. Statistical/Scientific Interpretation
The corrected protocol restored independent cache state across seeds, preventing cached LLM responses from being reused across seed boundaries.

Under the tested baseline conditions, the real local LLM produced aggregate adoption behavior close to the deterministic baseline. It effectively rejected spontaneous cascades because economic affordability parameters did not mathematically support adoption. 

## 9. Limitations
Five seeds remain statistically insufficient for broad generalization, serving merely as structural proofs of independent variance mapping prior to larger compute runs. The Real LLM evaluations were restricted to `llama3.2:3b` running natively via Ollama on local hardware.

## 10. Final Acceptance Status
**3B STATUS = FINAL**
All acceptance criteria met (cross-seed reuse = 0, explicit cache scope recorded, normalization auditable, 46/46 pytest). Authorized for Phase 4C economic sweeps.
