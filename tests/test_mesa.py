import pytest
import pandas as pd
from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.consumer import ConsumerAgent

@pytest.fixture
def base_config():
    return ExperimentConfig()

def test_model_initialization(base_config):
    model = SangamVidyutModel(base_config)
    assert model.config.simulation.n_agents == 500
    assert len(model.agents) == 504 # 500 consumers + 4 singleton agents
    assert len(model.G.nodes()) == 500

def test_sir_conservation(base_config):
    model = SangamVidyutModel(base_config)
    n = base_config.simulation.n_agents
    
    for _ in range(5):
        model.step()
        
        s_count = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 0)
        i_count = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 1)
        r_count = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 2)
        
        assert s_count + i_count + r_count == n

def test_government_budget(base_config):
    model = SangamVidyutModel(base_config)
    model.step()
    assert model.government.budget <= base_config.government.initial_budget

def test_reproducibility(base_config):
    model1 = SangamVidyutModel(base_config)
    for _ in range(3):
        model1.step()
    df1 = model1.datacollector.get_model_vars_dataframe()

    model2 = SangamVidyutModel(base_config)
    for _ in range(3):
        model2.step()
    df2 = model2.datacollector.get_model_vars_dataframe()
    
    pd_testing = pytest.importorskip("pandas.testing")
    pd_testing.assert_frame_equal(df1, df2)

def test_different_seeds(base_config):
    config1 = ExperimentConfig()
    config1.simulation.seed = 42
    
    config2 = ExperimentConfig()
    config2.simulation.seed = 99
    
    model1 = SangamVidyutModel(config1)
    model2 = SangamVidyutModel(config2)
    
    consumers1 = [a for a in model1.agents if isinstance(a, ConsumerAgent)]
    consumers2 = [a for a in model2.agents if isinstance(a, ConsumerAgent)]
    
    # Assert deterministic generation of agent attributes is different due to seed
    assert consumers1[0].income != consumers2[0].income
    
    # Assert initial infected set is different
    infected_1 = [a for a in consumers1 if a.sir_state == 1]
    infected_2 = [a for a in consumers2 if a.sir_state == 1]
    
    assert set([a.unique_id for a in infected_1]) != set([a.unique_id for a in infected_2])
