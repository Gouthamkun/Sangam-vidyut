# Major Research Assumptions

To construct the Sangam Vidyut simulation, several modeling assumptions must be made and explicitly acknowledged:

## 1. Demographic Representativeness
- **Assumption**: The provided Census/NSSO data accurately reflects the socioeconomic distribution of the target population.
- **Implication**: Any biases in the input data will propagate into the persona generation and baseline adoption rates.

## 2. Rationality and Bounded Rationality
- **Assumption**: Consumer agents behave with bounded rationality; they are influenced by economic factors (LSTM prices, government subsidies) but their final decisions are heavily mediated by social networks (SIR) and heuristic reasoning (LLMs).
- **Implication**: Agents may not always make mathematically optimal financial decisions, mimicking real human behavior.

## 3. SIR Applicability to Technology Diffusion
- **Assumption**: The spread of solar technology adoption follows a pattern analogous to viral contagion, where exposure to adopting neighbors increases the probability of adoption.
- **Implication**: The network topology (NetworkX graph) will be a primary driver of tipping points and cascades.

## 4. Orthogonality of Statistical and LLM Models
- **Assumption**: Baseline adoption probabilities (Logistic Regression) and LLM persona decisions can be mathematically or logically combined without invalidating either model.
- **Implication**: We assume a hybrid cognitive architecture where the ML models provide base priors, and LLMs handle edge-case reasoning and sentiment.

## 5. Exogenous vs Endogenous Variables
- **Assumption**: Government subsidies can be dynamically altered by the Government Agent (endogenous), while fundamental global silicon prices are forecasted exogenously via LSTM based on IRENA data.
- **Implication**: The Industry agent acts mostly as a passthrough for exogenous trends, while the Government agent actively reacts to simulation states.

## 6. Synthetic Data Validity
- **Assumption**: Where real data is unavailable (e.g., highly granular household social networks), synthetic graphs (like Barabasi-Albert or Watts-Strogatz) provide a sufficiently realistic approximation of human social clustering.
- **Implication**: Care must be taken to separate conclusions drawn from synthetic graphs versus empirical graphs.
