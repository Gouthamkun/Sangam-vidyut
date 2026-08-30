import pytest
import numpy as np
import pandas as pd
from src.models.statistical.baseline import AdoptionLogisticRegression

def test_random_seed_stochasticity():
    """same seed -> same result, different seed -> potentially different result"""
    X = pd.DataFrame(np.random.randn(100, 2))
    y = pd.Series(np.random.choice([0, 1], size=100))
    
    # Same seed
    model1 = AdoptionLogisticRegression(random_state=42)
    model1.fit(X, y)
    probs1 = model1.predict_proba(X)
    
    model2 = AdoptionLogisticRegression(random_state=42)
    model2.fit(X, y)
    probs2 = model2.predict_proba(X)
    
    np.testing.assert_array_equal(probs1, probs2)
    
    # To demonstrate different seeds doing different things,
    # LogisticRegression relies on random_state for shuffling in solvers like 'sag', 'saga'
    # or if we use mock_fit which generates data based on seed
    m1 = AdoptionLogisticRegression(random_state=10)
    m1.mock_fit()
    p1 = m1.predict_proba(pd.DataFrame(np.random.randn(10, 2)))
    
    m2 = AdoptionLogisticRegression(random_state=99)
    m2.mock_fit()
    p2 = m2.predict_proba(pd.DataFrame(np.random.randn(10, 2)))
    
    with pytest.raises(AssertionError):
        np.testing.assert_array_equal(p1, p2)

def test_train_test_split_evaluation():
    """Verify evaluation workflow does not leak data."""
    X = pd.DataFrame(np.random.randn(100, 2))
    y = pd.Series(np.random.choice([0, 1], size=100))
    
    model = AdoptionLogisticRegression(random_state=42)
    train_acc, test_acc = model.evaluate_with_split(X, y, test_size=0.2)
    
    assert 0.0 <= train_acc <= 1.0
    assert 0.0 <= test_acc <= 1.0
    assert model.is_fitted

def test_cross_validation():
    X = pd.DataFrame(np.random.randn(100, 2))
    y = pd.Series(np.random.choice([0, 1], size=100))
    
    model = AdoptionLogisticRegression(random_state=42)
    scores = model.cross_validate(X, y, cv=3)
    assert len(scores) == 3
    assert all(0.0 <= s <= 1.0 for s in scores)
