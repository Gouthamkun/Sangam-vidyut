import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from typing import Tuple

class AdoptionLogisticRegression:
    """
    Logistic Regression baseline model for solar adoption probability.
    This model remains strictly independent from Mesa and LangGraph.
    """
    def __init__(self, random_state: int = None):
        self.random_state = random_state
        self.model = LogisticRegression(random_state=random_state)
        self.is_fitted = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the logistic regression model on historical data."""
        self.model.fit(X, y)
        self.is_fitted = True
        
    def evaluate_with_split(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Tuple[float, float]:
        """
        Evaluate the model using a strict train/test split to prevent data leakage.
        Returns accuracy on training set and test set.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        self.fit(X_train, y_train)
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        return train_acc, test_acc

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> np.ndarray:
        """
        Perform k-fold cross validation.
        """
        return cross_val_score(LogisticRegression(random_state=self.random_state), X, y, cv=cv)
        
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probability of adoption."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before predicting.")
        # Returns probability of class 1 (adoption)
        return self.model.predict_proba(X)[:, 1]

    def mock_fit(self, n_features: int = 2):
        """Mock fitting for testing purposes to avoid needing real datasets."""
        if self.random_state is not None:
            np.random.seed(self.random_state)
        # Create dummy data to fit the shape
        X = pd.DataFrame(np.random.randn(100, n_features))
        y = pd.Series(np.random.choice([0, 1], size=100))
        self.fit(X, y)
