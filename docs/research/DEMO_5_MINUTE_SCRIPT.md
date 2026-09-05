# Sangam Vidyut — 5-Minute Demo Script

## Speaker Notes & Timeline

### 0:00–0:30 — PROBLEM (30 sec)
**Screen/Action**: Title Slide or initial README view.
**Spoken Script**: "Hi, I'm presenting Sangam Vidyut. I wanted to understand what happens when rooftop-solar adoption is driven not only by economics, but also by differences between individual households and their social influence on each other."
**Emphasize**: *not only by economics*, *differences between individual households*.

### 0:30–1:00 — RESEARCH QUESTION (30 sec)
**Screen/Action**: Transition to Research Question slide or remain on title.
**Spoken Script**: "The core question was: Can bottom-up household interactions create nonlinear adoption behavior that aggregate or static models might not explicitly represent? Specifically, what happens when network dynamics hit rigid macroeconomic limits?"
**Emphasize**: *bottom-up household interactions*, *nonlinear adoption behavior*.

### 1:00–1:45 — WHAT I BUILT (45 sec)
**Screen/Action**: Display `docs/figures/figure_01_architecture.png`.
**Spoken Script**: "To answer this, I built an Agent-Based Model in Python using Mesa and NetworkX. It consists of Consumer Agents who evaluate personalized adoption scores using SIR network diffusion, interacting with a Government Agent that controls a finite fiscal budget, and an Industry Agent that drops prices when demand is low. There is also an optional LangGraph LLM routing layer strictly for bounded ambiguity."
**Emphasize**: *Agent-Based Model*, *finite fiscal budget*, *SIR network diffusion*.

### 1:45–2:20 — DATA + CALIBRATION (35 sec)
**Screen/Action**: Display `docs/figures/figure_02_calibration.png`.
**Spoken Script**: "The model is grounded in the HCES 2023–24 dataset. Using survey weights, I extracted Monthly Per Capita Expenditure to build synthetic Indian households, and bounded them against PM Surya Ghar targets and CEA denominators. I want to explicitly state: the household calibration is aggregate-consistent and ecological; this is not a causal household-level identification."
**Emphasize**: *HCES 2023-24*, *aggregate-consistent*, *not a causal identification*.

### 2:20–3:25 — LIVE DASHBOARD (65 sec)
**Screen/Action**: Open `http://localhost:8501`. 
- **Action A**: Select "Phase 4F.2" in sidebar.
- **Action B**: Scroll to "Factor Analysis" and point out the Subsidy Response curve showing the three Regimes.
- **Action C**: Toggle Topology between Watts-Strogatz and Barabási-Albert to show conditional changes.
- **Action D**: Switch to "Phase 4F.3" in the sidebar.
- **Action E**: Point to the Main Adoption Chart comparing Fixed vs Target-seeking dynamic policy.
- **Action F**: Highlight the "Total Expenditure" and "Budget Remaining" KPI cards.
**Spoken Script**: "Here is the interactive dashboard visualizing our locked experimental results. Notice the subsidy response curve: we see clear regimes—an affordability-blocked zone, a diffusion-active zone, and a saturated zone. If I change the topology, the effect only emerges conditionally inside that active regime. Moving to Phase 4F.3, we can directly compare a fixed policy against a target-seeking dynamic policy, tracking exactly how fast the government budget exhausts."
**Emphasize**: *locked experimental results*, *conditionally*, *budget exhausts*.

### 3:25–4:20 — KEY FINDINGS (55 sec)
**Screen/Action**: Show Evidence Badges on the Dashboard.
**Spoken Script**: "Our 560-run and 320-run campaigns revealed three things. First (Phase 4F.1), affordability is an absolute bottleneck—this is SUPPORTED. Second (Phase 4F.2), topology, beta, and household heterogeneity only become active conditionally within the diffusion-active regime—this is CONDITIONALLY SUPPORTED. Third (Phase 4F.3), policy outcomes are violently dependent on finite budgets. Interestingly, the hypothesis that dynamic models always outperform static models was NOT SUPPORTED. Also, the hypothesis that LLMs provide an aggregate cognitive advantage was NOT SUPPORTED."
**Emphasize**: *SUPPORTED*, *CONDITIONALLY SUPPORTED*, *NOT SUPPORTED*.

### 4:20–4:45 — BUDGET–NETWORK PARADOX (25 sec)
**Screen/Action**: Show `docs/figures/figure_11_budget_feedback.png` or the Budget Paradox Panel on the dashboard.
**Spoken Script**: "This leads to our most memorable finding: The Budget-Network Paradox. Rapid early network adoption accelerates subsidy expenditure, causing early budget exhaustion and a subsidy collapse. Conversely, slower early adoption preserves the budget, allowing industry prices to decline further, which ultimately enables a delayed mass adoption. This is an emergent mechanism of the tested computational model, not a universal economic law."
**Emphasize**: *emergent mechanism*, *not a universal economic law*.

