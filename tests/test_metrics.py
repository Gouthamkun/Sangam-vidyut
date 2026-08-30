import pytest
import pandas as pd
from src.analysis.metrics import detect_tipping_point

def test_detect_tipping_point():
    # Construct a synthetic adoption curve where tipping point is at index 3
    # Population = 1000
    # Threshold = 5% = 50 new adoptions in one step
    population = 1000
    
    adoption_data = [
        10,  # step 0: diff N/A
        20,  # step 1: diff 10
        40,  # step 2: diff 20
        100, # step 3: diff 60 > 50 (TIPPING POINT)
        120, # step 4: diff 20
    ]
    
    curve = pd.Series(adoption_data)
    
    tp = detect_tipping_point(curve, population=population, threshold_percent=0.05)
    assert tp == 3
    
def test_no_tipping_point():
    population = 1000
    adoption_data = [10, 20, 30, 40, 50] # max diff is 10
    curve = pd.Series(adoption_data)
    tp = detect_tipping_point(curve, population=population, threshold_percent=0.05)
    assert tp is None

def test_empty_trajectory():
    population = 1000
    curve = pd.Series([])
    tp = detect_tipping_point(curve, population=population, threshold_percent=0.05)
    assert tp is None

def test_single_step_trajectory():
    population = 1000
    curve = pd.Series([10])
    tp = detect_tipping_point(curve, population=population, threshold_percent=0.05)
    assert tp is None
