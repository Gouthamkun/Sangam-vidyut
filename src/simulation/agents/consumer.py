import mesa
import pandas as pd

class ConsumerAgent(mesa.Agent):
    """
    Consumer agent representing a household.
    Implements a hybrid decision architecture:
    Mathematical Score -> If Ambiguous -> LLM Interface -> Final Decision.
    """
    def __init__(self, model, income: float, home_owner: int):
        super().__init__(model)
        self.income = income
        self.home_owner = home_owner
        
        self.is_adopter = False
        self.sir_state = 0  # 0: S, 1: I, 2: R
        self.time_infected = 0
        self.adoption_probability = 0.0
        self.decision_path = "none"

    def step(self):
        # 1. Update SIR timer if currently infected
        if self.sir_state == 1:
            self.time_infected += 1
            if self.time_infected >= self.model.config.sir.recovery_duration_quarters:
                self.sir_state = 2
                
        # 2. Make adoption decision if susceptible
        if not self.is_adopter:
            # Mathematical probability calculation
            
            # Feature vector for logreg
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
            
            # Economic adjustment (Affordability constraint)
            current_subsidy = self.model.current_subsidy
            current_price = self.model.current_panel_price
            affordability = min(current_subsidy / max(current_price, 1.0), 1.0)
            
            # Combined mathematical score
            score = 0.4 * p_base + 0.4 * sir_score + 0.2 * affordability
            self.adoption_probability = score
            
            decision = False
            
            # Configuration thresholds
            lower_thresh = self.model.config.cognitive.lower_threshold
            upper_thresh = self.model.config.cognitive.upper_threshold
            
            # Hybrid Cognitive Routing:
            if score >= upper_thresh:
                # Clearly decided: Accept
                decision = True
                self.decision_path = "rule"
                self.model.step_rule_decisions += 1
            elif score <= lower_thresh:
                # Clearly decided: Reject
                decision = False
                self.decision_path = "rule"
                self.model.step_rule_decisions += 1
            else:
                # Ambiguous: Call LLM Interface
                context = {
                    "agent_id": self.unique_id,
                    "timestep": self.model.timestep,
                    "income": self.income,
                    "home_owner": self.home_owner,
                    "sir_score": sir_score,
                    "affordability": affordability,
                    "combined_score": score,
                    "panel_price": current_price,
                    "subsidy": current_subsidy,
                    "adopting_neighbors": infected_neighbors,
                    "total_neighbors": len(neighbors),
                    "prompt_version": self.model.config.llm.prompt_version,
                    "model_identifier": self.model.config.llm.model
                }
                
                try:
                    decision = self.model.llm_interface.decide(context)
                    self.decision_path = "llm"
                    self.model.step_llm_decisions += 1
                except Exception as e:
                    # Fallback logic is handled by interface
                    pass
            
            # Final Decision
            if decision:
                self.is_adopter = True
                self.sir_state = 1
                self.time_infected = 0
                self.model.new_adoptions += 1
