import pandas as pd
from typing import Dict, List, Optional

def calculate_adoption_curve(states_over_time: List[Dict[str, int]]) -> pd.DataFrame:
    """
    Given a list of SIR counts over time, return a DataFrame with the adoption curve.
    Adoption = Infected + Recovered
    """
    df = pd.DataFrame(states_over_time)
    if not df.empty:
        df['Total_Adopters'] = df.get('I', 0) + df.get('R', 0)
        df['Timestep'] = df.index
    return df

def calculate_mse(baseline_curve: pd.Series, simulation_curve: pd.Series) -> float:
    """
    Calculate Mean Squared Error between two adoption curves.
    """
    return ((baseline_curve - simulation_curve) ** 2).mean()

def detect_tipping_point(adoption_curve: pd.Series, population: int, threshold_percent: float = 0.05) -> Optional[int]:
    """
    Detect the timestep where an algorithmically defined rapid change in adoption occurs.
    
    Operational Definition:
    A 'tipping point' in this specific software context is detected when the discrete 
    derivative (new adoptions per step) exceeds a specific threshold percentage of the 
    total population in a single timestep. This distinguishes 'rapid algorithmic change' 
    from a 'scientifically proven societal tipping point', which requires broader sociological validation.
    
    Returns the timestep (index) where this first occurs, or None if no such step exists.
    """
    if adoption_curve.empty or len(adoption_curve) < 2:
        return None
        
    # Calculate new adoptions per timestep (discrete derivative)
    new_adoptions = adoption_curve.diff().fillna(0)
    
    threshold = population * threshold_percent
    
    # Find timesteps where new adoptions exceed threshold
    tipping_points = new_adoptions[new_adoptions > threshold]
    
    if not tipping_points.empty:
        return int(tipping_points.index[0])
    
    return None
