import pytest
from pydantic import ValidationError
from src.config.schema import ExperimentConfig, CognitiveConfig

def test_cognitive_config_validation():
    # Valid config
    config = CognitiveConfig(lower_threshold=0.3, upper_threshold=0.7)
    assert config.lower_threshold == 0.3
    
    # Zero width is allowed
    config_zero = CognitiveConfig(lower_threshold=0.5, upper_threshold=0.5)
    assert config_zero.lower_threshold == 0.5
    
    # Invalid config (lower > upper)
    with pytest.raises(ValidationError):
        CognitiveConfig(lower_threshold=0.8, upper_threshold=0.7)

    # Invalid config (out of bounds)
    with pytest.raises(ValidationError):
        CognitiveConfig(lower_threshold=-0.1, upper_threshold=0.7)
        
    with pytest.raises(ValidationError):
        CognitiveConfig(lower_threshold=0.3, upper_threshold=1.5)
