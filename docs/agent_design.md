# Agent Architecture

This document defines the responsibilities, inputs, states, decisions, and outputs for all entities in the Sangam Vidyut simulation.

## 1. Consumer Agent
- **Responsibilities**: Represents a household making decisions about solar adoption.
- **Inputs**: Demographic features, historical probability, panel prices, subsidies, neighbor states (SIR exposure).
- **State**: `Adopted` (Boolean), `Budget`, `Social Influence Score`, `LLM Persona`.
- **Decision**: To adopt solar panels in the current time-step or wait.
- **Outputs**: State change broadcast to neighbors.
- **Interaction with Mesa**: Occupies a node in `NetworkGrid`, stepped by Mesa scheduler.
- **Interaction with LangGraph**: Invokes LangGraph for complex reasoning when exposed to strong triggers.

## 2. Government Agent
- **Responsibilities**: Represents policymakers adjusting subsidies to meet adoption targets.
- **Inputs**: Current simulation adoption rate, budget constraints.
- **State**: `Current Policy`, `Available Funds`.
- **Decision**: Whether to increase, decrease, or maintain solar subsidies.
- **Outputs**: Updated policy parameters distributed globally.
- **Interaction with Mesa**: Single agent stepped by Mesa; modifies global environment variables.
- **Interaction with LangGraph**: Evaluates policy effectiveness and public sentiment using LangGraph reasoning workflows.

## 3. Industry Agent
- **Responsibilities**: Represents the supply side and market forces.
- **Inputs**: Global panel prices (IRENA via LSTM), local demand from Consumer agents.
- **State**: `Current Market Price`, `Technology Efficiency`.
- **Decision**: Adjust pricing dynamically based on demand spikes.
- **Outputs**: New cost parameters for solar panels.
- **Interaction with Mesa**: Single agent; updates global price variables.
- **Interaction with LangGraph**: May use LangGraph to model bounded-rationality pricing strategies, otherwise heavily reliant on LSTM output.

## 4. Environment Agent
- **Responsibilities**: Tracks the ecological impact of the simulation.
- **Inputs**: Aggregate adoption counts from Consumer agents, regional carbon factors.
- **State**: `Total Emissions Mitigated`.
- **Decision**: Purely computational (no active decisions).
- **Outputs**: Cumulative carbon offset metrics.
- **Interaction with Mesa**: Observer agent.
- **Interaction with LangGraph**: N/A (strictly deterministic).

## 5. Analysis Agent
- **Responsibilities**: Monitors the simulation for cascading phenomena and tips in the network.
- **Inputs**: Step-by-step state of the `NetworkGrid`.
- **State**: `Cascade Detected` (Boolean), `Growth Derivative`.
- **Decision**: Flags when the network crosses a tipping point.
- **Outputs**: Analytics logs, Cascade warnings.
- **Interaction with Mesa**: Observer agent.
- **Interaction with LangGraph**: N/A (strictly statistical/mathematical).
