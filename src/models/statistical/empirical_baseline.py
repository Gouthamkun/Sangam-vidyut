import numpy as np
import pandas as pd
from typing import Dict, List, Any
import json
import os
from schemas.data.calibration import SerializedModelArtifact

class EmpiricalEcologicalBaseline:
    """
    Empirical Ecological Baseline Calibration Model.
    This model predicts household adoption propensity (p_base) based on 
    HCES demographic variables. It is fitted such that the survey-weighted 
    aggregation of these household probabilities matches state-level PM Surya Ghar 
    penetration rates.
    """
    def __init__(self):
        self.is_fitted = False
        self.coefficients: Dict[str, float] = {}
        self.intercept: float = 0.0
        self.feature_order: List[str] = []
        
    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deterministic preprocessing based on learned parameters."""
        X = df.copy()
        if 'derived_mpce' in X.columns:
            # Safe log transform
            X['log_mpce'] = np.log1p(X['derived_mpce'].clip(lower=1.0))
            X = X.drop(columns=['derived_mpce'])
            
        # One-hot encode categoricals, aligning to self.feature_order if fitted
        categorical_cols = ['sector', 'dwelling_type', 'electricity_access', 'free_electricity']
        X = pd.get_dummies(X, columns=[c for c in categorical_cols if c in X.columns], drop_first=True)
        
        # Ensure numeric
        for col in X.columns:
            if X[col].dtype == 'bool':
                X[col] = X[col].astype(float)
                
        # If fitted, align columns
        if self.is_fitted:
            missing = [c for c in self.feature_order if c not in X.columns]
            for m in missing:
                X[m] = 0.0
            return X[self.feature_order]
        else:
            return X
            
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probability of adoption using the logistic function:
        p_i = 1 / (1 + exp(-(X_i * beta + intercept)))
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
            
        X_proc = self._preprocess(X)
        beta = np.array([self.coefficients[f] for f in self.feature_order])
        linear_term = np.dot(X_proc.values, beta) + self.intercept
        return 1.0 / (1.0 + np.exp(-linear_term))
        
    def save(self, path: str, artifact: SerializedModelArtifact):
        """Serialize the fitted model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(artifact.model_dump_json(indent=2))
            
    def load(self, path: str):
        """Load a serialized model from disk."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.coefficients = data['coefficients']
        self.intercept = data['intercept']
        self.feature_order = data['feature_order']
        self.is_fitted = True
