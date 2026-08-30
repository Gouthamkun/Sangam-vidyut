import mesa

class GovernmentAgent(mesa.Agent):
    """
    Deterministic GovernmentAgent for Phase 3A.
    Adjusts subsidy based on adoption targets and remaining budget.
    """
    def __init__(self, model):
        super().__init__(model)
        self.budget = model.config.government.initial_budget
        self.subsidy = model.config.government.base_subsidy

    def step(self):
        # Deduct budget for adoptions from the LAST step
        spent = self.model.new_adoptions_last_step * self.subsidy
        self.budget = max(0.0, self.budget - spent)
        
        if self.budget <= 0:
            self.subsidy = 0.0
        else:
            # Policy adjustment:
            current_rate = self.model.total_adopters / self.model.config.simulation.n_agents
            target_rate = self.model.config.government.target_adoption_rate
            
            if current_rate < target_rate:
                # Need more adoption, increase subsidy slightly if affordable
                proposed_subsidy = self.subsidy * 1.05
                self.subsidy = min(proposed_subsidy, self.budget / max(1, self.model.new_adoptions_last_step))
            else:
                # Exceeding target, reduce subsidy
                self.subsidy *= 0.95
