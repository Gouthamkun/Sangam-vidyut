# Final Project Map

```text
DATA (HCES, CEA, MNRE)
       ↓
  CALIBRATION (Aggregate-Ecological)
       ↓
HOUSEHOLD AGENTS (ConsumerAgent)
       ↓
ECONOMIC DECISION (0.4*p_base + 0.4*SIR + 0.2*affordability)
       ↓
  NETWORK / SIR (Watts-Strogatz / Barabási-Albert)
       ↓
POLICY / INDUSTRY / ENVIRONMENT (Feedback Loops)
       ↓
OPTIONAL COGNITIVE ROUTING (LangGraph Ambiguity Filter)
       ↓
EXPERIMENT ENGINE (Mesa Orchestrator)
       ↓
    ANALYSIS (Aggregation & Provenance)
       ↓
    FIGURES (Matplotlib/Plotly)
       ↓
   DASHBOARD (Streamlit - app.py)
       ↓
REPORT / PORTFOLIO (Synthesis Documents)
```
