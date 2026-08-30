# Model Integration

## Decision Architecture for Consumer Agents

The decision to adopt solar panels is a function of:
- Demographic features
- Historical adoption probability
- Panel price / affordability
- Government subsidy
- Social-network exposure
- SIR influence
- LLM persona reasoning

### Candidate Integration Strategies

#### Strategy 1: LLM as Final Arbiter (The Prompted Approach)
- **Mechanism**: The deterministic variables (historical prob, price, subsidy, SIR score) are calculated mathematically and passed as a text prompt to the LangGraph LLM workflow. The LLM processes this context and makes the final boolean decision.
- **Advantages**: Captures qualitative nuances and bounded rationality accurately. Highly flexible.
- **Disadvantages**: Extremely compute-intensive. Prone to LLM hallucinations ignoring strong mathematical priors.

#### Strategy 2: Logit-Ensemble (The Mathematical Approach)
- **Mechanism**: The LLM evaluates purely qualitative inputs (persona sentiment, policy text) and outputs a scalar "Sentiment Score". This score is added as a feature alongside Price, Subsidy, and SIR influence into a final Logistic Regression equation: $P(Adopt) = \sigma(\beta_1 \cdot Stats + \beta_2 \cdot SIR + \beta_3 \cdot LLM\_Sentiment)$.
- **Advantages**: Computationally efficient. Mathematically rigorous and explicitly interpretable.
- **Disadvantages**: Rigid. It assumes linear independence between qualitative sentiment and quantitative prices.

#### Strategy 3: Threshold-Triggered Hybrid (Recommended)
- **Mechanism**: The agent uses a deterministic mathematical threshold function based on economics (Price - Subsidy) and SIR exposure. If the probability is extremely low or extremely high, the agent decides deterministically. If the probability falls in an "ambiguous middle band" (e.g., $0.4 < P < 0.6$), the LangGraph LLM is invoked to break the tie using bounded-rationality reasoning.
- **Advantages**: Blends mathematical rigor with LLM nuance. Highly cost-effective (LLM only called for edge cases). Modular.
- **Disadvantages**: Requires careful tuning of the threshold bounds.

**Recommendation**: **Strategy 3 (Threshold-Triggered Hybrid)** will be used for the first implementation to manage compute costs while retaining the capability to model complex human reasoning at critical decision boundaries.

---

## SIR Model Interpretation

The standard epidemiological SIR (Susceptible, Infected, Recovered) model is adapted for technology diffusion as follows:

- **S (Susceptible)**: Households that have not adopted solar and have minimal exposure to the technology.
- **I (Infected/Adopting)**: Households that have recently adopted solar panels. They actively "infect" their neighbors by sharing their positive experience, showing off the panels, or discussing savings.
- **R (Recovered/Inactive)**: Households that adopted solar long ago. Their novelty has worn off, and they no longer actively promote it to neighbors (they stop "infecting").

### Limitations & Assumptions
- **Assumption**: Adoption spreads via direct network ties.
- **Limitation**: The model assumes "Recovery" means stopping advocacy, but in reality, a visible solar panel is a permanent passive influence, which standard SIR struggles to model perfectly (SIS or SI models might be mathematically closer, but SIR allows for the temporal decay of active word-of-mouth). This limitation will be documented and evaluated against baselines.
