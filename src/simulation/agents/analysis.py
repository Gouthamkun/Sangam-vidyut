import mesa
import pandas as pd
from src.analysis.metrics import detect_tipping_point

class AnalysisAgent(mesa.Agent):
    """
    Deterministic AnalysisAgent for Phase 3A.
    Observes trajectory and calculates tipping points using the metrics library.
    """
    def __init__(self, model):
        super().__init__(model)
        self.adoption_history = []
        self.tipping_point = None

    def step(self):
        self.adoption_history.append(self.model.total_adopters)
        
        if self.tipping_point is None:
            curve = pd.Series(self.adoption_history)
            tp = detect_tipping_point(curve, self.model.config.simulation.n_agents, threshold_percent=0.05)
            if tp is not None:
                self.tipping_point = tp