### 4:45–5:00 — CLOSE (15 sec)
**Screen/Action**: Final slide / README hero.
**Spoken Script**: "To conclude, Sangam Vidyut is a computational laboratory for studying how affordability, household heterogeneity, social networks, finite policy budgets, and industry response interact. Note that experiments rely on N=500 synthetic networks and ecological calibration, so it serves as a theoretical testbed rather than a causal national forecast. Thank you."
**Emphasize**: *computational laboratory*, *theoretical testbed*.

---

## Live Dashboard Sequence Instructions
1. Open `http://localhost:8501`.
2. **Sidebar**: Set Phase to "Phase 4F.2".
3. **Main View**: Scroll to the "Subsidy Response Panel". Hover to show the red/orange/green zones (Blocked, Active, Saturated).
4. **Sidebar**: Toggle "Topology" between `watts_strogatz` and `barabasi_albert`. Show how the Topology Panel bar charts shift.
5. **Sidebar**: Change Phase to "Phase 4F.3".
6. **Main View**: Point to the "Main Adoption Chart" to show the Fixed vs Dynamic trajectory lines intersecting the 50% target.
7. **Main View**: Point out the KPI metrics at the top to highlight "Total Expenditure".
8. **Main View**: Scroll down to "The Budget Paradox Panel" to visually reinforce the final presentation point.

---

## Interview Questions & Answers

**Q1: Why ABM instead of system dynamics?**
A: System dynamics is great for macro-flows, but it structurally smooths over localized clustering. ABMs allow us to model explicit, discrete network contagion where a household is influenced precisely by its direct neighbors.

**Q2: Why SIR for solar?**
A: Solar adoption exhibits strong spatial and social peer effects (contagion). Susceptible-Infectious-Recovered allows us to model a household adopting (infected), enthusiastically talking about it for a few months (infectious), and then normalizing it (recovered).

**Q3: Why synthetic networks?**
A: We lacked empirical household-level geospatial relationship data. Small-world (Watts-Strogatz) and scale-free (Barabási-Albert) networks provide rigorously understood baselines to test social geometries.

**Q4: Why HCES?**
A: The Household Consumption Expenditure Survey (2023-24) is the most robust, recent empirical dataset for modeling the Indian economic distribution, capturing the specific wealth proxies (MPCE) needed to estimate affordability.

**Q5: How was calibration done?**
A: We used an aggregate-consistent ecological calibration. We survey-weighted the HCES data to build a synthetic population and matched baseline adoption propensities against macro CEA/MNRE targets, rather than attempting causal household-level labeling.

**Q6: Why did static sometimes outperform ABM?**
A: The Budget-Network Paradox. The ABM's early network clustering caused rapid adoption, which prematurely exhausted the finite government budget and stalled the cascade. The static model's slow early adoption conserved the budget until industry prices dropped, allowing everyone to adopt later.

**Q7: What is the budget paradox?**
A: It is the model-specific emergent observation that rapid early success (via social clustering) can fundamentally destroy long-term adoption if it triggers premature fiscal exhaustion before industry prices have had time to fall.

**Q8: What did the LLM actually do?**
A: It acted as an optional cognitive-routing layer to resolve boundedly rational ambiguity (scores between 0.05 and 0.20), replacing a pure random-number generator with a computational architecture evaluation.

**Q9: Why MockLLM?**
A: For scale and determinism. Running 1.1 million evaluations across 1,060 multi-threaded runs required an algorithmic proxy to perfectly validate the caching and multiprocessing architecture without API rate limits or stochastic pollution.

**Q10: How was cache leakage prevented?**
A: The cache key was explicitly bound to the specific integer seed of the run. This guaranteed that identical intra-run contexts were intercepted, but cross-seed contamination was completely impossible.

**Q11: How was reproducibility enforced?**
A: Strict 10-matched-seed arrays (`[42...51]`), configuration `SHA-256` hashing, calibration bindings, atomic JSON/CSV persistence to prevent mid-run corruption, and a suite of 126 `pytest` invariants.

**Q12: What would you improve next?**
A: Scaling to N=100,000+ populations, integrating real geospatial social-network data, and empirically calibrating the beta transmission rate rather than relying on theoretical parameterization.

---

## One-Minute Pitch
"I wanted to understand what happens when rooftop-solar adoption is driven not only by top-down economics, but by bottom-up household differences and social influence. I built an India-calibrated Agent-Based Model integrating SIR network diffusion with finite government budgets. In doing so, I discovered a surprising Budget-Network Paradox: models that ignore social clustering artificially preserve their budgets, mathematically overstating final adoption. Sangam Vidyut contributes a rigorous, reproducible computational testbed to explore these precise, regime-dependent phase transitions."

---

## Resume Bullets
- Engineered an India-calibrated household Agent-Based Model integrating SIR social network diffusion with macro-level policy and industry feedback loops.
- Orchestrated reproducible 560-run and 320-run experimental campaigns evaluating topological sensitivity and dynamic policy robustness under finite fiscal constraints.
- Developed a highly concurrent, seed-isolated cognitive caching architecture capable of deterministically routing millions of ambiguous decisions.
- Designed a rigorous research infrastructure validated by 126 automated tests, atomic artifact persistence, and configuration SHA-256 hashing to guarantee bitwise reproducibility.
