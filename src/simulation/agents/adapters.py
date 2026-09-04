import pandas as pd
from typing import Dict, Any
from src.simulation.agents.consumer import ConsumerAgent

def create_consumer_from_household_record(model: Any, record: pd.Series) -> ConsumerAgent:
    """
    Adapter/Factory to translate an HCES synthetic household record 
    into a ConsumerAgent state without mutating the underlying ABM logic.
    """
    
    # 1. Handle Missing/Unavailable Dependencies for existing ConsumerAgent
    # The current ConsumerAgent mathematically requires `income` and `home_owner`.
    # - `derived_mpce` acts as the proxy for `income`.
    # - `home_owner` is UNAVAILABLE in HCES. We map it to -1 to satisfy the 
    #   constructor signature without hallucinating true/false ownership.
    income = record['derived_mpce']
    home_owner = -1
    
    # 2. Instantiate Base Agent
    agent = ConsumerAgent(model=model, income=income, home_owner=home_owner)
    
    # 3. Inject HCES Empirical Profile as metadata/state extensions
    # Core Geography
    agent.state = record['state']
    agent.district = record['district']
    agent.sector = record['sector']
    
    # Demographics & Housing
    agent.household_size = record['household_size']
    agent.dwelling_type = record['dwelling_type']
    
    # Energy
    agent.electricity_access = record['electricity_access']
    agent.free_electricity = record['free_electricity']
    
    # Economics (Pre-computed inherited decile)
    agent.monthly_consumption_expenditure = record['monthly_consumption_expenditure']
    agent.derived_mpce = record['derived_mpce']
    agent.mpce_decile = record['mpce_decile']
    
    # Provenance
    agent.synthetic_agent_id = record['synthetic_agent_id']
    agent.source_hces_household_key = record['source_hces_household_key']
    agent.survey_weight = record['survey_weight']
    
    # Explicitly withheld properties (architectural boundary)
    # agent.system_size_kw = None
    # agent.social_network = None
    
    return agent
