import time
import uuid
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath("."))
from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
import pandas as pd

class LiveSimulationRunner:
    def __init__(self, **kwargs):
        self.config = ExperimentConfig()
        
        self.initial_adoption = 5 # Default in model
        
        # Apply parameters
        if "subsidy" in kwargs:
            self.config.government.base_subsidy = float(kwargs["subsidy"])
        if "beta" in kwargs:
            self.config.sir.beta = float(kwargs["beta"])
        if "population" in kwargs:
            self.config.simulation.n_agents = int(kwargs["population"])
        if "horizon" in kwargs:
            self.config.simulation.timesteps = int(kwargs["horizon"])
        if "seed" in kwargs:
            self.config.simulation.seed = int(kwargs["seed"])
        if "budget" in kwargs:
            self.config.government.initial_budget = float(kwargs["budget"])
        if "recovery" in kwargs:
            self.config.sir.recovery_duration_quarters = int(kwargs["recovery"])
        if "initial_adoption" in kwargs:
            self.initial_adoption = int(kwargs["initial_adoption"])
            
        if "topology" in kwargs:
            self.config.network.topology = kwargs["topology"]
        if "household_mode" in kwargs:
            self.config.simulation.baseline_provider = kwargs["household_mode"]
        if "policy_mode" in kwargs:
            self.config.government.dynamic_subsidy = (kwargs["policy_mode"] == "dynamic")
            
        if "cognitive_mode" in kwargs:
            if kwargs["cognitive_mode"] == "deterministic":
                self.config.llm.enabled = False
                # Single rule-based threshold at the empirically-calibrated boundary (0.20).
                # This eliminates the ambiguous zone (no LLM calls) while permitting
                # rule-based adoption when score >= 0.20. The value 0.20 matches the
                # upper_threshold of the cognitive_accessible_candidate_v1 policy.
                self.config.cognitive.lower_threshold = 0.20
                self.config.cognitive.upper_threshold = 0.20
            elif kwargs["cognitive_mode"] == "mock":
                self.config.llm.provider = "mock"
            elif kwargs["cognitive_mode"] == "ollama":
                self.config.llm.provider = "langgraph"
                self.config.llm.model = "llama3.2:3b"

    def run(self):
        start_time = time.time()
        model = SangamVidyutModel(self.config)
        self._model = model
        
        if self.config.simulation.baseline_provider == "empirical":
            from src.simulation.agents.adapters import create_consumer_from_household_record
            from src.simulation.agents.consumer import ConsumerAgent
            
            seed = self.config.simulation.seed
            pop_path = f'data/processed/households/synthetic/population_500_seed_{seed}.parquet'
            if not os.path.exists(pop_path):
                pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
                
            pop_df = pd.read_parquet(pop_path).head(self.config.simulation.n_agents)
            
            # Remove default mock consumer agents
            for agent in list(model.agents):
                if isinstance(agent, ConsumerAgent):
                    if hasattr(agent, 'pos') and agent.pos is not None:
                        model.grid.remove_agent(agent)
                    model.agents.remove(agent)
                    
            # Inject synthetic agents
            for i, row in pop_df.iterrows():
                agent = create_consumer_from_household_record(model, row)
                model.grid.place_agent(agent, i)
        
        # Override initial adoption safely (works for both empirical and constant)
        for a in model.agents:
            if hasattr(a, 'is_adopter'):
                a.is_adopter = False
                a.sir_state = 0
        
        initial_nodes = np.random.choice(model.G.nodes(), size=self.initial_adoption, replace=False)
        for node in initial_nodes:
            agent_list = model.grid.get_cell_list_contents([node])
            for a in agent_list:
                if hasattr(a, 'is_adopter'):
                    a.is_adopter = True
                    a.sir_state = 1
                    
        # Update the already collected step 0 data
        if "adoption_count" in model.datacollector.model_vars:
            model.datacollector.model_vars["adoption_count"][0] = self.initial_adoption
            model.datacollector.model_vars["infected_count"][0] = self.initial_adoption
            model.datacollector.model_vars["susceptible_count"][0] = self.config.simulation.n_agents - self.initial_adoption
            model.datacollector.model_vars["adoption_rate"][0] = self.initial_adoption / self.config.simulation.n_agents

        horizon = self.config.simulation.timesteps
        for step in range(horizon):
            model.step()
        
        df = model.datacollector.get_model_vars_dataframe()
        
        # FIX THE EXTRACTION LAYER: 
        # Mesa collects before incrementing, so the index is 0, 0, 1, 2...
        df["timestep"] = range(len(df))
        
        # FIX TEMPORAL SEMANTICS:
        # new_adoptions is reported as new_adoptions_last_step by the Mesa collector.
        # This means df["new_adoptions"] is lagged by 1 relative to df["adoption_count"].
        # We shift it backward by 1 to align it with the timestep the adoption actually occurred.
        df["new_adoptions"] = df["new_adoptions"].shift(-1).fillna(0)
        
        # Recalculate true coherent expenditure aligned with the event boundary
        # Rather than relying on the lagging government.budget from the next step's start.
        df["step_expenditure"] = df["new_adoptions"] * df["subsidy"]
        df["cumulative_expenditure"] = df["step_expenditure"].cumsum()
        df["budget_remaining"] = self.config.government.initial_budget - df["cumulative_expenditure"]
        
        run_id = str(uuid.uuid4())[:8].upper()
        
        metrics = {
            "call_count": getattr(model.llm_interface.provider, "call_count", 0) if hasattr(model, "llm_interface") and hasattr(model.llm_interface, "provider") else 0,
            "rule_decisions": getattr(model, "step_rule_decisions", 0),
        }
        
        return {
            "run_id": run_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": self.config,
            "df": df,
            "final_adoption": df["adoption_count"].iloc[-1],
            "metrics": metrics,
            "execution_time": time.time() - start_time
        }
