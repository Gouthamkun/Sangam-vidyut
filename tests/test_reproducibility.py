import pytest
from src.config.schema import ExperimentConfig
from src.simulation.adoption_sim import BasicMathematicalSimulation
from src.utils import set_seed

def test_reproducibility():
    """
    Running the same experiment twice with identical configuration
    and seed must produce identical deterministic outputs.
    """
    config = ExperimentConfig()
    
    # Run 1
    set_seed(config.simulation.seed)
    sim1 = BasicMathematicalSimulation(config, seed=config.simulation.seed)
    sim1.seed_initial_adopters(5)
    df1 = sim1.run()
    
    # Run 2
    set_seed(config.simulation.seed)
    sim2 = BasicMathematicalSimulation(config, seed=config.simulation.seed)
    sim2.seed_initial_adopters(5)
    df2 = sim2.run()
    
    # Assert identical trajectories
    pd_testing = pytest.importorskip("pandas.testing")
    pd_testing.assert_frame_equal(df1, df2)

def test_different_seeds_produce_different_outputs():
    config = ExperimentConfig()
    
    set_seed(10)
    sim1 = BasicMathematicalSimulation(config, seed=10)
    sim1.seed_initial_adopters(5)
    df1 = sim1.run()
    
    set_seed(20)
    sim2 = BasicMathematicalSimulation(config, seed=20)
    sim2.seed_initial_adopters(5)
    df2 = sim2.run()
    
    # They should not be perfectly equal
    with pytest.raises(AssertionError):
        pd_testing = pytest.importorskip("pandas.testing")
        pd_testing.assert_frame_equal(df1, df2)
