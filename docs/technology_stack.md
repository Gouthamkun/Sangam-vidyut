# Technology Stack

This document outlines the core technologies used in Sangam Vidyut, explaining their role, data flow, and interactions.

### Python
- **Why**: Standard language for data science, modeling, and scientific computing.
- **Role**: Core programming language.
- **Input/Output**: N/A
- **Connection**: Hosts all frameworks and scripts.

### Mesa
- **Why**: Python framework specifically designed for Agent-Based Modeling (ABM).
- **Role**: Provides the grid/network space, scheduling mechanism, and base agent classes.
- **Input**: Agent initialization parameters, NetworkX graph.
- **Output**: Step-by-step state changes of all agents.
- **Connection**: Drives the simulation core; connects with LangGraph for agent decision orchestration.

### LangGraph
- **Why**: Provides robust orchestration for LLM-powered workflows and state machines.
- **Role**: Manages the complex multi-step reasoning and interaction sequences of Consumer, Government, and Industry agents.
- **Input**: Agent states, environmental context, prompts.
- **Output**: Agent decisions (e.g., "Adopt Solar", "Wait").
- **Connection**: Integrated within Mesa's step function to drive intelligent agent behavior.

### NetworkX
- **Why**: Industry standard for complex network creation and graph analysis.
- **Role**: Constructs and manages the social network graph of households.
- **Input**: Household Social Network Graph Data.
- **Output**: Graph object with nodes (households) and edges (social connections).
- **Connection**: Feeds directly into Mesa's `NetworkGrid` and the SIR diffusion model.

### Scikit-learn (Logistic Regression)
- **Why**: Reliable, interpretable statistical modeling.
- **Role**: Calibrates baseline adoption rates and probability scores.
- **Input**: MNRE historical adoption records, demographic features.
- **Output**: Base adoption probability.
- **Connection**: Fed into Consumer agents as a foundational trait before LLM reasoning and SIR diffusion take over.

### PyTorch / LSTM (Long Short-Term Memory)
- **Why**: Excellent at modeling time-series and sequence data.
- **Role**: Forecasts price-demand responses based on historical trends.
- **Input**: IRENA Panel Pricing & Technology Cost Data.
- **Output**: Predicted future panel prices.
- **Connection**: Consumed by the Industry Agent to set simulation market prices.

### SIR Diffusion Model (Susceptible-Infected-Recovered)
- **Why**: Classic epidemiological model, well-suited for modeling the spread of ideas/technology in a network.
- **Role**: Models the pure peer-to-peer viral spread of solar adoption.
- **Input**: NetworkX graph, current adoption states ("Infected").
- **Output**: Probabilistic "exposure" scores for non-adopters.
- **Connection**: Combines with LLM persona logic to finalize consumer adoption decisions.

### LLM APIs (e.g., Gemini / OpenAI)
- **Why**: Provides nuanced, persona-driven decision-making that traditional statistics cannot capture (e.g., sentiment, complex policy interpretation).
- **Role**: Powers the cognitive layer of Consumer, Government, and Analysis agents.
- **Input**: Demographic prompts, policy rules, peer pressure context.
- **Output**: Behavioral decisions, natural language reasoning.
- **Connection**: Orchestrated via LangGraph within the Mesa framework.

### Pandas & NumPy
- **Why**: Fundamental data manipulation and numerical computation.
- **Role**: Data cleaning, preprocessing, and array operations.
- **Input**: Raw CSV/JSON datasets.
- **Output**: Clean DataFrames and tensors.
- **Connection**: Feeds into Scikit-learn, PyTorch, and initialization scripts.

### Matplotlib / Plotly / Streamlit
- **Why**: High-quality visualization and interactive dashboarding.
- **Role**: Renders the downstream analysis.
- **Input**: Simulation output logs, regression outputs.
- **Output**: Charts, interactive web UI (Streamlit).
- **Connection**: The final layer in the pipeline, consuming data from the Downstream Analysis modules.
