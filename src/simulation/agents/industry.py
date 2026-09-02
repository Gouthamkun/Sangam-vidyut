import mesa

class IndustryAgent(mesa.Agent):
    """
    Deterministic IndustryAgent for Phase 3A.
    Adjusts panel price based on demand without LSTM integration yet.
    """
    def __init__(self, model):
        super().__init__(model)
        self.panel_price = model.config.industry.base_price

    def step(self):
        if not self.model.config.industry.dynamic_pricing:
            return
            
        # Demand threshold (e.g. > 1% of population in a quarter)
        threshold = self.model.config.simulation.n_agents * 0.01
        rate = self.model.config.industry.price_adjustment_rate
        
        if self.model.new_adoptions_last_step > threshold:
            # High demand drives prices up
            self.panel_price *= (1.0 + rate)
        else:
            # Low demand drops prices to encourage adoption
            self.panel_price *= (1.0 - rate)
