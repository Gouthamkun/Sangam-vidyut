import os
import json
import mesa
import pandas as pd
import numpy as np
from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.consumer import ConsumerAgent
from src.simulation.agents.adapters import create_consumer_from_household_record

OUT_DIR = 'outputs/validation/phase_4e_3'

def setup_synthetic_model(config: ExperimentConfig) -> SangamVidyutModel:
    model = SangamVidyutModel(config)
    seed = config.simulation.seed
    pop_path = f'data/processed/households/synthetic/population_500_seed_{seed}.parquet'
    if not os.path.exists(pop_path):
        pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
    pop_df = pd.read_parquet(pop_path).head(config.simulation.n_agents)
    
    for agent in list(model.agents):
        if isinstance(agent, ConsumerAgent):
            if hasattr(agent, 'pos') and agent.pos is not None:
                model.grid.remove_agent(agent)
            model.agents.remove(agent)
            
    for i, row in pop_df.iterrows():
        agent = create_consumer_from_household_record(model, row)
        model.grid.place_agent(agent, i)
        
    initial_nodes = np.random.choice(model.G.nodes(), size=5, replace=False)
    for node in initial_nodes:
        agent_list = model.grid.get_cell_list_contents([node])
        for a in agent_list:
            if isinstance(a, ConsumerAgent):
                a.is_adopter = True
                a.sir_state = 1
    return model

def run_sensitivity():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 1. We will override weights and thresholds in ConsumerAgent.step
    # Wait, weights are hardcoded in ConsumerAgent.step:
    # score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
    # Since I'm not allowed to permanently modify the production configuration yet, 
    # I will dynamically monkey-patch the step function just for this test!
    pass

# We will monkey patch ConsumerAgent.step to accept dynamic weights
original_step = ConsumerAgent.step

def get_patched_step(w_base, w_sir, w_aff, lower, upper):
    def patched_step(self):
        # 1. Update SIR timer if currently infected
        if self.sir_state == 1:
            self.time_infected += 1
            if self.time_infected >= self.model.config.sir.recovery_duration_quarters:
                self.sir_state = 2
                
        # 2. Make adoption decision if susceptible
        if not self.is_adopter:
            # Mathematical probability calculation
            if getattr(self.model, "baseline_provider", None) is not None:
                p_base = self.model.baseline_provider.predict(self)
            else:
                features = pd.DataFrame([[self.income, self.home_owner]])
                p_base = self.model.baseline_model.predict_proba(features)[0]
            
            # SIR/Social influence score
            neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
            infected_neighbors = 0
            
            for item in neighbors:
                if isinstance(item, mesa.Agent):
                    if getattr(item, 'sir_state', 0) == 1:
                        infected_neighbors += 1
                else:
                    agents_in_cell = self.model.grid.get_cell_list_contents([item])
                    for a in agents_in_cell:
                        if isinstance(a, ConsumerAgent) and getattr(a, 'sir_state', 0) == 1:
                            infected_neighbors += 1
                        
            sir_score = 1.0 - (1.0 - self.model.config.sir.beta) ** infected_neighbors
            
            current_subsidy = self.model.current_subsidy
            current_price = self.model.current_panel_price
            affordability = min(current_subsidy / max(current_price, 1.0), 1.0)
            
            # --- PATCHED SCORE ---
            score = w_base * p_base + w_sir * sir_score + w_aff * affordability
            self.adoption_probability = score
            
            decision = False
            
            # --- PATCHED THRESHOLDS ---
            lower_thresh = lower
            upper_thresh = upper
            
            if score >= upper_thresh:
                decision = True
                self.decision_path = "rule"
                self.model.step_rule_decisions += 1
            elif score <= lower_thresh:
                decision = False
                self.decision_path = "rule"
                self.model.step_rule_decisions += 1
            else:
                context = {
                    "agent_id": self.unique_id, "timestep": self.model.timestep,
                    "income": self.income, "home_owner": self.home_owner,
                    "sir_score": sir_score, "affordability": affordability,
                    "combined_score": score, "panel_price": current_price,
                    "subsidy": current_subsidy, "adopting_neighbors": infected_neighbors,
                    "total_neighbors": len(neighbors),
                    "prompt_version": self.model.config.llm.prompt_version,
                    "model_identifier": self.model.config.llm.model,
                    "provider": self.model.config.llm.provider,
                    "temperature": self.model.config.llm.temperature
                }
                try:
                    decision = self.model.llm_interface.decide(context)
                    self.decision_path = "llm"
                    self.model.step_llm_decisions += 1
                except Exception as e:
                    pass
            
            if decision:
                self.is_adopter = True
                self.sir_state = 1
                self.time_infected = 0
                self.model.new_adoptions += 1
    return patched_step

def run_experiment(w_base, w_sir, w_aff, lower, upper, provider="empirical"):
    ConsumerAgent.step = get_patched_step(w_base, w_sir, w_aff, lower, upper)
    
    config = ExperimentConfig()
    config.simulation.baseline_provider = provider
    config.simulation.timesteps = 4
    config.llm.enabled = True
    config.llm.provider = "mock"
    
    model = setup_synthetic_model(config)
    
    for _ in range(4):
        model.step()
        
    df = model.datacollector.get_model_vars_dataframe()
    final_rate = float(df["adoption_rate"].iloc[-1])
    total_rule = int(df["step_rule_decisions"].sum())
    total_llm = int(df["step_llm_decisions"].sum())
    
    # Calculate reachability fractions
    scores = []
    for a in model.agents:
        if isinstance(a, ConsumerAgent):
            scores.append(getattr(a, 'adoption_probability', 0.0))
            
    scores = np.array(scores)
    llm_reachable = np.mean((scores > lower) & (scores < upper))
    auto_reachable = np.mean(scores >= upper)
    
    return {
        "w_base": w_base, "w_sir": w_sir, "w_aff": w_aff,
        "lower_thresh": lower, "upper_thresh": upper,
        "provider": provider,
        "llm_reachable_frac": float(llm_reachable),
        "auto_reachable_frac": float(auto_reachable),
        "max_score": float(np.max(scores)),
        "median_score": float(np.median(scores)),
        "p90_score": float(np.percentile(scores, 90)),
        "final_adoption": final_rate,
        "llm_calls": total_llm
    }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    weights = [
        (0.4, 0.4, 0.2), # Legacy
        (0.8, 0.1, 0.1), # Baseline heavy
        (1.0, 0.0, 0.0), # Pure empirical
        (0.34, 0.33, 0.33) # Balanced
    ]
    
    thresholds = [
        (0.3, 0.7),     # Legacy
        (0.1, 0.3),     # Moderately lower
        (0.05, 0.15),   # Lowered
        (0.01, 0.05),   # Scaled to empirical
        (0.001, 0.01)   # Hyper sensitive
    ]
    
    results = []
    
    print("Running Phase C and D experiments...")
    for w in weights:
        for t in thresholds:
            for prov in ["legacy", "empirical"]:
                res = run_experiment(w[0], w[1], w[2], t[0], t[1], prov)
                results.append(res)
                
    # Restore original method
    ConsumerAgent.step = original_step
    
    df = pd.DataFrame(results)
    
    df.to_csv(f"{OUT_DIR}/parameter_sensitivity.csv", index=False)
    
    # Extract legacy vs empirical matched comparison
    comp_df = df.copy()
    comp_df.to_csv(f"{OUT_DIR}/legacy_vs_empirical.csv", index=False)
    
    print("Phase C and D complete.")

if __name__ == '__main__':
    main()
