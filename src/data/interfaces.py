from abc import ABC, abstractmethod
import pandas as pd
from typing import Any

class DataInterface(ABC):
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        pass

class DemographicDataInterface(DataInterface):
    """Interface for Census/NSSO household data."""
    def load_data(self) -> pd.DataFrame:
        raise NotImplementedError("Empirical demographic data interface not yet implemented.")

class HistoricalAdoptionDataInterface(DataInterface):
    """Interface for MNRE state-wise solar adoption records."""
    def load_data(self) -> pd.DataFrame:
        raise NotImplementedError("Empirical historical adoption data interface not yet implemented.")

class PanelPricingDataInterface(DataInterface):
    """Interface for IRENA panel pricing data."""
    def load_data(self) -> pd.DataFrame:
        raise NotImplementedError("Empirical panel pricing data interface not yet implemented.")

class PolicyDataInterface(DataInterface):
    """Interface for Government Subsidy data."""
    def load_data(self) -> pd.DataFrame:
        raise NotImplementedError("Empirical policy data interface not yet implemented.")

class SocialNetworkDataInterface(DataInterface):
    """Interface for empirical household social network graphs."""
    def load_data(self) -> Any:
        raise NotImplementedError("Empirical social network data interface not yet implemented.")

# Placeholder for synthetic data generator
def generate_synthetic_demographics(n_agents: int) -> pd.DataFrame:
    """Generate synthetic household features for testing/dev ONLY."""
    import numpy as np
    incomes = np.random.lognormal(mean=10, sigma=1, size=n_agents)
    home_ownership = np.random.choice([0, 1], size=n_agents, p=[0.3, 0.7])
    return pd.DataFrame({
        "income": incomes,
        "home_owner": home_ownership
    })
