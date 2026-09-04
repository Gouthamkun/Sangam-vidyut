import os
import pandas as pd
import numpy as np
from src.models.statistical.empirical_baseline import EmpiricalEcologicalBaseline

class EmpiricalBaselineProvider:
    """
    Deterministic provider that loads the frozen empirical calibration artifact
    and computes the household-level p_base probability.
    """
    def __init__(self, artifact_path: str = 'outputs/calibration/selected_model/empirical_baseline.json'):
        self.artifact_path = artifact_path
        self.model = EmpiricalEcologicalBaseline()
        
        if not os.path.exists(self.artifact_path):
            raise FileNotFoundError(f"Empirical calibration artifact not found: {self.artifact_path}")
            
        self.model.load(self.artifact_path)
        
        if not self.model.is_fitted:
            raise ValueError("Calibration artifact is malformed or not fitted.")

    def predict(self, agent) -> float:
        """
        Calculate household-level p_base.
        Translates agent properties to the calibrated feature representation.
        """
        # 1. Feature Mapping
        # Map fields precisely as calibrated
        features = {
            'derived_mpce': agent.derived_mpce,
            'household_size': agent.household_size,
            'sector': agent.sector,
            'dwelling_type': agent.dwelling_type,
            'electricity_access': agent.electricity_access,
            'free_electricity': agent.free_electricity
        }
        
        df = pd.DataFrame([features])
        
        # 2. Preprocessing (exact identical transformation used in fitting)
        X_proc = self.model._preprocess(df)
        
        # 3. Align with feature ordering
        # Ensure all columns exist; fill missing dummies with 0
        for col in self.model.feature_order:
            if col not in X_proc.columns:
                X_proc[col] = 0.0
                
        # Reorder strictly
        X_final = X_proc[self.model.feature_order]
        
        # 4. Dot product with coefficients
        logits = 0.0
        if self.model.intercept is not None:
            logits += self.model.intercept
            
        for col, coef in self.model.coefficients.items():
            if col in X_final.columns:
                logits += X_final[col].iloc[0] * coef
                
        # 5. Sigmoid (bounded probability)
        p_base = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
        
        return float(p_base)
