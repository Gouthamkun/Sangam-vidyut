import mesa

class EnvironmentAgent(mesa.Agent):
    """
    Deterministic EnvironmentAgent for Phase 3A.
    Calculates estimated CO2 emissions reduction.
    """
    def __init__(self, model):
        super().__init__(model)
        self.co2_reduction = 0.0

    def step(self):
        kw_per_panel = self.model.config.environment.kw_per_panel
        co2_per_kw = self.model.config.environment.co2_per_kw
        total_adopters = self.model.total_adopters
        
        self.co2_reduction = total_adopters * kw_per_panel * co2_per_kw
